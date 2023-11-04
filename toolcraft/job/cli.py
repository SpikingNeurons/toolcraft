import enum
import os
import pathlib
import time

import psutil
import typer
from typing_extensions import Annotated
import sys
import dataclasses
import typing as t
import subprocess
import datetime
import traceback

from .. import error as e
from .. import logger
from .__base__ import Runner, Job
from . import PRETTY_EXCEPTIONS_ENABLE, PRETTY_EXCEPTIONS_SHOW_LOCALS
from . import cli_launch
_now = datetime.datetime.now


_LOGGER = logger.get_logger()

# noinspection PyTypeChecker
_RUNNER: Runner = None

_APP = typer.Typer(
    name="Toolcraft Job Runner",
    pretty_exceptions_show_locals=PRETTY_EXCEPTIONS_SHOW_LOCALS,
    pretty_exceptions_enable=PRETTY_EXCEPTIONS_ENABLE,
)
# noinspection PyProtectedMember
_APP.add_typer(cli_launch._APP, name="launch")


class LaunchClusterType(str, enum.Enum):
    # todo: explore windows task scheduler
    #    https://www.jcchouinard.com/python-automation-using-task-scheduler/
    #    Or make custom bsub job scheduler for windows in python
    local = "local"
    # todo: support ibm_lsf over ssh using https://www.fabfile.org
    lsf = "lsf"


def get_app(runner: Runner):
    """
    Note we use _RUNNER module var to get access to Runner instance.
    This method is hence required.
    """
    global _RUNNER, _APP
    if _RUNNER is None:
        _RUNNER = runner
        cli_launch._RUNNER = runner
    else:
        raise e.code.CodingError(
            msgs=["Was expecting internal var _RUNNER to be None"]
        )
    return _APP


@_APP.command(help="Test nxdi environment")
def nxdi():
    """
    """
    print("__is_on_nxdi__", (pathlib.Path.home() / "__is_on_nxdi__").exists())
    # noinspection PyUnresolvedReferences
    import tensorflow as tf
    print("CUDA", tf.test.is_built_with_cuda())
    print("Devices", tf.config.list_physical_devices())


@_APP.command(help="Run the job")
def run(
    job: Annotated[
        str,
        typer.Argument(
            help="Job ID in format <runner-hex-hash:method-name> or <runner-hex-hash:experi-hex-hash:method-name>",
            show_default=False,
        )
    ],
):
    """
    Run a job in runner.
    """

    # ------------------------------------------------------------ 01
    # get respective job
    # note that it also does validations
    _job = _RUNNER.get_job_from_cli_run_arg(job=job)

    # ------------------------------------------------------------ 02
    # get some vars
    _rp = _RUNNER.richy_panel

    # ------------------------------------------------------------ 03
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
                "job_id": _job.job_id,
                "sys.argv": sys.argv,
                "started": _start.ctime(),
            }
        ]
    )

    # ------------------------------------------------------------ 04
    # check if launcher client machine has created launched tag
    if not _job.tag_manager.launched.exists():
        raise e.code.CodingError(
            msgs=[
                "We expect that `launched` tag is created by client launching machine .... "
            ]
        )

    # ------------------------------------------------------------ 05
    # indicates that job is started
    _job.tag_manager.started.create()

    # ------------------------------------------------------------ 06
    # indicate that job will now be running
    # also note this acts as semaphore and is deleted when job is finished
    # ... hence started tag is important
    _job.tag_manager.running.create()

    # ------------------------------------------------------------ 07
    try:
        for _wj in _job.wait_on_jobs:
            if not _wj.is_finished:
                raise e.code.CodingError(
                    msgs=[f"Wait-on job with job-id "
                          f"{_wj.job_id} is supposed to be finished ..."]
                )
        if _job.experiment is None:
            _job.method()
        else:
            with _job.experiment(richy_panel=_rp):
                _job.method()
        _job.tag_manager.running.delete()
        _job.tag_manager.finished.create()
        _end = _now()
        _LOGGER.info(
            msg=f"Successfully finished job on worker machine ...",
            msgs=[
                {
                    "job_id": _job.job_id,
                    "started": _start.ctime(),
                    "ended": _end.ctime(),
                    "seconds": str((_end - _start).total_seconds()),
                }
            ]
        )
    except Exception as _ex:
        _ex_str = traceback.format_exc()
        _job.tag_manager.failed.create(exception=_ex_str)
        _end = _now()
        _LOGGER.error(
            msg=f"Failed job on worker machine ...",
            msgs=[
                {
                    "job_id": _job.job_id,
                    "started": _start.ctime(),
                    "ended": _end.ctime(),
                    "seconds": str((_end - _start).total_seconds()),
                }
            ]
        )
        _LOGGER.error(
            msg="*** EXCEPTION MESSAGE *** \n" + _ex_str
        )
        _job.tag_manager.running.delete()
        # above thing will tell toolcraft that things failed gracefully
        # while below raise will tell cluster systems like bsub that job has failed
        # todo for `JobRunnerClusterType.local_on_same_thread` this will not allow
        #  future jobs to run ... but this is expected as we want to debug in
        #  this mode mostly
        raise _ex


@_APP.command(help="View dashboard")
def view():
    """
    Views all the jobs in runner.
    """
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
        theme_selector: gui.widget.Combo = dataclasses.field(default_factory=gui.callback.SetThemeCallback.get_combo_widget)
        title_text: gui.widget.Text = dataclasses.field(default_factory=lambda: gui.widget.Text(default_value=f"Flow for {_RUNNER.py_script}"))
        job_status: gui.widget.Button = dataclasses.field(default_factory=lambda: gui.widget.Button(label=">>> Show Job Flow Status <<<", callback=ShowFlowStatusCallback(),))
        hr1: gui.widget.Separator = dataclasses.field(default_factory=gui.widget.Separator)
        hr2: gui.widget.Separator = dataclasses.field(default_factory=gui.widget.Separator)
        runner_jobs_view: gui.form.ButtonBarForm = dataclasses.field(
            default_factory=lambda: _RUNNER.view()
        )
        hr3: gui.widget.Separator = dataclasses.field(default_factory=gui.widget.Separator)
        hr4: gui.widget.Separator = dataclasses.field(default_factory=gui.widget.Separator)
        experiment_view: gui.form.DoubleSplitForm = dataclasses.field(
            default_factory=lambda: gui.form.DoubleSplitForm(
                label="Experiments ...",
                callable_name="view",
                default_open=True,
            )
        )

    # ---------------------------------------------------------------- 03
    # make dashboard
    _dashboard = RunnerDashboard(title="Runner Dashboard")
    _rp = _RUNNER.richy_panel

    # ---------------------------------------------------------------- 04
    # register jobs for runner
    def _j_view(_j: Job) -> gui.widget.Widget:
        return _j.view()

    # for _method, _job in _rp.track(_RUNNER.associated_jobs.items(), task_name="Register views for Runner"):
    #     _dashboard.runner_jobs_view.register(
    #         key=_method.__name__, gui_name=_method.__name__,
    #         fn=_j_view,
    #         fn_kwargs={"_j": _job}
    #     )

    # ---------------------------------------------------------------- 05
    # add experiments
    for _experiment in _rp.track(_RUNNER.registered_experiments.values(), task_name="Register views for Experiments"):
        _group_key = None
        if bool(_experiment.group_by):
            _group_key = " > ".join(_experiment.group_by)
        _dashboard.experiment_view.add(
            hashable=_experiment, group_key=_group_key,
        )

    # ---------------------------------------------------------------- 06
    # log
    _rp.update("The view is now opened in external window. Close it to terminate.")

    # ---------------------------------------------------------------- 07
    # run
    gui.Engine.run(_dashboard)


@_APP.command(help="Archive/partition/upload the results folder")
def archive(
    part_size: Annotated[int, typer.Option(help="Max part size in MB to break the resulting archive file.")] = None,
    transmft: Annotated[bool, typer.Option(help="Upload resulting files to cloud drive and make script to download them.")] = False,
):
    if part_size is None:
        _cmd_tokens = [
            "tar", "-cvf",
            f"{_RUNNER.cwd.local_path.as_posix()}.tar",
            f"{_RUNNER.cwd.local_path.as_posix()}"
        ]
    else:
        _cmd_tokens = [
            "tar", "-cvf", "-", f"{_RUNNER.cwd.local_path.as_posix()}", "|",
            "split", f"--bytes={part_size}m", "--suffix-length=4", "--numeric-suffix", "-",
            f"{_RUNNER.cwd.local_path.as_posix()}.tar",
        ]
    _rp = _RUNNER.richy_panel
    _rp.update(
        f"archiving results dir {_RUNNER.cwd.local_path.as_posix()} "
        f"{'' if part_size is None else 'and making parts '} ... "
        f"{' '.join(_cmd_tokens)}"
    )
    _rp.stop()
    subprocess.run(
        _cmd_tokens, shell=False
    )
    _rp.start()
    # tar -cvf prepared_datas.tar prepared_datas
    # tar -cvf - prepared_datas | split --bytes=399m --suffix-length=4 --numeric-suffix - prepared_datas.tar
    # tar -cvf - <stuff to put in archive> | split --bytes=1m --suffix-length=4 --numeric-suffix - myarchive.tar.


@_APP.command(help="Copies from server to cwd.")
def copy():
    """
    todo: Add support for more switches
      https://superuser.com/questions/314503/what-does-robocopy-mean-by-tweaked-lonely-and-extra

    Switch   Function
    ======== =====================
    /XL      eXclude Lonely files and directories.
    /IT      Include Tweaked files.
    /IS      Include Same files.
    /XC      eXclude Changed files.
    /XN      eXclude Newer files.
    /XO      eXclude Older files.

    Use the following switch to suppress the reporting and processing of Extra files:
    /XX      eXclude eXtra files
    """
    _rp = _RUNNER.richy_panel
    _rp.update("copying results from server to cwd ...")
    _rp.stop()
    _cmd_tokens = [
        "ROBOCOPY",
        _RUNNER.copy_src_dst[1], _RUNNER.copy_src_dst[0],
        "*.*", "/J", "/E", "/ETA"
    ]
    _cmd = " ".join(_cmd_tokens)
    subprocess.run(
        _cmd_tokens, shell=False
    )
    _rp.start()
    print(_cmd)


@_APP.command(help="Cleans the job in runner that are not finished (use carefully).")
def clean():
    """
    """
    _rp = _RUNNER.richy_panel
    for _stage_name, _stage in _rp.track(_RUNNER.flow.stages.items(), task_name="Scanning stages"):
        _rp.update(f"Scanning stage {_stage_name} ...")
        _j: Job
        for _j in _rp.track(_stage.all_jobs, task_name=f"Deleting for stage {_stage_name}"):
            if not _j.is_finished:
                _rp.update(f"Deleting job {_j.short_name}")
                _j.path.delete(recursive=True)


@_APP.command(help="Deletes the job in runner even successfully finished runs (use carefully).")
def delete():
    """
    """
    _rp = _RUNNER.richy_panel
    # todo: support asking prompts later ...
    # _delete = _rp.ask(prompt="Are you sure you want to delete? It will delete even completed runs!!", option='confirm')
    for _stage_name, _stage in _rp.track(_RUNNER.flow.stages.items(), task_name="Scanning stages"):
        _rp.update(f"Scanning stage {_stage_name} ...")
        _j: Job
        for _j in _rp.track(_stage.all_jobs, task_name=f"Deleting for stage {_stage_name}"):
            _rp.update(f"Deleting job {_j.short_name}")
            _j.path.delete(recursive=True)


@_APP.command(help="Lists the jobs in runner that are not finished.")
def unfinished():
    """
    """
    _rp = _RUNNER.richy_panel
    for _stage_name, _stage in _rp.track(_RUNNER.flow.stages.items(), task_name="Scanning stages"):
        _rp.update(f"Scanning stage {_stage_name} ...")
        _j: Job
        for _j in _rp.track(_stage.all_jobs, task_name=f"Scanning for stage {_stage_name}"):
            if not _j.is_finished:
                _rp.log([_j.short_name])


@_APP.command(help="Lists the jobs in runner that have failed.")
def failed():
    """
    """
    _rp = _RUNNER.richy_panel
    for _stage_name, _stage in _rp.track(_RUNNER.flow.stages.items(), task_name="Scanning stages"):
        _rp.update(f"Scanning stage {_stage_name} ...")
        _j: Job
        for _j in _rp.track(_stage.all_jobs, task_name=f"Scanning for stage {_stage_name}"):
            if _j.is_failed:
                _rp.log([_j.short_name])
