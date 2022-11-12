import enum
import typer
import sys
import dataclasses
import typing as t
import subprocess
import datetime

from .. import error as e
from .. import logger
from .__base__ import Runner, Job, JobRunnerClusterType


_LOGGER = logger.get_logger()
# noinspection PyTypeChecker
_RUNNER: Runner = None
# noinspection PyTypeChecker
_CLUSTER_TYPE: JobRunnerClusterType = None
_APP = typer.Typer(name="Toolcraft Job Runner")
_now = datetime.datetime.now


def get_app(runner: Runner, cluster_type: JobRunnerClusterType):
    """
    Note we use _RUNNER module var to get access to Runner instance.
    This method is hence required.
    """
    global _RUNNER, _CLUSTER_TYPE, _APP
    if _RUNNER is None:
        _RUNNER = runner
    else:
        e.code.CodingError(
            msgs=["Was expecting internal var _RUNNER to be None"]
        )
    if _CLUSTER_TYPE is None:
        _CLUSTER_TYPE = cluster_type
    else:
        e.code.CodingError(
            msgs=["Was expecting internal var _CLUSTER_TYPE to be None"]
        )
    return _APP


@_APP.command()
def launch():
    """
    Launches all the jobs in runner.
    """

    # --------------------------------------------------------- 01
    # get some vars
    _rp = _RUNNER.richy_panel
    _rp.update(f"launching jobs on {_CLUSTER_TYPE.name!r} cluster ...")
    _flow = _RUNNER.flow

    # --------------------------------------------------------- 02
    # call jobs ...
    # todo: we might want this to be called from client machine and submit jobs via
    #   ssh ... rather than using instance on cluster to launch jobs
    #   This will also help to have gui in dearpygui
    # --------------------------------------------------------- 02.01
    # for local
    if _CLUSTER_TYPE is JobRunnerClusterType.local:

        # ----------------------------------------------------- 02.01.01
        # tracker containers
        _completed_jobs = []

        # ----------------------------------------------------- 02.01.02
        # loop over stages
        for _stage_key, _stage in _flow.stages.items():
            _rp.update(f"launching jobs for stage: {_stage_key}...")

            # ------------------------------------------------- 02.01.03
            # loop over jobs in current _stage
            _jobs = _stage.all_jobs
            for _job in _rp.track(
                sequence=_jobs, task_name=f"stage {_stage_key}"
            ):
                # --------------------------------------------- 02.01.03.01
                # get wait on jobs that are needed to be completed before executing _job
                _wait_jobs = []
                for _wo in _job._wait_on:
                    if isinstance(_wo, Job):
                        _wait_jobs += [_wo]
                    else:
                        _wait_jobs += _wo.bottom_jobs

                # --------------------------------------------- 02.01.03.02
                # check if all wait on jobs are completed
                for _wj in _wait_jobs:
                    if _wj not in _completed_jobs:
                        raise e.code.CodingError(
                            msgs=[
                                "When not on server we expect that property `all_jobs` "
                                "should resolve in such a way that all `wait_on` jobs "
                                "must be already done ..",
                                f"Check {_wj.flow_id} which should be completed by now ..."
                            ]
                        )

                # --------------------------------------------- 02.01.03.03
                # make cli command
                _cli_command = ["start", "/wait", "cmd", "/c", ] + _job.cli_command

                # --------------------------------------------- 02.01.03.04
                # run job
                _run_job(_job, _cli_command)

                # --------------------------------------------- 02.01.03.05
                # append to list as job is completed
                _completed_jobs.append(_job)

    # --------------------------------------------------------- 02.02
    # for ibm_lsf
    elif _CLUSTER_TYPE is JobRunnerClusterType.ibm_lsf:
        # ----------------------------------------------------- 02.02.01
        # loop over stages
        for _stage_key, _stage in _flow.stages.items():
            _rp.update(f"launching jobs for stage: {_stage_key}...")

            # ------------------------------------------------- 02.02.02
            # loop over jobs in current _stage
            _jobs = _stage.all_jobs
            for _job in _rp.track(
                sequence=_jobs, task_name=f"stage {_stage_key}"
            ):
                # --------------------------------------------- 02.02.02.01
                # make cli command
                # todo: when self.path is not local we need to see how to log files ...
                #   should we stream or dump locally ?? ... or maybe figure out
                #   dapr telemetry
                _log = _job.path / "bsub.log"
                _nxdi_prefix = ["bsub", "-oo", _log.local_path.as_posix(), "-J", _job.job_id]
                _wait_on_jobs = _job.wait_on_jobs
                if bool(_wait_on_jobs):
                    _wait_on = \
                        " && ".join([f"done({_.job_id})" for _ in _wait_on_jobs])
                    _nxdi_prefix += ["-w", f"{_wait_on}"]
                _cli_command = _nxdi_prefix + _job.cli_command

                # --------------------------------------------- 02.02.02.02
                # run job
                _run_job(_job, _cli_command)

    # --------------------------------------------------------- 02.03
    else:
        raise e.code.NotSupported(
            msgs=[f"Not supported {_CLUSTER_TYPE}"]
        )

    # todo: add richy tracking panel ...that makes a layout for all stages and
    #  shows status of all jobs submitted above
    #  The status info will be based on tracking provided by
    #  + if toolcraft maybe use predefined tags to show status ... but his might
    #    cause some io overhead ... instead have toolcraft.Job to update
    #    richy client
    #  + Also see if you can use
    #    - bsub
    #    - qsub
    #    - dapr telemetry
    #  IMP: see docstring we can even have dearpygui client if we can submit jobs
    #    and track jobs via ssh


def _run_job(_job: Job, _cli_command: t.List[str]):
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
    subprocess.run(_cli_command, shell=True)

    # ------------------------------------------------------------- 04
    # log
    _LOGGER.info(
        msg=f"Launched job from main machine with below command...", msgs=[_cli_command],
    )


@_APP.command()
def run(
    method: str = typer.Argument(..., help="Method to execute in runner.", show_default=False, ),
    experiment: t.Optional[str] = typer.Argument(None, help="Experiment which will be used by method in runner."),
):
    """
    Run a job in runner.
    """

    # ------------------------------------------------------------ 01
    # get respective job
    try:
        _method = getattr(_RUNNER, method)
    except AttributeError as _ae:
        raise e.code.NotAllowed(
            msgs=[f"The method with name {method} is not available in runner class {_RUNNER.__class__}"]
        )
    if experiment is None:
        _experiment = None
        _job = _RUNNER.associated_jobs[_method]
    else:
        _experiment = _RUNNER.monitor.get_experiment_from_hex_hash(hex_hash=experiment)
        _job = _experiment.associated_jobs[_method]

    # ------------------------------------------------------------ 02
    # set job in runner
    _RUNNER.internal.job = _job

    # ------------------------------------------------------------ 03
    # get some vars
    _rp = _RUNNER.richy_panel

    # ------------------------------------------------------------ 04
    # reconfig logger to change log file for job
    import logging
    _log = _job.log_file
    logger.setup_logging(
        propagate=False,
        level=logging.NOTSET,
        # todo: here we can config that on server where things will be logged
        handlers=[
            # logger.get_rich_handler(),
            # logger.get_stream_handler(),
            logger.get_file_handler(_log.local_path),
        ],
    )
    _start = _now()
    _LOGGER.info(
        msg=f"Starting job on worker machine ...",
        msgs=[
            {
                "name": _job.name,
                "sys.argv": sys.argv,
                "started": _start.ctime(),
            }
        ]
    )

    # ------------------------------------------------------------ 05
    # check if launcher client machine has created launched tag
    if not _job.tag_manager.launched.exists():
        raise e.code.CodingError(
            msgs=[
                "We expect that `launched` tag is created by client launching machine .... "
            ]
        )

    # ------------------------------------------------------------ 06
    # indicates that job is started
    _job.tag_manager.started.create()

    # ------------------------------------------------------------ 07
    # indicate that job will now be running
    # also note this acts as semaphore and is deleted when job is finished
    # ... hence started tag is important
    _job.tag_manager.running.create()

    # ------------------------------------------------------------ 08
    _failed = False
    try:
        for _wj in _job.wait_on_jobs:
            if not _wj.is_finished:
                raise e.code.CodingError(
                    msgs=[f"Wait-on job with flow-id {_wj.flow_id} and job-id "
                          f"{_wj.job_id} is supposed to be finished ..."]
                )
        _rp.log(
            [
                f"flow_id: {_job.flow_id}",
                f"job_id : {_job.job_id}",
                f"name   : {_job.name}",
            ]
        )
        if _experiment is None:
            _job.method()
        else:
            _job.method(experiment=_experiment)
        _job.tag_manager.running.delete()
        _job.tag_manager.finished.create()
        _end = _now()
        _LOGGER.info(
            msg=f"Successfully finished job on worker machine ...",
            msgs=[
                {
                    "flow_id": _job.flow_id,
                    "job_id": _job.job_id,
                    "name": _job.name,
                    "started": _start.ctime(),
                    "ended": _end.ctime(),
                    "seconds": str((_end - _start).total_seconds()),
                }
            ]
        )
    except Exception as _ex:
        _failed = True
        _job.tag_manager.failed.create(
            data={
                "exception": str(_ex)
            }
        )
        _end = _now()
        _LOGGER.info(
            msg=f"Failed job on worker machine ...",
            msgs=[
                {
                    "flow_id": _job.flow_id,
                    "job_id": _job.job_id,
                    "name": _job.name,
                    "started": _start.ctime(),
                    "ended": _end.ctime(),
                    "seconds": str((_end - _start).total_seconds()),
                    "exception": str(_ex),
                }
            ]
        )
        _job.tag_manager.running.delete()
        # above thing will tell toolcraft that things failed gracefully
        # while below raise will tell cluster systems like bsub that job has failed
        # todo for `JobRunnerClusterType.local_on_same_thread` this will not allow
        #  future jobs to run ... but this is expected as we want to debug in
        #  this mode mostly
        raise _ex


@_APP.command()
def view():
    """
    Views all the jobs in runner.
    """

    # ---------------------------------------------------------------- 01
    # That is do not call view when not on main machine
    # todo: check if on server
    if not sys.platform == 'win32':
        raise e.code.NotAllowed(
            msgs=["looks like you are on linux system i.e. dearpygui might nor work ..."]
        )

    # ---------------------------------------------------------------- 02
    # define dashboard
    from .. import gui

    @dataclasses.dataclass
    class ShowFlowStatusCallback(gui.callback.Callback):

        def fn(_self, sender: gui.widget.Widget):
            _window = gui.window.Window(
                label="Job Flow Status", width=600, height=700, pos=(250, 250),
            )
            with _window:
                _RUNNER.flow.status_text()
            _dashboard.add_window(window=_window)

    @dataclasses.dataclass
    class RunnerDashboard(gui.dashboard.BasicDashboard):
        theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()
        title_text: gui.widget.Text = gui.widget.Text(default_value=f"Flow for {_RUNNER.py_script}")
        job_status: gui.widget.Button = gui.widget.Button(
            label=">>> Show Job Flow Status <<<", callback=ShowFlowStatusCallback(),
        )
        hr1: gui.widget.Separator = gui.widget.Separator()
        hr2: gui.widget.Separator = gui.widget.Separator()
        runner_jobs_view: gui.form.ButtonBarForm = gui.form.ButtonBarForm(
            title="Runner Jobs ...",
            collapsing_header_open=True,
        )
        hr3: gui.widget.Separator = gui.widget.Separator()
        hr4: gui.widget.Separator = gui.widget.Separator()
        experiment_view: gui.form.DoubleSplitForm = gui.form.DoubleSplitForm(
            title="Experiments ...",
            callable_name="view",
            allow_refresh=False,
            collapsing_header_open=True,
        )

    # ---------------------------------------------------------------- 03
    # make dashboard
    _dashboard = RunnerDashboard(title="Runner Dashboard")
    _rp = _RUNNER.richy_panel

    # ---------------------------------------------------------------- 04
    # register jobs for runner
    def _j_view(_j: Job) -> gui.widget.Widget:
        return _j.view()

    for _method, _job in _rp.track(_RUNNER.associated_jobs.items(), task_name="Register views for Runner"):
        _dashboard.runner_jobs_view.register(
            key=_method.__name__, gui_name=_method.__name__,
            fn=_j_view,
            fn_kwargs={"_j": _job}
        )

    # ---------------------------------------------------------------- 05
    # add experiments
    for _experiment in _rp.track(_RUNNER.registered_experiments, task_name="Register views for Experiments"):
        _dashboard.experiment_view.add(
            hashable=_experiment,
            # todo: add group key for grouping
            group_key=None,
        )

    # ---------------------------------------------------------------- 06
    # log
    _rp.update("The view is now opened in external window. Close it to terminate.")

    # ---------------------------------------------------------------- 07
    # run
    gui.Engine.run(_dashboard)


@_APP.command()
def clean():
    """
    Cleans the job in runner that are not finished (use carefully).
    """
    _rp = _RUNNER.richy_panel
    for _stage_name, _stage in _rp.track(_RUNNER.flow.stages.items(), task_name="Scanning stages"):
        _rp.update(f"Scanning stage {_stage_name} ...")
        _j: Job
        for _j in _rp.track(_stage.all_jobs, task_name=f"Deleting for stage {_stage_name}"):
            if not _j.is_finished:
                _rp.update(f"Deleting job {_j.flow_id}")
                _j.path.delete(recursive=True)
