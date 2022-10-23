"""
todo: deprecate in favour of dapr module
"""
import abc
import datetime
import enum
import inspect
import pathlib
import typing as t
import dataclasses
import subprocess
import itertools
import yaml
import sys
import asyncio
import hashlib
import types
_now = datetime.datetime.now

from . import logger
from . import error as e
from . import marshalling as m
from . import util
from . import storage as s
from . import richy
from .gui import UseMethodInForm

try:
    import tensorflow as tf
    from tensorflow.python.training.tracking import util as tf_util
except ImportError:
    tf = None
    tf_util = None


# noinspection PyUnreachableCode
if False:
    from . import gui


_LOGGER = logger.get_logger()
_MONITOR_FOLDER = "monitor"


class ArtifactViewer:
    """
    Just add static methods to the subclasses ... and make sure that they have only one arg named `data`

    Note that this class has no static methods

    Then any artifact-file that is saved in artifacts folder and whose name matches one of static method of this
    class is supported ...

    Unknown file names will get a Text widget stating that it is `unknown artifact`

    For supporting more artifacts simple extend this class and any static methods in child class will be registered

    todo: this pattern seems good for register-plugins kind of things ... see if it can be added elsewhere
    """

    _fn_mapper = {}

    def __init_subclass__(cls, **kwargs):
        # validation
        # todo: add validation to test if only static methods are defined the subclasses

        # detect fn's and register
        for _ in dir(cls):
            if _.startswith("_"):
                continue
            if _ in ArtifactViewer._fn_mapper.keys():
                raise e.code.CodingError(
                    msgs=[f"You have already registered artifact-viewer for "
                          f"key `{_}` with function "
                          f"{ArtifactViewer._fn_mapper[_]}"]
                )
            ArtifactViewer._fn_mapper[_] = getattr(cls, _)

    @staticmethod
    def call(artifact: str, experiment: t.Optional["Experiment"], file_path: s.Path) -> "gui.widget.Widget":
        from . import gui

        # if file does not exist
        if not file_path.exists():
            return gui.widget.Text(
                f"Cannot find artifact for {file_path.name!r} on the disk ...\n{file_path}"
            )
        # if directly supported then return
        elif artifact in ArtifactViewer._fn_mapper.keys():
            if experiment is None:
                _fn = ArtifactViewer._fn_mapper[artifact]
                if 'experiment' in inspect.signature(_fn).parameters.keys():
                    raise e.code.CodingError(
                        msgs=[f"Please do not define kwarg `experiment` in function {_fn} "
                              f"as it not meant to be used with it ..."]
                    )
                return _fn(file_path=file_path)
            else:
                return ArtifactViewer._fn_mapper[artifact](experiment=experiment, file_path=file_path)
        # if artifact has dot then we need to call extension methods
        elif artifact.find(".") != -1:
            artifact_m = "dot_" + artifact.split(".")[1]
            if artifact_m in ArtifactViewer._fn_mapper.keys():
                return ArtifactViewer._fn_mapper[artifact_m](experiment=experiment, file_path=file_path)
            else:
                return gui.widget.Text(f"View not provided for file extension {'*.'+artifact.split('.')[1]!r} \n"
                                       f"... cannot render ... \n"
                                       f"Please support method {artifact_m!r}")
        else:
            return gui.widget.Text(
                f"View not provided for artifact {artifact!r} \n"
                f"... cannot render ... \n"
                f"Please support method {artifact!r}")

    @staticmethod
    def dot_png(experiment: "Experiment", file_path: s.Path) -> "gui.widget.Widget":
        from . import gui
        subprocess.Popen(["start", file_path.local_path.as_posix()], shell=True)
        return gui.widget.Text(f"Image will be opened in external window\n{file_path}")

    @staticmethod
    def dot_txt(experiment: "Experiment", file_path: s.Path) -> "gui.widget.Widget":
        from . import gui
        return gui.widget.Text(file_path.read_text())


class JobRunnerClusterType(m.FrozenEnum, enum.Enum):
    """
    todo: support ibm_lsf over ssh using https://www.fabfile.org
    """
    ibm_lsf = enum.auto()
    local = enum.auto()


class JobFlowId(t.NamedTuple):
    """
    A tuple that helps you find job in the Flow
    """
    stage: int
    job_group: int
    job: int

    def __str__(self):
        return f"[ stage: {self.stage}, job_group: {self.job_group}, job: {self.job} ]"


class JobGroupFlowId(t.NamedTuple):
    """
    A tuple that helps you find job group in the Flow
    """
    stage: int
    job_group: int

    def __str__(self):
        return f"[ stage: {self.stage}, job_group: {self.job_group} ]"


@dataclasses.dataclass
class Tag:

    name: str
    manager: "TagManager"

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        _ret = self.manager.path / self.name
        return _ret

    def create(self, data: t.Dict[str, t.Any] = None):
        if self.path.exists():
            raise e.code.CodingError(
                msgs=[f"Tag at {self.path} already exists ..."]
            )
        if data is None:
            data = {}
        if "time" in data.keys():
            raise e.code.CodingError(
                msgs=[
                    f"Do not supply key time in data dict we will add it ..."
                ]
            )
        data["time"] = _now()
        _LOGGER.info(msg=f"Creating tag {self.path}")
        self.path.write_text(text=yaml.safe_dump(data))

    def read(self) -> t.Optional[t.Dict[str, t.Any]]:
        if not self.path.exists():
            return None
        _LOGGER.info(msg=f"Reading tag {self.path}")
        return yaml.safe_load(self.path.read_text())

    def exists(self) -> bool:
        return self.path.exists()

    def delete(self):
        if self.path.exists():
            _LOGGER.info(msg=f"Deleting tag {self.path}")
            self.path.delete()
        else:
            raise e.code.CodingError(
                msgs=[
                    f"The tag {self.path} does not exist so cannot delete ..."
                ]
            )

    def update(self, data: t.Dict[str, t.Any]):
        # _LOGGER.info(msg=f"Updating tag {self.path}")
        raise e.code.NotYetImplemented(msgs=[f"yet to implement {Tag.update}"])


@dataclasses.dataclass
class TagManager:
    """
    todo: we might want these tags to save state on some state server ...
      so that we can check states there ...
    todo: can we route all tags to simple database file ...
      To support dynamic tags we might need some document storage database instead of
      fixed schema database ...
    """
    job: "Job"

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        _ret = self.job.path / "tags"
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    @util.CacheResult
    def launched(self) -> Tag:
        return Tag(name="launched", manager=self)

    @property
    @util.CacheResult
    def started(self) -> Tag:
        return Tag(name="started", manager=self)

    @property
    @util.CacheResult
    def running(self) -> Tag:
        return Tag(name="running", manager=self)

    @property
    @util.CacheResult
    def failed(self) -> Tag:
        return Tag(name="failed", manager=self)

    @property
    @util.CacheResult
    def finished(self) -> Tag:
        return Tag(name="finished", manager=self)

    @property
    @util.CacheResult
    def description(self) -> Tag:
        return Tag(name="description", manager=self)

    def view(self) -> "gui.widget.Widget":
        # ----------------------------------------------------------------- 01
        # read tags
        _launched = self.launched.read()
        _started = self.started.read()
        _running = self.running.read()
        _finished = self.finished.read()
        _failed = self.failed.read()
        _description = self.description.read()

        # ----------------------------------------------------------------- 02
        # make gui
        from . import gui
        _ret = gui.widget.Group(horizontal=False)
        with _ret:
            with gui.widget.Group(horizontal=True):
                gui.widget.Text(default_value=f"[[[ Job: {self.job.method.__name__} ]]]")
                if _finished:
                    gui.widget.Text(default_value="--- FINISHED ---")
                elif _failed:
                    gui.widget.Text(default_value="XXX  FAILED  XXX")
                elif _launched:
                    if _running:
                        gui.widget.Text(default_value="--- RUNNING  ---")
                    elif _started:
                        gui.widget.Text(default_value="--- STARTED  ---")
                    else:
                        gui.widget.Text(default_value="--- LAUNCHED ---")
                else:
                    gui.widget.Text(default_value=">> PLEASE RUN <<")
            if _launched:
                gui.widget.Text(default_value=f"launched at: {_launched}")
            if _started:
                gui.widget.Text(default_value=f"started at: {_started}")
            if _running:
                gui.widget.Text(default_value=f"running from: {_running}")
            if _failed:
                gui.widget.Text(default_value=f"failed at: {_failed}")
            if _finished:
                gui.widget.Text(default_value=f"finished at: {_finished}")
            if _description:
                gui.widget.Text(default_value=f"\n-- description --\n {_description}")

        # ----------------------------------------------------------------- 03
        # return
        return _ret


class JobViewerInternal(m.Internal):
    job: "Job"


@dataclasses.dataclass(frozen=True)
class JobViewer(m.HashableClass):

    method_name: str
    experiment: t.Optional["Experiment"]

    @property
    @util.CacheResult
    def internal(self) -> JobViewerInternal:
        return JobViewerInternal(owner=self)

    @property
    @util.CacheResult
    def job(self) -> "Job":
        _ret = self.internal.job
        if _ret.experiment != self.experiment:
            raise e.code.CodingError(
                msgs=["Job set to this JobViewer is not correct ..."]
            )
        if _ret.method.__name__ != self.method_name:
            raise e.code.CodingError(
                msgs=[f"The method name set is not correct"]
            )
        return _ret

    @property
    @util.CacheResult
    def button_label(self) -> str:
        if self.experiment is None:
            return self.method_name
        _title, _args = self.experiment.view_gui_label
        return "\n".join([_title, *_args])

    @m.UseMethodInForm(label_fmt="button_label")
    def job_gui_with_run(self) -> "gui.form.HashableMethodsRunnerForm":
        # import
        from . import gui

        # if finished return
        _job = self.job
        if _job.is_finished or _job.is_failed:
            return self.job_gui()

        _ret = gui.form.HashableMethodsRunnerForm(
            title=self.button_label.split("\n")[0],
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["tags_gui", "artifacts_gui", "run_gui"],
            collapsing_header_open=True,
        )

        with _ret._button_bar:
            _txt = gui.widget.Text(default_value="<-- please run")
            # _txt.move_up()

        return _ret

    @m.UseMethodInForm(label_fmt="button_label")
    def job_gui(self) -> "gui.form.HashableMethodsRunnerForm":
        from . import gui

        _ret = gui.form.HashableMethodsRunnerForm(
            title=self.button_label.split("\n")[0] + f" : {self.method_name}",
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["tags_gui", "artifacts_gui", ],
            collapsing_header_open=True,
        )

        _job = self.job
        with _ret._button_bar:
            if _job.is_failed:
                gui.widget.Text(default_value="--- FAILED ---")
            elif _job.is_finished:
                gui.widget.Text(default_value="--- FINISHED ---")
            else:
                raise e.code.ShouldNeverHappen(msgs=[])

        return _ret

    @m.UseMethodInForm(label_fmt="Info")
    def info_widget(self) -> "gui.widget.Text":
        """
        We override as we are interested in field `experiment` and not `self` ...
        """
        # import
        from . import gui
        # make
        _experiment = self.experiment
        _text = f"job-id: {self.job.job_id}\n" \
                f"flow-id: {self.job.flow_id}\n" \
                f"method: {self.method_name}\n\n"
        if _experiment is not None:
            _text += f"hex-hash: {_experiment.hex_hash}\n" \
                    f"{_experiment.yaml()}"
        # noinspection PyUnresolvedReferences
        _ret_widget = gui.widget.Text(default_value=_text)
        # return
        return _ret_widget

    @m.UseMethodInForm(label_fmt="tags")
    def tags_gui(self) -> "gui.widget.Text":
        return self.job.tag_manager.gui()

    @m.UseMethodInForm(label_fmt="artifacts")
    def artifacts_gui(self) -> "gui.form.ButtonBarForm":
        return self.job.artifact_manager.gui()

    @m.UseMethodInForm(label_fmt="run")
    def run_gui(self) -> "gui.widget.Group":
        return self.job.sub_process_manager.gui()


@dataclasses.dataclass
class ArtifactManager:
    job: "Job"

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        _ret = self.job.path / "artifacts"
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    def save_compressed_pickle(self, name: str, data: t.Any):
        _file = self.path / name
        _file.save_compressed_pickle(data)

    def load_compressed_pickle(self, name: str) -> t.Any:
        _file = self.path / name
        return _file.load_compressed_pickle()

    def available_artifacts(self) -> t.List[str]:
        return [_.name for _ in self.path.ls()]

    def gui(self) -> "gui.form.ButtonBarForm":
        # import
        from . import gui

        # class for ButtonBarForm that supports loading artifacts
        @dataclasses.dataclass
        class ButtonBarForm(gui.form.ButtonBarForm):

            def init(self_1):
                # call super
                super().init()

                # use a different callback
                # make class for callback handling
                @dataclasses.dataclass
                class Callback(gui.callback.Callback):
                    # noinspection PyMethodParameters
                    def fn(self_2, sender: gui.widget.Widget):
                        _key = sender.get_user_data()["key"]

                        # the file on disk
                        _file = self.path / _key

                        # add ui
                        self_1._receiver.clear()
                        _w = ArtifactViewer.call(
                                artifact=_key, experiment=self.job.experiment, file_path=_file)
                        self_1._receiver(_w)

                # set the var
                self_1._callback = Callback()

        _form = ButtonBarForm(title=None, collapsing_header_open=False)

        for _ in self.available_artifacts():
            # todo: see if specialization can be done when fn is None ...
            #   i.e. use different callback in parent class gui.form.ButtonBarForm instead of overriding here
            _form.register(key=_, fn=None)

        return _form


@dataclasses.dataclass
class SubProcessManager:

    job: "Job"

    @property
    @util.CacheResult
    def stdout_stream(self) -> t.List[str]:
        return []

    @property
    @util.CacheResult
    def stderr_stream(self) -> t.List[str]:
        return []

    @property
    @util.CacheResult
    def blocking_task(self) -> "gui.BlockingTask":
        """
        Note we cache and also queue this task on first call as we do not want to get this task
        launched multiple times
        """
        from . import gui
        _bt = gui.BlockingTask(
            fn=self.blocking_fn,
            # todo: making this false raises pickling error as the blocking task is run in different thread
            #    we need to investigate if we want to fix this
            concurrent=True
        )
        _bt.add_to_task_queue()
        return _bt

    async def awaitable_fn(self, receiver_grp: "gui.widget.Group"):
        from .gui.widget import Text
        _blinker = itertools.cycle(["..", "....", "......"])

        try:

            # calling property will schedule blocking task to run in queue only once
            # so consecutive calls will safely bypass calling blocking_fn
            _blocking_task = self.blocking_task

            # try to get future ... for first call to property the future might not be available, so we await
            _future = None
            while _future is None:
                await asyncio.sleep(0.4)
                _future = _blocking_task.future

            # loop infinitely
            while receiver_grp.does_exist:

                # small sleep
                await asyncio.sleep(0.6)

                # if not build continue
                if not receiver_grp.is_built:
                    continue

                # dont update if not visible
                # todo: can we await on bool flags ???
                if not receiver_grp.is_visible:
                    continue

                # clear group
                receiver_grp.clear()

                # add streams
                with receiver_grp:
                    Text(default_value="="*15 + " STDOUT " + "="*15)
                    Text(default_value="\n".join(self.stdout_stream))
                    Text(default_value="="*15 + " ====== " + "="*15)
                    Text(default_value="="*15 + " STDERR " + "="*15)
                    Text(default_value="\n".join(self.stderr_stream))
                    Text(default_value="="*15 + " ====== " + "="*15)

                # if running
                if _future.running():
                    with receiver_grp:
                        Text(default_value=next(_blinker))
                    continue

                # if done
                if _future.done():
                    _exp = _future.exception()
                    if _exp is None:
                        with receiver_grp:
                            Text(default_value="="*15 + " ======= " + "="*14)
                            Text(default_value="="*15 + " SUCCESS " + "="*14)
                            Text(default_value="="*15 + " ======= " + "="*14)
                        break
                    else:
                        with receiver_grp:
                            Text(default_value="X"*15 + " XXXXXXX " + "X"*14)
                            Text(default_value="X"*15 + " FAILURE " + "X"*14)
                            Text(default_value="X"*15 + " XXXXXXX " + "X"*14)
                        raise _exp

        except Exception as _e:
            if receiver_grp.does_exist:
                raise _e
            else:
                ...

    def blocking_fn(self):
        """
        todo: need to see why streams updated here do not show up in awaitable fn ...
        """

        _stdout_stream, _stderr_stream = self.stdout_stream, self.stderr_stream
        _process = subprocess.Popen(
            self.job.cli_command,
            # stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,
        )
        # todo: make it work with command line
        # through command line this causes issue ...
        # but works with pycharm (note that the sting color and special unicode characters are lost)
        # for _line in _process.stdout:
        #     _stdout_stream.append(_line)
        # for _line in _process.stderr:
        #     _stderr_stream.append(_line)

        _stdout_stream.append("... waiting for process to finish ...")
        _stderr_stream.append("... waiting for process to finish ...")
        _process.wait()

        _ret_code = _process.returncode
        if _ret_code == 0:
            _final_lines = ["=" * 30, f"Finished with return code {_ret_code}", "=" * 30]
            _stdout_stream.extend(_final_lines)
        else:
            _final_lines = ["=" * 30, f"Failed with return code {_ret_code}", "=" * 30]
            _stderr_stream.extend(_final_lines)
        if _ret_code != 0:
            raise e.code.CodingError(
                msgs=[
                    f"Below cli command failed with error code {_ret_code}:",
                    self.job.cli_command,
                    f"The stderr from subprocess is as below:", _stderr_stream,
                ]
            )

    def gui(self) -> "gui.widget.Group":
        # import
        from . import gui

        # test that the there is no residual job running failed started or completed
        # todo: only is_started check should suffice ...
        if self.job.is_started:
            raise e.code.CodingError(
                msgs=[
                    "You might not need to call this multiple times!!!",
                    "Job has already started for cli command: ", self.job.cli_command,
                ]
            )
        if self.job.is_running:
            raise e.code.CodingError(
                msgs=[
                    "Multiple calls detected for cli command: ", self.job.cli_command,
                ]
            )
        if self.job.is_failed:
            raise e.code.CodingError(
                msgs=[
                    "You might not need to call this multiple times!!!",
                    "Previous call to below cli command has failed: ", self.job.cli_command,
                ]
            )
        if self.job.is_finished:
            raise e.code.CodingError(
                msgs=[
                    "You might not need to call this multiple times!!!",
                    "Previous call to below cli command has finished: ", self.job.cli_command,
                ]
            )

        # return widget
        _grp = gui.widget.Group()

        # make awaitable task and run that can read process streams
        gui.AwaitableTask(
            fn=self.awaitable_fn, fn_kwargs=dict(receiver_grp=_grp)
        ).add_to_task_queue()

        # return
        return _grp


class Job:
    """
    Note that this job is available only on server i.e. to the submitted job on
    cluster ... on job launching machine access to this property will raise error

    Note this can read cli args and construct `method` and `method_kwargs` fields
    """

    @property
    @util.CacheResult
    def viewer(self) -> JobViewer:
        _ret = JobViewer(experiment=self.experiment, method_name=self.method.__name__)
        _ret.internal.job = self
        return _ret

    @property
    @util.CacheResult
    def tag_manager(self) -> TagManager:
        return TagManager(job=self)

    @property
    @util.CacheResult
    def artifact_manager(self) -> ArtifactManager:
        return ArtifactManager(job=self)

    @property
    @util.CacheResult
    def sub_process_manager(self) -> SubProcessManager:
        return SubProcessManager(job=self)

    @property
    def is_launched(self) -> bool:
        return self.tag_manager.launched.exists()

    @property
    def is_started(self) -> bool:
        return self.tag_manager.started.exists()

    @property
    def is_running(self) -> bool:
        return self.tag_manager.running.exists()

    @property
    def is_finished(self) -> bool:
        return self.tag_manager.finished.exists()

    @property
    def is_failed(self) -> bool:
        return self.tag_manager.finished.exists()

    @property
    def flow_id(self) -> str:
        if self._flow_id is None:
            raise e.code.CodingError(
                msgs=[
                    f"This must be automatically set by code ..."
                ]
            )
        return self._flow_id

    @flow_id.setter
    def flow_id(self, value: str):
        """
        This takes in account
        + fn_name
        + fn_kwargs if present
        + experiment hex_hash if present
        """
        if self._flow_id is None:
            self._flow_id = value + f"|{self.path.suffix_path.replace('/', '|')}"
        else:
            raise e.code.CodingError(
                msgs=[f"This property is already set you cannot set it again ..."]
            )

    @property
    def job_id(self) -> str:
        return f"x{hashlib.sha256(self.flow_id.encode('utf-8')).hexdigest()[:16]}"

    @property
    def is_on_main_machine(self) -> bool:
        return self.runner.is_on_main_machine

    @property
    @util.CacheResult
    def tf_chkpts_path(self) -> s.Path:
        _ret = self.path / "tf_chkpts"
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    def wait_on_jobs(self) -> t.List["Job"]:
        _wait_on_jobs = []
        for _j in self._wait_on:
            if isinstance(_j, Job):
                _wait_on_jobs += [_j]
            else:
                _wait_on_jobs += _j.bottom_jobs
        return _wait_on_jobs

    @property
    def cli_command(self) -> t.List[str]:
        _command = [
            "python", self.runner.py_script, self.method.__func__.__name__,
        ]
        if self.experiment is not None:
            _command += [self.experiment.hex_hash]
        return _command

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        """
        Note that if group_by is defined in Experiment then the nested folders are created and `hashable.hex_hash`
        is created inside it.

        As an advantage we can have different instances made up of different Experiment classes store in same nested
        folders. This can be easily achieved by having group_by of those Experiment classes return similar things ;)

        todo: integrate this with storage with partition_columns ... (not important do only if necessary)
        """
        _ret = self.runner.cwd
        _ret /= self.method.__func__.__name__
        if self.experiment is not None:
            for _ in self.experiment.group_by:
                _ret /= _
            _ret /= self.experiment.hex_hash
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    def __init__(
        self,
        runner: "Runner",
        method: t.Callable,
        experiment: t.Optional["Experiment"] = None,
    ):
        # ------------------------------------------------------------------ 01
        # assign some vars
        self.runner = runner
        # noinspection PyTypeChecker
        self.method = method  # type: types.MethodType
        self.experiment = experiment
        # make simple name
        self.name = method.__name__
        if experiment is not None:
            self.name += f":{experiment.hex_hash[:10]}"
        # container to save wait_on jobs
        self._wait_on = []  # type: t.List[t.Union[Job, SequentialJobGroup, ParallelJobGroup]]
        # noinspection PyTypeChecker
        self._flow_id = None  # type: str

        # ------------------------------------------------------------------ 02
        # make sure that method is from same runner instance
        try:
            # noinspection PyTypeChecker
            if id(self.method.__self__) != id(runner):
                raise e.code.CodingError(
                    msgs=["Was expecting them to be same instance"]
                )
        except Exception as _ex:
            raise e.code.CodingError(
                msgs=[
                    f"Doesn't seem like a method of an instance ...", _ex
                ]
            )

        # ------------------------------------------------------------------ 03
        # check if method supplies is available in runner
        if experiment is None:
            e.validation.ShouldBeOneOf(
                value=method, values=runner.methods_to_be_used_in_jobs()["runner"],
                msgs=[
                    f"Method {method} is not recognized as a method that can be used with runner level Job's"
                ]
            ).raise_if_failed()
        else:
            e.validation.ShouldBeOneOf(
                value=method, values=runner.methods_to_be_used_in_jobs()["experiment"],
                msgs=[
                    f"Method {method} is not recognized as a method that can be used with experiment level Job's"
                ]
            ).raise_if_failed()

    def __call__(self, cluster_type: JobRunnerClusterType):
        # check health
        self.check_health()

        # launch
        if self.is_on_main_machine:
            self._launch_on_main_machine(cluster_type)
        else:
            self._launch_on_worker_machine()

    def _launch_on_worker_machine(self):
        """
        The jobs are run on cluster ... this piece of code will execute on the
        worker machines that will execute those scheduled jobs
        """

        # ------------------------------------------------------------------- 01
        # reconfig logger to change log file for job
        import logging
        _log = self.path / "toolcraft.log"
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
                    "name": self.name,
                    "started": _start.ctime(),
                }
            ]
        )

        # ------------------------------------------------------------------- 02
        # check if launcher client machine has created launched tag
        if not self.tag_manager.launched.exists():
            raise e.code.CodingError(
                msgs=[
                    "We expect that `launched` tag is created by client launching machine .... "
                    "check _launch_on_main_machine"
                ]
            )

        # ------------------------------------------------------------------- 03
        # indicates that job is started
        self.tag_manager.started.create()

        # ------------------------------------------------------------------- 04
        # indicate that job will now be running
        # also note this acts as semaphore and is deleted when job is finished
        # ... hence started tag is important
        self.tag_manager.running.create()

        # ------------------------------------------------------------------- 05
        _failed = False
        try:
            for _wj in self.wait_on_jobs:
                if not _wj.is_finished:
                    raise e.code.CodingError(
                        msgs=[f"Wait-on job with flow-id {_wj.flow_id} and job-id "
                              f"{_wj.job_id} is supposed to be finished ..."]
                    )
            _sub_title = [
                f"name: {self.name}", f"py-script: {self.runner.py_script}",
            ]
            _job_display_name = f"{self.runner.__module__}.{self.runner.__class__.__name__}.{self.method.__name__}"
            with richy.StatusPanel(
                title="Running Job",
                sub_title=_sub_title, tc_log=logger.get_logger(self.runner.__module__)
            ) as _rp:
                if self.experiment is None:
                    with self.runner(richy_panel=_rp):
                        self.method()
                else:
                    with (self.runner(richy_panel=_rp), self.experiment(richy_panel=_rp)):
                        self.method(experiment=self.experiment)
            self.tag_manager.running.delete()
            self.tag_manager.finished.create()
            _end = _now()
            _LOGGER.info(
                msg=f"Successfully finished job on worker machine ...",
                msgs=[
                    {
                        "name": self.name,
                        "py-script": self.runner.py_script,
                        "started": _start.ctime(),
                        "ended": _end.ctime(),
                        "seconds": str((_end - _start).total_seconds()),
                    }
                ]
            )
        except Exception as _ex:
            _failed = True
            self.tag_manager.failed.create(
                data={
                    "exception": str(_ex)
                }
            )
            _end = _now()
            _LOGGER.info(
                msg=f"Failed job on worker machine ...",
                msgs=[
                    {
                        "name": self.name,
                        "py-script": self.runner.py_script,
                        "started": _start.ctime(),
                        "ended": _end.ctime(),
                        "seconds": str((_end - _start).total_seconds()),
                        "exception": str(_ex),
                    }
                ]
            )
            self.tag_manager.running.delete()
            # above thing will tell toolcraft that things failed gracefully
            # while below raise will tell cluster systems like bsub that job has failed
            # todo for `JobRunnerClusterType.local_on_same_thread` this will not allow
            #  future jobs to run ... but this is expected as we want to debug in
            #  this mode mostly
            raise _ex

    def _launch_on_main_machine(self, cluster_type: JobRunnerClusterType):
        """
        This runs on your main machine so that jobs are launched on cluster
        todo: make this run on client and run jobs over ssh connection ...
        """
        # ------------------------------------------------------------- 01
        # make command to run on cli
        _command = self.cli_command

        # ------------------------------------------------------------- 02
        # create tag so that worker machine knows that the client has launched it
        self.tag_manager.launched.create()

        # ------------------------------------------------------------- 03
        # launch
        # todo: might be feasible only with `local` not sure about `ibm_lsf`
        #   + figure out how `subprocess.run` kwargs can be used to pull the console rendered by subprocess i.e.
        #     things like rich ui can be grabbed and streamed
        #   + explore logger handlers with extra kwargs to grab streams using `subprocess.run`
        # ------------------------------------------------------------- 03.01
        if cluster_type is JobRunnerClusterType.local:
            subprocess.run(_command)
        # ------------------------------------------------------------- 03.02
        elif cluster_type is JobRunnerClusterType.ibm_lsf:
            # todo: when self.path is not local we need to see how to log files ...
            #   should we stream or dump locally ?? ... or maybe figure out
            #   dapr telemetry
            _log = self.path / "bsub.log"
            _nxdi_prefix = ["bsub", "-oo", _log.local_path.as_posix(), "-J", self.job_id]
            _wait_on_jobs = self.wait_on_jobs
            if bool(_wait_on_jobs):
                _wait_on = \
                    " && ".join([f"done({_.job_id})" for _ in _wait_on_jobs])
                _nxdi_prefix += ["-w", f"{_wait_on}"]
            _command = _nxdi_prefix + _command
            subprocess.run(_command)

        # ------------------------------------------------------------- 03.03
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[f"Unsupported cluster_type {cluster_type}"]
            )

        # ------------------------------------------------------------- 04
        # log
        _LOGGER.info(
            msg=f"Launching jobs from main machine with below command...",
            msgs=[_command]
        )

    def wait_on(self, wait_on: t.Union['Job', 'SequentialJobGroup', 'ParallelJobGroup']) -> "Job":
        self._wait_on.append(wait_on)
        return self

    @classmethod
    def from_cli(
        cls,
        runner: "Runner",
    ) -> "Job":
        # test if running on machines that execute jobs ...
        if runner.is_on_main_machine:
            raise e.code.CodingError(
                msgs=[
                    "This call is available only for jobs submitted to worker ... "
                    "it cannot be accessed by client which launches jobs ..."
                ]
            )

        # fetch method
        _method_name = sys.argv[1]
        _method = getattr(runner, _method_name)

        # fetch experiment
        if len(sys.argv) == 2:
            return runner.associated_jobs[_method]
        elif len(sys.argv) == 3:
            _experiment = runner.monitor.get_experiment_from_hex_hash(hex_hash=sys.argv[2])
            return _experiment.associated_jobs[_method]
        else:
            raise e.code.CodingError(
                msgs=[
                    "there can be only two or three sys arguments ... found",
                    sys.argv,
                ]
            )

    def check_health(self):
        # ------------------------------------------------------------- 01
        # some vars
        _job_info = {"name": self.name, "py-script": self.runner.py_script, "path": self.path.full_path}
        _tm = self.tag_manager
        _launched = _tm.launched.read()
        _started = _tm.started.read()
        _running = _tm.running.read()
        _finished = _tm.finished.read()
        _failed = _tm.failed.read()

        # ------------------------------------------------------------- 02
        # if either finished or failed running tag must never be present as we take care in code to delete it
        if _finished or _failed:
            if _running:
                raise e.code.ShouldNeverHappen(
                    msgs=[
                        "the previous job was wither failed or finished but the running tag was never deleted",
                        "Please fix any bugs ...",
                        _job_info,
                    ]
                )
        # ------------------------------------------------------------- 03
        # raise error if already called (i.e. finished or failed)
        if _finished:
            raise e.code.CodingError(
                msgs=[
                    "The job was already finished ... ",
                    "Please refrain from calling again or test with property `is_finished` before calling",
                    _job_info,
                    {"finished msg": _finished},
                ]
            )
        if _failed:
            raise e.code.CodingError(
                msgs=[
                    "The job was already failed ... please delete run files manually to run it again ...",
                    _job_info,
                    {"failed msg": _failed},
                ]
            )
        # ------------------------------------------------------------- 04
        # if _running is present then _started should be present
        if _running:
            if not _started:
                raise e.code.ShouldNeverHappen(
                    msgs=[
                        "When running started tag is expected to be present",
                        _job_info,
                    ]
                )
        # if _started is present then _launched should be present
        if _started:
            if not _launched:
                raise e.code.ShouldNeverHappen(
                    msgs=[
                        "When started launched tag is expected to be present",
                        _job_info,
                    ]
                )

        # ------------------------------------------------------------- 05
        if self.is_on_main_machine:
            if _launched or _started or _running:
                raise e.code.CodingError(
                    msgs=[
                        "You are on main (client) machine that launches job",
                        "So no tags including launched must be present",
                        _job_info,
                        {
                            "launched msg": _launched, "started msg": _started, "running msg": _running,
                        },
                    ]
                )
        else:
            if not _launched:
                raise e.code.CodingError(
                    msgs=[
                        "You are on worker machine so we expect to have launched tag that will be created by main "
                        "(i.e. client) machine that launches job",
                        _job_info,
                    ]
                )
            if _started or _running:
                raise e.code.CodingError(
                    msgs=[
                        "You are on worker machine that runs job",
                        "So no tag started and running must not be present",
                        _job_info,
                        {
                            "launched msg": _launched, "started msg": _started, "running msg": _running,
                        },
                    ]
                )

    def view(self) -> "gui.widget.Widget":
        return self.tag_manager.view()

    # noinspection PyUnresolvedReferences
    def save_tf_chkpt(self, name: str, tf_chkpt: "tf.train.Checkpoint"):
        """
        todo: make this compatible for all type of path
        """
        # check if tensorflow available
        if tf is None:
            raise e.code.CodingError(
                msgs=["Tensorflow is not available so cannot call dont use this method"]
            )

        # if name has . do not allow
        if name.find(".") != -1:
            raise e.validation.NotAllowed(
                msgs=[f"Tensorflow checkpoint saving mechanism does not allow `.` in checkpoint names ... "
                      f"Correct the value `{name}`"]
            )

        # check if files present
        _file = self.tf_chkpts_path / name
        _data_file = self.tf_chkpts_path / f"{name}.data-00000-of-00001"
        _index_file = self.tf_chkpts_path / f"{name}.index"
        if _file.exists() or _data_file.exists() or _index_file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"looks like there is already a checkpoint artifact or simple artifact for name '{name}' present"
                ]
            )

        # write
        # options have type tf.train.CheckpointOptions
        tf_chkpt.write(file_prefix=_file.local_path.as_posix(), options=None)

    def restore_tf_chkpt(self, name: str, tf_chkpt: "tf.train.Checkpoint"):
        """
        todo: make this compatible for all type of path
        """
        # check if tensorflow available
        if tf is None:
            raise e.code.CodingError(
                msgs=["Tensorflow is not available so cannot call dont use this method"]
            )

        # check if respective files present
        _file = self.tf_chkpts_path / name
        _data_file = self.tf_chkpts_path / f"{name}.data-00000-of-00001"
        _index_file = self.tf_chkpts_path / f"{name}.index"
        if not _data_file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"was expecting {_data_file.name} to be present on the disk ..."
                ]
            )
        if not _index_file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"was expecting {_index_file.name} to be present on the disk ..."
                ]
            )
        if _file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"This should not happen as tensorflow saves things as data and index file ..."
                ]
            )

        # options have type tf.train.CheckpointOptions
        _status = tf_chkpt.read(
            save_path=_file.local_path.as_posix(), options=None)  # type: tf_util.CheckpointLoadStatus
        _status.assert_existing_objects_matched()
        _status.assert_nontrivial_match()
        _status.expect_partial()
        _status.assert_consumed()


class JobGroup(abc.ABC):
    """
    We can have multiple JobGroup within
      stages so that we can move ahead with next stages if we only depend on one of
      JobGroup from previous stage
    """

    @property
    def flow_id(self) -> str:
        if self._flow_id is None:
            raise e.code.CodingError(
                msgs=[
                    f"This must be automatically set by code ..."
                ]
            )
        return self._flow_id

    @flow_id.setter
    def flow_id(self, value: str):
        if self._flow_id is None:
            self._flow_id = value
            _len = len(str(len(self.jobs)))
            for _i, _j in enumerate(self.jobs):
                if isinstance(_j, Job):
                    _j.flow_id = f"{value}.j{_i:0{_len}d}"
                elif isinstance(_j, SequentialJobGroup):
                    _j.flow_id = f"{value}.s{_i:0{_len}d}"
                elif isinstance(_j, ParallelJobGroup):
                    _j.flow_id = f"{value}.p{_i:0{_len}d}"
                else:
                    raise e.code.CodingError(
                        msgs=[f"unsupported type {type(_j)}"]
                    )
        else:
            raise e.code.CodingError(
                msgs=[f"This property is already set you cannot set it again ..."]
            )

    @property
    def is_on_main_machine(self) -> bool:
        return self.runner.is_on_main_machine

    @property
    @util.CacheResult
    def all_jobs(self) -> t.List[Job]:
        _ret = []
        for _j in self.jobs:
            if isinstance(_j, Job):
                _ret += [_j]
            else:
                _ret += _j.all_jobs
        return _ret

    @property
    @abc.abstractmethod
    def bottom_jobs(self) -> t.List[Job]:
        ...

    @property
    @abc.abstractmethod
    def top_jobs(self) -> t.List[Job]:
        ...

    def __init__(
        self,
        runner: "Runner",
        jobs: t.List[t.Union["ParallelJobGroup", "SequentialJobGroup", Job]],
    ):
        # save vars
        self.runner = runner
        self.jobs = jobs
        # noinspection PyTypeChecker
        self._flow_id = None  # type: str

        # call init
        self.init()

    def __str__(self) -> str:
        return self.flow_id

    def init(self):
        ...


class SequentialJobGroup(JobGroup):
    """
    The jobs here will run in sequential
    """

    @property
    @util.CacheResult
    def bottom_jobs(self) -> t.List[Job]:
        """
        What do we wait on
        """
        _last = self.jobs[-1]
        if isinstance(_last, Job):
            return [_last]
        else:
            return _last.bottom_jobs

    @property
    @util.CacheResult
    def top_jobs(self) -> t.List[Job]:
        """
        What do we start with
        """
        _first = self.jobs[0]
        if isinstance(_first, Job):
            return [_first]
        else:
            return _first.top_jobs

    def init(self):
        # call super
        super().init()

        # this ties up all jobs in list to execute one after other
        for _ in range(1, len(self.jobs)):
            _j = self.jobs[_]
            _pj = self.jobs[_-1]
            if isinstance(_j, Job):
                _j.wait_on(_pj)
            else:
                for __j in _j.top_jobs:
                    __j.wait_on(_pj)


class ParallelJobGroup(JobGroup):
    """
    The jobs here will run in parallel
    """

    @property
    @util.CacheResult
    def bottom_jobs(self) -> t.List[Job]:
        """
        What do we wait on
        """
        _ret = []
        for _j in self.jobs:
            if isinstance(_j, Job):
                _ret += [_j]
            else:
                _ret += _j.bottom_jobs
        return _ret

    @property
    @util.CacheResult
    def top_jobs(self) -> t.List[Job]:
        """
        What do we start with
        """
        _ret = []
        for _j in self.jobs:
            if isinstance(_j, Job):
                _ret += [_j]
            else:
                _ret += _j.top_jobs
        return _ret


class Flow:
    """
    This will decide how jobs will be executed on cluster
    Gets called when script is called without arguments

    Note that stages are made up of list of ParallelJobGroup, while within each ParallelJobGroup we can have
    ParallelJobGroup or SequentialJobGroup ... note that if you want to wait JobGroup within stage to wait over
    previous JobGroup then you need to define that with wait_on

    Note that `other_jobs` are related to methods with `experiment` kwarg. It is mostly jobs that are run on client
    to debug or get some info from job runs that were run on server ... the data will be generated on client where
    viewer is used ... and jobs will be run only when interacted with viewer ...
    example:
    + debug model to find out learning rate
    """

    def __init__(
        self,
        stages: t.List[ParallelJobGroup],
        runner: "Runner",
    ):
        # save reference
        self.stages = stages
        self.runner = runner

        # set flow ids
        _len = len(str(len(self.stages)))
        for _stage_id, _stage in enumerate(self.stages):
            _stage.flow_id = f"#[{_stage_id:0{_len}d}]"

    def __call__(self, cluster_type: JobRunnerClusterType):
        """
        todo: we might want this to be called from client machine and submit jobs via
          ssh ... rather than using instance on cluster to launch jobs
          This will also help to have gui in dearpygui
        """
        # --------------------------------------------------------- 01
        # gather all jobs
        _all_jobs = []
        for _stage in self.stages:
            _all_jobs += _stage.all_jobs

        # --------------------------------------------------------- 02
        # check health of all jobs
        with richy.StatusPanel(
            title="Running the flow for runner ...",
            sub_title=self.runner, tc_log=_LOGGER,
        ) as _rp:
            _rp.update("Checking health of all jobs ...")
            _job: Job
            for _job in _rp.track(sequence=_all_jobs, task_name="check health"):
                _job.check_health()

        # --------------------------------------------------------- 03
        # call jobs ...
        if cluster_type is JobRunnerClusterType.local:
            # tracker containers
            _completed_jobs = []

            # loop over all jobs in flow
            for _j in _all_jobs:
                # extract wait on jobs that need to finished before calling _j
                _wait_jobs = []
                for _wo in _j._wait_on:
                    if isinstance(_wo, Job):
                        _wait_jobs += [_wo]
                    else:
                        _wait_jobs += _wo.bottom_jobs
                for _wj in _wait_jobs:
                    if _wj not in _completed_jobs:
                        raise e.code.CodingError(
                            msgs=[
                                "When not on server we expect that property `all_jobs` should resolve in such "
                                "a way that all `wait_on` jobs must be already done ..",
                                f"Check {_wj.flow_id} which should be completed by now ..."
                            ]
                        )

                # call _j
                _j(cluster_type)

                # append to list as job is completed
                _completed_jobs.append(_j)

        elif cluster_type is JobRunnerClusterType.ibm_lsf:
            _rp = richy.StatusPanel(
                title=f"Launch stages on `{cluster_type.name}` for runner",
                sub_title=self.runner, tc_log=_LOGGER,
                stages=self.stages
            )
            for _stage in _rp:
                _rp.update(f"launching jobs for stage: {_stage}...")
                _jobs = _stage.all_jobs
                _job: t.Union[Job, ParallelJobGroup]
                for _job in _rp.track(
                    sequence=_jobs, task_name=f"stage {_stage}"
                ):
                    _job(cluster_type)
        else:
            raise e.code.NotSupported(
                msgs=[f"Not supported {cluster_type}"]
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

    def status(self) -> t.Dict:
        _ret = dict()
        for _si, _stage in enumerate(self.stages):
            _jobs = _stage.all_jobs
            _total = 0
            _started = 0
            _running = 0
            _finished = 0
            _failed = 0
            _job: Job
            for _job in _jobs:
                _total += 1
                if _job.is_started:
                    _started += 1
                if _job.is_running:
                    _running += 1
                if _job.is_finished:
                    _finished += 1
                if _job.is_failed:
                    _failed += 1
            _ret[f"Stage {_si:03d}"] = dict(
                total=_total, started=_started, running=_running, finished=_finished, failed=_failed,
            )
        return _ret

    def status_text(self) -> "gui.widget.Text":
        from . import gui
        _lines = []
        for _stage, _value in self.status().items():
            _stage_msg = ""
            if _value['running'] != 0:
                _stage_msg = " !!  Running !! "
            if _value['failed'] != 0:
                _stage_msg = " XX  Failed  XX "
            if _value['finished'] == _value['total']:
                _stage_msg = " (: Finished :) "
            _lines += [("---"*15) + _stage_msg]
            _lines += [
                f"{_stage}: Total: {_value['total']:03d}"
            ]
            _lines += [f" >>> Started  {_value['started']:03d} : Running {_value['running']:03d} "]
            _lines += [f" >>> Finished {_value['finished']:03d} : Failed  {_value['failed']:03d} "]
        _lines += ["---"*15]
        return gui.widget.Text(
            default_value="\n".join(_lines)
        )


@dataclasses.dataclass(frozen=True)
class Monitor:
    runner: "Runner"

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        _ret = self.runner.cwd / _MONITOR_FOLDER
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    @util.CacheResult
    def experiments_folder_path(self) -> s.Path:
        _ret = self.path / "experiments"
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    def make_experiment_info_file(self, experiment: "Experiment"):
        _file = self.experiments_folder_path / f"{experiment.hex_hash}.info"
        if not _file.exists():
            _LOGGER.info(
                f"Creating experiment info file {_file.local_path.as_posix()}")
            _file.write_text(experiment.yaml())

    def get_experiment_from_hex_hash(self, hex_hash: str) -> "Experiment":
        _experiment_info_file = self.experiments_folder_path / f"{hex_hash}.info"
        if _experiment_info_file.exists():
            # get class
            _cls = m.HashableClass.get_class(_experiment_info_file)
            # create instance from yaml
            _instance_1: Experiment
            _instance_1 = _cls.from_yaml(_experiment_info_file)
            # get kwargs to bake new instance
            _kwargs = _instance_1.as_dict()
            # need to replace runner ... as loading from yaml creates new runner which we want to replace with
            # existing one so that associated_jobs property can be used properly
            _kwargs["runner"] = self.runner
            # return new instance
            return _cls(**_kwargs)
        else:
            raise e.code.CodingError(
                msgs=[f"We expect that you should have already created file "
                      f"{_experiment_info_file}"]
            )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=[
        'cwd', 'job', 'flow', 'monitor', 'registered_experiments',
        'associated_jobs', 'methods_to_be_used_in_jobs',
    ],
    things_not_to_be_overridden=['cwd', 'job', 'monitor', 'methods_to_be_used_in_jobs'],
    # we do not want any fields for Runner class
    restrict_dataclass_fields_to=[],
)
class Runner(m.HashableClass, abc.ABC):
    """
    Can use click or pyinvoke also but not bothered about it as we don't intend to
    call ourselves from cli ... todo: check and do if it is interesting

    todo: add .trash folder
      + this will move any deleted items so that recovery is possible of any
        deleted models, metrics, artifacts and tags

    todo: implement decorator `@job.JobStep` to indicate that the method can be used
      while running as job ... note that we might want to use normal methods so that
      JobRunner classes can be reused by overriding

    todo: auto understand metrics, artifacts, models, tags
      + provide standard view elements for metrics

    todo: log file viewing
      Already we are logging in file `self.storage_dir/.jog` ... read this or
      stream it to view live logs in console

    todo: Add tags supports ... it is super easy and useful [SUPER IMPORTANT]
      basically we will make a file with tag name in folder `self.storage_dir/tags`
      and the tag will have some text inside it
      Come up with `@job.Tag` decorator for methods. Also not that the tagged methods
      will then not be useful for job defined in method flow
      (add that check in `run_flow._tuple_2_job` local method)
      Some features:
      + With tags users can communicate with jobs from client
          Like kill job, delete job, migrate data to cloud
      + tags can save information about lifecycle of job ... i.e if it is started,
        how many steps are over and is it finished
      + tags can be used to store
          review comments from users
          job description ...

    todo: add metrics support (in folder `self.storage_dir/metrics`)

    todo: add artifacts support (in folder `self.storage_dir/artifacts`)

    todo: add models support (in folder `self.storage_dir/models`)
    """

    @property
    def py_script(self) -> str:
        return pathlib.Path(sys.argv[0]).name

    @property
    @util.CacheResult
    def monitor(self) -> Monitor:
        return Monitor(runner=self)

    @property
    @util.CacheResult
    def associated_jobs(self) -> t.Dict[t.Callable, Job]:
        _methods = self.methods_to_be_used_in_jobs()["runner"]
        return {
            _m: Job(method=_m, runner=self, experiment=None) for _m in _methods
        }

    @property
    @util.CacheResult
    def cwd(self) -> s.Path:
        """
        todo: adapt code so that the cwd can be on any other file system instead of CWD
        """
        import pathlib
        _py_script = self.py_script
        _folder_name = _py_script.replace(".py", "")
        _ret = s.Path(suffix_path=_folder_name, fs_name='CWD')
        e.code.AssertError(
            value1=_ret.local_path.as_posix(),
            value2=(pathlib.Path(_py_script).parent / _folder_name).as_posix(),
            msgs=[
                f"Something unexpected ... the cwd for job runner is "
                f"{pathlib.Path.cwd() / _folder_name}",
                f"While the accompanying script is at "
                f"{pathlib.Path(_py_script).as_posix()}",
                f"Please debug ..."
            ]
        ).raise_if_failed()
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    @abc.abstractmethod
    def flow(self) -> Flow:
        ...

    @property
    def is_on_main_machine(self) -> bool:
        return len(sys.argv) == 1

    @property
    @util.CacheResult
    def job(self) -> Job:
        return Job.from_cli(runner=self)

    @property
    @util.CacheResult
    def registered_experiments(self) -> t.List["Experiment"]:
        return []

    def init_validate(self):
        # call super
        super().init_validate()

        # call this property to test class methods
        _ = self.methods_to_be_used_in_jobs()

    def init(self):
        # call super
        super().init()

        # setup logger
        import logging
        import pathlib
        # note that this should always be local ... dont use `self.cwd`
        _log_file = pathlib.Path(self.py_script.replace(".py", "")) / "runner.log"
        _log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.setup_logging(
            propagate=False,
            level=logging.NOTSET,
            handlers=[
                # logger.get_rich_handler(),
                # logger.get_stream_handler(),
                logger.get_file_handler(_log_file),
            ],
        )

    @util.CacheResult
    def methods_to_be_used_in_jobs(self) -> t.Dict[str, t.List[types.MethodType]]:
        # ------------------------------------------------------- 01
        # container to return
        _ret = {'runner': [], 'experiment': []}
        # methods to skip
        _methods_to_skip = [
            self.run, self.view, self.methods_to_be_used_in_jobs
        ]
        # attrs to ignore that come from parent class
        _hashable_class_attrs = dir(m.HashableClass)
        # other vars
        _cls = self.__class__

        # ------------------------------------------------------- 02
        # test fn signature
        # loop over attributes ... to find eligible methods for job
        for _attr in [_ for _ in dir(_cls) if _ not in _hashable_class_attrs]:

            # --------------------------------------------------- 02.01
            # get cls attr value
            _cls_val = getattr(_cls, _attr)

            # --------------------------------------------------- 02.02
            # if not method skip
            if not inspect.isfunction(_cls_val):
                continue

            # --------------------------------------------------- 02.03
            # ignore some special methods
            _val = getattr(self, _attr)
            if _val in _methods_to_skip:
                continue

            # --------------------------------------------------- 02.04
            # get signature
            _signature = inspect.signature(_cls_val)
            _parameter_keys = list(_signature.parameters.keys())

            # --------------------------------------------------- 02.05
            # you must have self
            if "self" not in _parameter_keys:
                raise e.code.CodingError(
                    msgs=[
                        f"Any method defined in class {_cls} is used for job ... ",
                        f"So we expect it to have `self` i.e., it should be instance method",
                        f"If you are using anything special either make it private with `_` or "
                        f"update code in {self.methods_to_be_used_in_jobs} to skip it ..."
                    ]
                )

            # --------------------------------------------------- 02.06
            # if no other kwarg it's okay
            if len(_parameter_keys) == 1:
                _ret["runner"].append(_val)
            # if two keys then second kwarg must be "experiment"
            elif len(_parameter_keys) == 2:
                if _parameter_keys[1] != "experiment":
                    raise e.code.CodingError(
                        msgs=[
                            f"Any method defined in class {_cls} can be used for job ... ",
                            f"So if you are specifying any kwarg then it can only be `experiment` of type {Experiment}",
                            f"Found {_parameter_keys[1]}"
                        ]
                    )
                _ret["experiment"].append(_val)
            else:
                raise e.code.CodingError(
                    msgs=[
                        f"Any method defined in class {_cls} can be used for job ... ",
                        "We only restrict you to have one or no kwarg ... and if one kwarg is supplied "
                        "then it can be only named `experiment`",
                        f"Check signature for {_cls_val}"
                    ]
                )

        # ------------------------------------------------------- 03
        # return
        return _ret

    def run(self, cluster_type: JobRunnerClusterType):
        if self.is_on_main_machine:
            self.flow(cluster_type)
        else:
            self.job(cluster_type)

    def view(self):
        # ---------------------------------------------------------------- 01
        # if command line args exist then may be you requested job to from within UI on your local machine,
        # so we run job locally
        if not self.is_on_main_machine:
            return self.job(JobRunnerClusterType.local)

        # ---------------------------------------------------------------- 02
        # define dashboard
        from . import gui

        @dataclasses.dataclass
        class ShowFlowStatusCallback(gui.callback.Callback):

            def fn(_self, sender: gui.widget.Widget):
                _window = gui.window.Window(
                    label="Job Flow Status", width=600, height=700, pos=(250, 250),
                )
                with _window:
                    self.flow.status_text()
                _dashboard.add_window(window=_window)

        @dataclasses.dataclass
        class RunnerDashboard(gui.dashboard.BasicDashboard):
            theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()
            title_text: gui.widget.Text = gui.widget.Text(default_value=f"Flow for {self.py_script}")
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

        # ---------------------------------------------------------------- 04
        # register jobs for runner
        def _j_view(_j: Job) -> gui.widget.Widget:
            return _j.view()
        for _method, _job in self.associated_jobs.items():
            _dashboard.runner_jobs_view.register(
                key=_method.__name__, gui_name=_method.__name__,
                fn=_j_view,
                fn_kwargs={"_j": _job}
            )

        # ---------------------------------------------------------------- 04
        # add experiments
        for _experiment in self.registered_experiments:
            _dashboard.experiment_view.add(
                hashable=_experiment,
            )

        # ---------------------------------------------------------------- 05
        # run
        gui.Engine.run(_dashboard)

    def setup(self):
        _exps = self.registered_experiments
        _rp = self.richy_panel
        for _exp in _rp.track(sequence=_exps, task_name=f"setup {len(_exps)} experiments"):
            with _exp(richy_panel=_rp):
                ...


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=["associated_jobs"],
)
class Experiment(m.HashableClass, abc.ABC):
    """
    Check `Job.path` ... define group_by to create nested folders. Also, instances of different Experiment classes can
    be stored in same folder hierarchy if some portion of first strs of group_by matches...
    """

    # runner
    runner: Runner

    @property
    @util.CacheResult
    def associated_jobs(self) -> t.Dict[t.Callable, Job]:
        _runner = self.runner
        _methods = _runner.methods_to_be_used_in_jobs()["experiment"]
        return {
            _m: Job(method=_m, runner=_runner, experiment=self) for _m in _methods
        }

    @property
    def view_gui_label(self) -> str:
        return f"{self.__class__.__module__}:{self.hex_hash[:10]}"

    @property
    def view_callable_names(self) -> t.List[str]:
        _ret = self.methods_to_be_used_in_gui_form()
        # skip info_widget as that is controlled by `Experiment.view()` method
        # Skip view as that makes the main form in which the remaining methods are shown
        return [_ for _ in _ret if _ not in ["info_widget", "view"]]

    def init(self):
        # ------------------------------------------------------------------ 01
        # call super
        super().init()

        # ------------------------------------------------------------------ 02
        # register self to runner
        self.runner.registered_experiments.append(self)

        # ------------------------------------------------------------------ 03
        # make sure that it is not s.StorageHashable or any of its fields are
        # not s.StorageHashable
        # Very much necessary check as we are interested in having some Hashable for tracking jobs and not to
        # use with storage ... this will avoid creating files/folders and doing any IO
        # todo: we disable this as now instance creation of StorageHashable's do not cause IO
        #   confirm this behaviour and delete this code .... the check is commented for now as we
        #   want to allow StorageHashable's to work example with
        #   `experiment/downloads.py` and `experiment/prepared_datas.py`
        # self.check_for_storage_hashable(
        #     field_key=f"{self.experiment.__class__.__name__}"
        # )

        # ------------------------------------------------------------------ 04
        # make <hex_hash>.info if not present
        self.runner.monitor.make_experiment_info_file(experiment=self)

    @UseMethodInForm(label_fmt="Job's")
    def associated_jobs_view(self) -> "gui.widget.Group":
        from . import gui
        _ret = gui.widget.Group()
        with _ret:
            _jobs = self.associated_jobs
            if bool(_jobs):
                for _k, _j in _jobs.items():
                    gui.widget.Separator()
                    _j.tag_manager.view()
            else:
                gui.widget.Text(default_value="There are no jobs for this experiment ...")
        return _ret

    @UseMethodInForm(label_fmt="view_gui_label")
    def view(self) -> "gui.form.HashableMethodsRunnerForm":
        from . import gui
        return gui.form.HashableMethodsRunnerForm(
            title=self.view_gui_label.split("\n")[0],
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=self.view_callable_names,
            collapsing_header_open=True,
            allow_refresh=True,
        )
