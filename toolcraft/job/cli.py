import enum
import typer
import sys
import dataclasses
import typing as t

from .. import error as e
from .__base__ import Runner, Job, JobRunnerClusterType

# noinspection PyTypeChecker
_RUNNER: Runner = None
# noinspection PyTypeChecker
_CLUSTER_TYPE: JobRunnerClusterType = None
_APP = typer.Typer(name="Toolcraft Job Runner")


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
    _rp = _RUNNER.richy_panel
    _rp.update(f"launching jobs on {_CLUSTER_TYPE.name!r}")
    _RUNNER.flow(_CLUSTER_TYPE)


@_APP.command()
def run(
    method: str = typer.Argument(..., help="Method to execute in runner."),
    experiment: t.Optional[str] = typer.Argument(None, help="Experiment which will be used by method in runner.")
):
    """
    Run a job in runner.
    """
    _rp = _RUNNER.richy_panel
    # note that this will consume cli args method and experiment to find respective job
    # check the code for property `_RUNNER.job`
    _job = _RUNNER.job


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
