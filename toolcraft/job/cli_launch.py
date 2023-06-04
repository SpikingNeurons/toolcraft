"""
todo: add richy tracking panel ...that makes a layout for all stages and
 shows status of all jobs submitted above
 The status info will be based on tracking provided by
 + if toolcraft maybe use predefined tags to show status ... but his might
   cause some io overhead ... instead have toolcraft.Job to update
   richy client
 + Also see if you can use
   - bsub
   - qsub
   - dapr telemetry
 IMP: see docstring we can even have dearpygui client if we can submit jobs
   and track jobs via ssh
"""

import os
import time
import psutil
import typer
import typing as t
import subprocess

from .. import logger, settings
from .. import error as e
from .__base__ import Runner, Job
from . import PRETTY_EXCEPTIONS_ENABLE, PRETTY_EXCEPTIONS_SHOW_LOCALS


_LOGGER = logger.get_logger()


# noinspection PyTypeChecker
_RUNNER: Runner = None
_APP = typer.Typer(
    pretty_exceptions_show_locals=PRETTY_EXCEPTIONS_SHOW_LOCALS,
    pretty_exceptions_enable=PRETTY_EXCEPTIONS_ENABLE,
    help="Launch all the registered jobs in flow"
)


def _run_job(_job: Job, _cli_command: t.List[str], single_cpu: bool):
    # ------------------------------------------------------------- 01
    # check health
    _ret = _job.check_health(is_on_main_machine=True)
    if _ret is not None:
        _LOGGER.error(msg=_ret)
        return

    # ------------------------------------------------------------- 02
    # create tag so that worker machine knows that the client has
    # launched it
    _job.tag_manager.launched.create()

    # ------------------------------------------------------------- 03
    # run in subprocess
    if single_cpu:
        if _job.experiment is None:
            return _job.method()
        else:
            return  _job.method(experiment=_job.experiment)
    else:
        _ret = subprocess.run(_cli_command, shell=True, env=os.environ.copy())


@_APP.command(help="Launches all the jobs in runner on lsf infrastructure.")
def lsf(
    email: bool = typer.Option(default=False, help="Set this if you want to receive email after lsf job completion."),
    cpus: int = typer.Option(default=None, help="Number of processors to use for lsf job."),
    memory: int = typer.Option(default=None, help="Amount of memory to reserve for lsf job."),
):
    """

    todo: see if wsl can be used to submit job queue from windows to lsf https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/WSL.html

    Returns:

    """

    # --------------------------------------------------------- 01
    # get some vars
    _rp = _RUNNER.richy_panel
    _rp.update(f"launching jobs on LSF cluster ...")
    _flow = _RUNNER.flow

    # --------------------------------------------------------- 02
    # call jobs ...
    # todo: we might want this to be called from client machine and submit jobs via
    #   ssh ... rather than using instance on cluster to launch jobs
    #   This will also help to have gui in dearpygui
    # loop over stages
    for _stage_key, _stage in _flow.stages.items():
        _rp.update(f"launching jobs for stage: {_stage_key}...")

        # loop over jobs in current _stage
        _jobs = _stage.all_jobs
        for _job in _rp.track(
            sequence=_jobs, task_name=f"stage {_stage_key}"
        ):
            # ------------------------------------------------- 02.01
            if _job.is_finished:
                _rp.update(f"skipping {_stage_key}:{_job.job_id}")
                continue
            else:
                _rp.update(f"launching {_stage_key}:{_job.job_id}")

            # ------------------------------------------------- 02.02
            # make cli command
            # todo: when self.path is not local we need to see how to log files ...
            #   should we stream or dump locally ?? ... or maybe figure out
            #   dapr telemetry
            _log = _job.path / "bsub.log"
            _nxdi_prefix = ["bsub", ]
            _nxdi_prefix += ["-J", _job.job_id, ]
            # override if job specific launch_lsf_parameters are supplied
            if bool(_job.launch_lsf_parameters):
                email = _job.launch_lsf_parameters['email']
                cpus = _job.launch_lsf_parameters['cpus']
                memory = _job.launch_lsf_parameters['memory']
            if not email:
                _nxdi_prefix += ["-oo", _log.local_path.as_posix(), ]
            if cpus is not None:
                _nxdi_prefix += ["-n", f"{cpus}"]
            if memory is not None:
                _nxdi_prefix += ["-R", f'rusage[mem={memory}]']
            _wait_on_jobs = [_ for _ in _job.wait_on_jobs if not _.is_finished]
            if bool(_wait_on_jobs):
                _wait_on = \
                    " && ".join([f"done({_.job_id})" for _ in _wait_on_jobs])
                _nxdi_prefix += ["-w", f"{_wait_on}"]
            _cli_command = _nxdi_prefix + _job.cli_command
            print(" ".join(_cli_command))
            # _rp.log([" ".join(_cli_command)])

            # ------------------------------------------------- 02.03
            # run job
            _run_job(_job, _cli_command, shell=False)


@_APP.command(help="Launches all the jobs in runner on local machine.")
def local(
    single_cpu: bool = typer.Option(default=False, help="Launches on single CPU in sequence (good for debugging)")
):
    """
    todo: remote linux instances via wsl via ssh https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/WSL.html
      decide parameters by arguments to this method
    """

    # --------------------------------------------------------- 01
    # some validation
    if settings.PYC_DEBUGGING:
        if not single_cpu:
            raise e.validation.NotAllowed(
                msgs=[
                    "looks like you are in pycharm debug mode",
                    "Make sure to set --single-cpu to enable full debugging inside jobs ... "
                ]
            )
    # get some vars
    _rp = _RUNNER.richy_panel
    _rp.update(f"launching jobs on LOCAL cluster ...")
    if single_cpu:
        _rp.stop()
    _flow = _RUNNER.flow

    # --------------------------------------------------------- 02
    # some vars
    _MAX_JOBS = os.cpu_count()
    _MAX_MEMORY_USAGE_IN_PERCENT = 95.
    _WARM_UP_TIME_FOR_NEXT_JOB_IN_SECONDS = 1
    _jobs_running_in_parallel = {}

    # --------------------------------------------------------- 03
    # populate _all_jobs
    _all_jobs = {}
    for _stage in _flow.stages.values():
        for _job in _stage.all_jobs:
            _all_jobs[_job.job_id] = _job
    _job_track_task = _rp.add_task(total=len(_all_jobs), task_name="jobs")

    # --------------------------------------------------------- 04
    # loop infinitely until all jobs complete
    while bool(_all_jobs):

        # loop over _all_jobs
        for _job_flow_id in list(_all_jobs.keys()):

            # ------------------------------------------------- 04.01
            # get job
            _job = _all_jobs[_job_flow_id]

            # ------------------------------------------------- 04.02
            # if finished skip
            if _job.is_finished:
                _rp.log([f"✅ {_job_flow_id} :: skipping already finished"])
                del _all_jobs[_job_flow_id]
                _job_track_task.update(advance=1)
                continue

            # ------------------------------------------------- 04.03
            # if failed skip
            if _job.is_failed:
                _rp.log([f"❌ {_job_flow_id} :: skipping as it is failed"])
                del _all_jobs[_job_flow_id]
                _job_track_task.update(advance=1)
                continue

            # ------------------------------------------------- 04.04
            # look in all _wait_on jobs
            # if one or more failed in _wait_on jobs then skip
            _one_or_more_failed = False
            for _wait_job in _job.wait_on_jobs:
                if _wait_job.is_failed:
                    _one_or_more_failed = True
                    break
            if _one_or_more_failed:
                _rp.log([f"❌ {_job_flow_id} :: skipping as one or more wait_on job failed"])
                del _all_jobs[_job_flow_id]
                _job_track_task.update(advance=1)
                continue

            # ------------------------------------------------- 04.05
            # look in all _wait_on jobs
            # if any one job is still not finished then skip and do not log it to richy_panel
            _all_finished = True
            for _wait_job in _job.wait_on_jobs:
                if not _wait_job.is_finished:
                    _all_finished = False
                    break
            if not _all_finished:
                _rp.update(f"⏰ {_job.job_id} :: postponed wait_on jobs not completed")
                continue

            # ------------------------------------------------- 04.06
            # if any already launched job is finished then remove from dict _jobs_running_in_parallel
            for _k in list(_jobs_running_in_parallel.keys()):
                if _jobs_running_in_parallel[_k].is_finished:
                    _rp.update(f"✅ {_job.job_id} :: completed")
                    del _jobs_running_in_parallel[_k]
                    _job_track_task.update(advance=1)

            # ------------------------------------------------- 04.07
            # if we reach here that means all jobs are over and current job is eligible to execute
            # but before launching make sure that memory and cpus are available
            # ------------------------------------------------- 04.07.01
            # make cli command
            _cli_command = _job.cli_command
            if not single_cpu:
                if 'WSL2' in settings.PLATFORM.release:
                    _cli_command = ["gnome-terminal", "--", "bash", "-c", ] + ['"' + ' '.join(_cli_command) + '"']
                else:
                    _cli_command = ["start", "cmd", "/c", ] + _cli_command
            # ------------------------------------------------- 04.07.02
            # for first job no need to check anything just launch
            if len(_jobs_running_in_parallel) == 0:
                _run_job(_job, _cli_command, single_cpu=single_cpu)
                _jobs_running_in_parallel[_job.job_id] = _job
                _rp.log([f"🏁 {_job.job_id} :: launching"])
                del _all_jobs[_job_flow_id]
                _job_track_task.update(advance=1)
                continue
            # ------------------------------------------------- 04.07.03
            # else we need to do multiple things
            else:
                # if not enough cpus then skip
                if len(_jobs_running_in_parallel) >= _MAX_JOBS:
                    _rp.update(f"⏰ {_job.job_id} :: postponed not enough cpu's")
                    continue
                # if enough memory not available then skip
                if psutil.virtual_memory()[2] > _MAX_MEMORY_USAGE_IN_PERCENT:
                    _rp.update(f"⏰ {_job.job_id} :: postponed not enough memory")
                    continue
                # all is well launch
                _run_job(_job, _cli_command, single_cpu=single_cpu)
                _jobs_running_in_parallel[_job.job_id] = _job
                _rp.log([f"🏁 {_job.job_id} :: launching"])
                del _all_jobs[_job_flow_id]
                _job_track_task.update(advance=1)
            # ------------------------------------------------- 04.07.04
            # _WARM_UP_TIME_FOR_NEXT_JOB_IN_SECONDS
            # this allows the job to enter properly and get realistic ram usage
            time.sleep(_WARM_UP_TIME_FOR_NEXT_JOB_IN_SECONDS)

    # --------------------------------------------------------- 05
    if single_cpu:
        _rp.start()
