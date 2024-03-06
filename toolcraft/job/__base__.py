"""
todo: deprecate in favour of dapr module
"""
import abc
import datetime
import os
import inspect
import pathlib
import socket
import typing as t
import dataclasses
import subprocess
import itertools
import warnings

import yaml
import sys
import asyncio
import types

if False:
    import tensorflow as tf
    from tensorflow.python.training.tracking import util as tf_util

from .. import logger
from .. import error as e
from .. import marshalling as m
from .. import util
from .. import storage as s
from .. import richy
from .. import settings
from .. import gui

_now = datetime.datetime.now


_LOGGER = logger.get_logger()
_MONITOR_FOLDER = "monitor"


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

    def create(self, data: t.Dict[str, t.Any] = None, exception: str = None):
        if self.path.exists():
            raise e.code.CodingError(
                msgs=[f"Tag at {self.path} already exists ..."]
            )
        if data is None:
            data = {}
        for _k in ['time', 'hostname', 'ip_address']:
            if _k in data.keys():
                raise e.code.CodingError(
                    msgs=[
                        f"Do not supply key {_k} in data dict we will add it ..."
                    ]
                )
        data["time"] = _now()
        data["hostname"] = socket.gethostname()
        data["ip_address"] = socket.gethostbyname(data["hostname"])
        if exception is not None:
            # data['exception'] = "\n".join(["", ">>> EXCEPTION <<<", "", exception])
            data['exception'] = ["", ">>> EXCEPTION <<<", "", *exception.split("\n")]
        _LOGGER.info(msg=f"Creating tag {self.path}")
        _parent_dir = self.path.parent
        if not _parent_dir.exists():
            _parent_dir.mkdir(create_parents=True)
        self.path.write_yaml(data=data)

    def read(self) -> t.Optional[t.Dict[str, t.Any]]:
        if not self.path.exists():
            return None
        _LOGGER.info(msg=f"Reading tag {self.path}")
        return self.path.read_yaml()

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

    def update(self, data: t.Dict[str, t.Any], allow_overwrite: bool = False, encoding: str = 'utf-8'):
        _LOGGER.info(msg=f"Updating tag {self.path}")
        _old_data = {}
        if self.path.exists():
            _old_data = self.path.read_yaml(encoding=encoding)
        for _k in data.keys():
            if _k in _old_data.keys():
                if not allow_overwrite:
                    raise e.validation.NotAllowed(
                        msgs=[f"Cannot overwrite key {_k} in tag ..."]
                    )
        _old_data.update(data)
        self.path.write_yaml(_old_data, encoding=encoding)


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
        from .. import gui
        _ret = gui.widget.Group(horizontal=False)
        with _ret:
            with gui.widget.Group(horizontal=True):
                _show_log = True
                gui.widget.Text(default_value=f"[[[ Job: {self.job.method.__name__} ]]]")
                if _finished:
                    gui.widget.Text(default_value="--- FINISHED ---")
                elif _failed:
                    gui.widget.Text(default_value="XXX  FAILED  XXX")
                    self.job.path.delete_folder_button(label="Delete")
                elif _launched:
                    if _running:
                        gui.widget.Text(default_value="--- RUNNING  ---")
                    elif _started:
                        gui.widget.Text(default_value="--- STARTED  ---")
                    else:
                        gui.widget.Text(default_value="--- LAUNCHED ---")
                else:
                    _show_log = False
                    gui.widget.Text(default_value=">> PLEASE RUN <<")
                    gui.widget.Button(label="Run", callback=lambda: self.job.launch_as_subprocess())
                if _show_log:
                    self.job.log_file.webbrowser_open_button(label="Show Full Log")
            if _description:
                gui.widget.Text(default_value=f"\n-- description --\n {_description}")
            if _launched:
                gui.widget.Text(default_value=f"launched at: {_launched['time']}")
            if _started:
                gui.widget.Text(default_value=f"started at: {_started['time']}")
            if _running:
                gui.widget.Text(default_value=f"running from: {_running['time']}")
            if _failed:
                gui.widget.Text(default_value=f"failed at: {_failed['time']}")
                gui.widget.Text(default_value="\n".join(_failed['exception']))
            if _finished:
                gui.widget.Text(default_value=f"finished at: {_finished['time']}")

        # ----------------------------------------------------------------- 03
        # return
        return _ret


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
        from .. import gui
        _bt = gui.BlockingTask(
            fn=self.blocking_fn,
            # todo: making this false raises pickling error as the blocking task is run in different thread
            #    we need to investigate if we want to fix this
            concurrent=True
        )
        _bt.add_to_task_queue()
        return _bt

    async def awaitable_fn(self, receiver_grp: "gui.widget.Group"):
        from ..gui.widget import Text
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
        from .. import gui

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


@dataclasses.dataclass
class JobLaunchParameters:

    # Set this if you want to receive email after lsf job completion.
    lsf_email: bool = False
    # Number of processors to use for lsf job.
    lsf_cpus: int = None
    # Amount of memory in MB to reserve for lsf job.
    lsf_memory: int = None

    def __setattr__(self, key, value):
        # test for lsf parameters
        if key.startswith("lsf_"):
            if not settings.IS_LSF:
                raise e.code.CodingError(
                    msgs=["Do not try to set LSF launch parameters as this is not LSF environment."]
                )

        # check if value is set multiple times
        # noinspection PyUnresolvedReferences,DuplicatedCode
        _default_value = self.__class__.__dataclass_fields__[key].default
        _current_value = getattr(self, key)
        # this means incoming value is not default
        if _default_value != value:
            # this means that current value is already updated
            if _current_value != _default_value:
                raise e.code.CodingError(
                    msgs=[f"The launch parameter {key} is already set to non default value {_current_value}",
                          f"You cannot update it again with new value {value}"]
                )

        # set attr
        super().__setattr__(key, value)


@dataclasses.dataclass
class JobOsEnvVars:

    IS_ON_SINGLE_CPU: bool = False
    IS_LSF_JOB: bool = False
    IS_LOCAL_JOB: bool = False

    def __post_init__(self):
        for _f in dataclasses.fields(self):
            if not _f.name.isupper():
                raise e.code.CodingError(
                    msgs=[f"All the fields in this class must be upper case. Found {_f.name} !!!"]
                )


    def __setattr__(self, key, value):
        # ------------------------------------------- 01
        # validation
        # ------------------------------------------- 01.01
        # check IS_ON_SINGLE_CPU
        if key == 'IS_ON_SINGLE_CPU':
            if settings.IS_LSF and value:
                raise e.code.CodingError(
                    msgs=["You cannot set IS_ON_SINGLE_CPU on LSF platform to True"]
                )
        # ------------------------------------------- 01.02
        # check IS_LSF_JOB
        if key == 'IS_LSF_JOB':
            if getattr(self, 'IS_LOCAL_JOB'):
                raise e.code.CodingError(
                    msgs=["You cannot set IS_LSF_JOB as you have already set IS_LOCAL_JOB"]
                )
        # ------------------------------------------- 01.03
        # check IS_LSF_JOB
        if key == 'IS_LOCAL_JOB':
            if getattr(self, 'IS_LSF_JOB'):
                raise e.code.CodingError(
                    msgs=["You cannot set IS_LOCAL_JOB as you have already set IS_LSF_JOB"]
                )
        # ------------------------------------------- 01.04
        # check if value is set multiple times
        # noinspection PyUnresolvedReferences,DuplicatedCode
        _default_value = self.__class__.__dataclass_fields__[key].default
        _current_value = getattr(self, key)
        # this means incoming value is not default
        if _default_value != value:
            # this means that current value is already updated
            if _current_value != _default_value:
                raise e.code.CodingError(
                    msgs=[f"The env var {key} is already set to non default value {_current_value}",
                          f"You cannot update it again with new value {value}"]
                )

        # ------------------------------------------- 02
        super().__setattr__(key, value)

    def get_environ_dict(self) -> t.Dict[str, str]:
        _ret = {}
        for _f in dataclasses.fields(self):
            _env_name = f"TC_{_f.name}"
            if _env_name in os.environ.keys():
                raise e.code.CodingError(
                    msgs=[
                        f"The env var {_env_name} is already set to {os.environ[_env_name]}.",
                    ]
                )
            # noinspection PyUnresolvedReferences
            _default_value = self.__class__.__dataclass_fields__[_f.name].default
            _value = getattr(self, _f.name)
            if _default_value != _value:
                _ret[_env_name] = str(_value)
        return _ret

    @classmethod
    def make_instance_from_environ(cls) -> "JobOsEnvVars":
        _ret = JobOsEnvVars()
        for _f in dataclasses.fields(cls):
            _env_name = f"TC_{_f.name}"
            try:
                setattr(_ret, _f.name, eval(os.environ[_env_name]))
            except KeyError:
                ...
        return _ret





class Job:
    """
    Note that this job is available only on server i.e. to the submitted job on
    cluster ... on job launching machine access to this property will raise error

    Note this can read cli args and construct `method` and `method_kwargs` fields
    """

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
    def num_keras_tuners(self) -> int:
        return int(os.environ['TC_NUM_KERAS_TUNERS'])

    @property
    def is_on_single_cpu(self) -> bool:
        if 'launch' in sys.argv and 'local' in sys.argv and '--single-cpu' in sys.argv:
            return True
        else:
            return self.os_env_vars.IS_ON_SINGLE_CPU

    @property
    def is_lsf_job(self) -> bool:
        if 'launch' in sys.argv and 'lsf' in sys.argv:
            return True
        else:
            return self.os_env_vars.IS_LSF_JOB

    @property
    def is_local_job(self) -> bool:
        if 'launch' in sys.argv and 'local' in sys.argv:
            return True
        else:
            return self.os_env_vars.IS_LOCAL_JOB

    @property
    def is_view_job(self) -> bool:
        if 'view' in sys.argv:
            if sys.argv[1] == 'view':
                return True
            else:
                raise e.code.ShouldNeverHappen(msgs=[f"Check {sys.argv}"])

    @property
    def is_archive_job(self) -> bool:
        if 'archive' in sys.argv:
            if sys.argv[1] == 'archive':
                return True
            else:
                raise e.code.ShouldNeverHappen(msgs=[f"Check {sys.argv}"])

    @property
    def is_unfinished_job(self) -> bool:
        if 'unfinished' in sys.argv:
            if sys.argv[1] == 'unfinished':
                return True
            else:
                raise e.code.ShouldNeverHappen(msgs=[f"Check {sys.argv}"])

    @property
    def is_failed_job(self) -> bool:
        if 'failed' in sys.argv:
            if sys.argv[1] == 'failed':
                return True
            else:
                raise e.code.ShouldNeverHappen(msgs=[f"Check {sys.argv}"])

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
        return self.tag_manager.failed.exists()

    @property
    def short_name(self) -> str:
        _job_id = self.job_id[:-20] + "..."
        if self.experiment is None:
            return f"runner:{self.method.__name__}"
        else:
            _exp_short = self.experiment.hex_hash
            _exp_short = f"{_exp_short[:4]}...{_exp_short[-4:]}"
            return ":".join(self.experiment.group_by + [_exp_short, self.method.__name__, ])

    @property
    @util.CacheResult
    def job_id(self) -> str:
        """
        Note that the job is made up of three unique things namely experiment,
        method and runner.

        Note that experiment has runner as dataclass field so we really
        need not worry uniqueness of our job :) But when experiment is None we
        need to use runner hex_hash :(
        """
        _ret = self.runner.hex_hash
        if self.experiment is None:
            _ret += f':{self.method.__name__}'
        else:
            assert _ret == self.experiment.runner.hex_hash, "some coding error"
            _ret += f':{self.experiment.hex_hash}:{self.method.__name__}'
        return _ret

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
        for _j in self._wait_on_jobs:
            if isinstance(_j, Job):
                _wait_on_jobs += [_j]
            else:
                _wait_on_jobs += _j.bottom_jobs
        return _wait_on_jobs

    @property
    @util.CacheResult
    def cli_command(self) -> t.List[str]:
        _command = [
            sys.executable,
            self.runner.py_script.name,
            "run",
            self.job_id,
        ]
        return _command

    @property
    @util.CacheResult
    def os_env_vars(self) -> JobOsEnvVars:
        """
        The environment vars you want to see when job is actually running
        """
        return JobOsEnvVars.make_instance_from_environ()

    @property
    @util.CacheResult
    def launch_parameters(self) -> JobLaunchParameters:
        """
        The parameters that can be accessed when job is launched from main machine
        """
        return JobLaunchParameters()

    @property
    def kwargs(self) -> t.Optional[t.Dict]:
        """
        the container that stores kwargs that can be consumed by self.method

        Container to that you can call job with kwargs
        Note that the kwargs do not alter hash so use carefully
        while when we call we will save the kwargs used in launched tag for future reference
        """
        try:
            # noinspection PyUnresolvedReferences
            return self._kwargs
        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._kwargs = None
            return self._kwargs

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
        _ret = self.runner.results_dir
        _ret /= self.method.__func__.__name__
        if bool(self.experiment):
            for _ in self.experiment.group_by:
                _ret /= _
            _ret /= self.experiment.hex_hash
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    def log_file(self) -> s.Path:
        return self.path / "toolcraft.log"

    def __init__(
        self,
        runner: "Runner",
        method: t.Callable,
        experiment: t.Optional["Experiment"] = None,
    ):

        # ------------------------------------------------------------------ 01
        # validations
        # ------------------------------------------------------------------ 01.01
        # check if method supplied is available in runner
        if experiment is None:
            e.validation.ShouldBeOneOf(
                value=method, values=runner.methods_that_can_be_used_by_jobs(),
                msgs=[
                    f"Method {method} is not recognized as a method that can be used with runner level Job's"
                ]
            ).raise_if_failed()
        else:
            e.validation.ShouldBeOneOf(
                value=method, values=experiment.methods_that_can_be_used_by_jobs(),
                msgs=[
                    f"Method {method} is not recognized as a method that can be used with experiment level Job's"
                ]
            ).raise_if_failed()
        # ------------------------------------------------------------------ 01.02
        # check environments
        if self.is_lsf_job:
            if not settings.IS_LSF:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Please run lsf job on LSF environment"
                    ]
                )
        elif self.is_local_job:
            if settings.IS_LSF:
                raise e.validation.NotAllowed(
                    msgs=[
                        "This is lsf environment and you are trying to run local job"
                    ]
                )
        elif self.is_view_job or self.is_archive_job or self.is_unfinished_job or self.is_failed_job:
            ...
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Check {sys.argv}"])
        # ------------------------------------------------------------------ 01.03
        # check single cpu
        if self.is_on_single_cpu:
            if not self.is_local_job:
                raise e.validation.NotAllowed(
                    msgs=["This is not local job so you cannot have single cpu mode"]
                )

        # ------------------------------------------------------------------ 02
        # assign some vars
        self.runner = runner
        self.experiment = experiment
        if experiment is None:
            self.method = getattr(runner, method.__name__)  # type: types.MethodType
        else:
            self.method = getattr(experiment, method.__name__)  # type: types.MethodType
        # Container to save wait_on jobs
        self._wait_on_jobs = []  # type: t.List[t.Union[Job, SequentialJobGroup, ParallelJobGroup]]

        # ------------------------------------------------------------------ 04
        # validate self.method
        _full_arg_spec = inspect.getfullargspec(self.method)
        if _full_arg_spec.args != ['self']:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Only kwargs are allowed for job method {self.method} except for arg `self`",
                    f"Invalid arg spec: {_full_arg_spec}",
                ]
            )

    def run_on_worker(self, _rp: richy.StatusPanel):

        # ------------------------------------------------------------ 01
        # reconfig logger to change log file for job
        import logging
        _log = self.log_file
        _previous_log_settings = logger.setup_logging(
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
                    "job_id": self.job_id,
                    "sys.argv": sys.argv,
                    "started": _start.ctime(),
                }
            ]
        )

        # ------------------------------------------------------------ 02
        # check if launcher client machine has created launched tag
        if not self.tag_manager.launched.exists():
            raise e.code.CodingError(
                msgs=[
                    "We expect that `launched` tag is created by client launching machine .... "
                ]
            )

        # ------------------------------------------------------------ 03
        # indicates that job is started
        self.tag_manager.started.create()

        # ------------------------------------------------------------ 04
        # indicate that job will now be running
        # also note this acts as semaphore and is deleted when job is finished
        # ... hence started tag is important
        self.tag_manager.running.create()

        # ------------------------------------------------------------ 05
        try:
            for _wj in self.wait_on_jobs:
                if not _wj.is_finished:
                    raise e.code.CodingError(
                        msgs=[f"Wait-on job with job-id "
                              f"{_wj.job_id} is supposed to be finished ..."]
                    )
            _job_kwargs = {} if self.kwargs is None else self.kwargs
            if self.experiment is None:
                self.method(**_job_kwargs)
            else:
                with self.experiment(richy_panel=_rp):
                    self.method(**_job_kwargs)
            self.tag_manager.running.delete()
            self.tag_manager.finished.create()
            _end = _now()
            _LOGGER.info(
                msg=f"Successfully finished job on worker machine ...",
                msgs=[
                    {
                        "job_id": self.job_id,
                        "started": _start.ctime(),
                        "ended": _end.ctime(),
                        "seconds": str((_end - _start).total_seconds()),
                    }
                ]
            )
        except Exception as _ex:
            import traceback
            _ex_str = traceback.format_exc()
            self.tag_manager.failed.create(exception=_ex_str)
            _end = _now()
            _LOGGER.error(
                msg=f"Failed job on worker machine ...",
                msgs=[
                    {
                        "job_id": self.job_id,
                        "started": _start.ctime(),
                        "ended": _end.ctime(),
                        "seconds": str((_end - _start).total_seconds()),
                    }
                ]
            )
            _LOGGER.error(
                msg="*** EXCEPTION MESSAGE *** \n" + _ex_str
            )
            self.tag_manager.running.delete()
            # above thing will tell toolcraft that things failed gracefully
            # while below raise will tell cluster systems like bsub that job has failed
            # todo for `JobRunnerClusterType.local_on_same_thread` this will not allow
            #  future jobs to run ... but this is expected as we want to debug in
            #  this mode mostly
            raise _ex

        # ------------------------------------------------------------ 06
        # reset back the logger handling
        logger.setup_logging(**_previous_log_settings)

    def launch_as_subprocess(
        self,
        cli_command: t.List[str] = None,
        use_current_env_vars: bool = True,
        single_cpu: bool = False,
    ):
        # ------------------------------------------------------------- 01
        # make cli command if None
        if cli_command is None:
            cli_command = self.cli_command

        # ------------------------------------------------------------- 02
        # check health
        _ret = self.check_health(is_on_main_machine=True)
        if _ret is not None:
            _LOGGER.error(msg=_ret)
            return

        # ------------------------------------------------------------- 03
        # create tag so that worker machine knows that the client has
        # launched it
        _data = None
        if bool(self.kwargs):
            _data = {'job_kwargs': self.kwargs}
        self.tag_manager.launched.create(data=_data)

        # ------------------------------------------------------------- 04
        # run in subprocess
        _env_vars = {}
        if use_current_env_vars:
            _env_vars.update(os.environ.copy())
        _env_vars.update(self.os_env_vars.get_environ_dict())
        if single_cpu:
            _sub_title = [
                self.short_name,
            ]
            if bool(self.kwargs):
                _sub_title += [f"with kwargs: {self.kwargs}"]
            with richy.StatusPanel(
                tc_log=_LOGGER,
                title=f".. running on single cpu ..",
                sub_title=_sub_title,
                log_task_progress_after=10*60,
            ) as _rp:
                self.run_on_worker(_rp=_rp)
        else:
            _ret = subprocess.run(cli_command, env=_env_vars)
        if _ret.returncode != 0:
            warnings.warn(
                f"Failed with return code `{_ret.returncode}` while calling `{cli_command}`"
            )

    def wait_on(self, wait_on: t.Union['Job', 'SequentialJobGroup', 'ParallelJobGroup']) -> "Job":
        self._wait_on_jobs.append(wait_on)
        return self

    def with_kwargs(self, _dict: dict) -> "Job":
        if self.kwargs is None:
            _full_arg_spec = inspect.getfullargspec(self.method)
            for _k in _dict.keys():
                e.validation.ShouldBeOneOf(
                    value=_k, values=_full_arg_spec.kwonlyargs,
                    msgs=[f"One of the item in dict is not valid kwarg for method {self.method}"]
                ).raise_if_failed()
            for _k in _full_arg_spec.kwonlyargs:
                if _k not in _full_arg_spec.kwonlydefaults.keys():
                    if _k not in _dict.keys():
                        raise e.validation.NotAllowed(
                            msgs=[f"Please supply mandatory kwarg {_k}"]
                        )
            # noinspection PyAttributeOutsideInit
            self._kwargs = _dict
            return self
        else:
            raise e.code.CodingError(
                msgs=["with_kwargs was already set ..."]
            )

    def check_health(self, is_on_main_machine: bool) -> t.Optional[str]:
        """
        If str is returned then skip calling job and print error message ...
        If none is returned then we need to call job
        """
        # ------------------------------------------------------------- 01
        # some vars
        _job_info = {"name": self.job_id, "py-script": self.runner.py_script, "path": self.path.full_path}
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
                        "Please fix any bugs or `clean` previous runs ...",
                        _job_info,
                    ]
                )

        # ------------------------------------------------------------- 03
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

        # ------------------------------------------------------------- 04
        # return str (i.e. finished or failed or running) so that job is not called
        if _finished:
            return "The job was already finished ..."
        if _failed:
            return "The job was already failed ... please `clean` so that you can `run` it again ..."
        if _running:
            return "There is already a job running on worker .... please kill job and/or `clean` to `run` it again ..."

        # ------------------------------------------------------------- 05
        if is_on_main_machine:
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
            return None
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
            return None

    def view(self) -> "gui.widget.Widget":
        """
        todo: Add more views like
          + artifact manager view
          + live status
          + log streams
        """
        return self.tag_manager.view()

    # noinspection PyUnresolvedReferences
    def save_tf_chkpt(self, name: str, tf_chkpt: "tf.train.Checkpoint"):
        """
        todo: make this compatible for all type of path
        """
        import tensorflow as tf
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
        import tensorflow as tf
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

        # validate
        for _j in jobs:
            if isinstance(_j, Job):
                _full_arg_spec = inspect.getfullargspec(_j.method)
                _supplied_kwargs = {} if _j.kwargs is None else _j.kwargs
                for _k in _full_arg_spec.kwonlyargs:
                    if _k not in _full_arg_spec.kwonlydefaults.keys():
                        if _k not in _supplied_kwargs.keys():
                            raise e.validation.NotAllowed(
                                msgs=[
                                    f"You need to supply mandatory kwarg {_k} for method {_j.method}",
                                    f"Please use with_kwargs method on job instance to supply kwargs ..."
                                ]
                            )

        # call init
        self.init()

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
        stages: t.Dict[str, ParallelJobGroup],
        runner: "Runner",
    ):
        # save reference
        self.stages = stages
        self.runner = runner

        # set flow ids
        _previous_stage_id = None
        for _stage_id, _stage in self.stages.items():
            if _previous_stage_id is not None:
                for _ in _stage.all_jobs:
                    _.wait_on(self.stages[_previous_stage_id])
            _previous_stage_id = _stage_id

    def status(self) -> t.Dict:
        _ret = dict()
        for _sk, _stage in self.stages.items():
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
            _ret[f"Stage {_sk}"] = dict(
                total=_total, started=_started, running=_running, finished=_finished, failed=_failed,
            )
        return _ret

    def status_text(self) -> "gui.widget.Text":
        from .. import gui
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
        _ret = self.runner.results_dir / _MONITOR_FOLDER
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

    def make_runner_info_file(self):
        _file = self.path / f"{self.runner.hex_hash}.info"
        if not _file.exists():
            _LOGGER.info(
                f"Creating runner info file {_file.local_path.as_posix()}")
            _file.write_text(self.runner.yaml())

    def make_experiment_info_file(self, experiment: "Experiment"):
        _file = self.experiments_folder_path / f"{experiment.hex_hash}.info"
        if not _file.exists():
            _LOGGER.info(
                f"Creating experiment info file {_file.local_path.as_posix()}")
            _file.write_text(experiment.yaml())

    def get_experiment_from_hex_hash(self, hex_hash: str) -> "Experiment":
        """
        Note that the experiments are present in Runner instance so we can return that.
        But sometimes you might have filtered experiments or trying some other experiments while
        commenting previous experiments while running Runner instance. In that case the experiments might still
        be on disk but current Runner instance might not be aware of it. So we will make an instance for you.
        But be aware that the runner will not know any thing about it
        """
        # ------------------------------------------------------------- 01
        # some vars
        _experiment_info_file = self.experiments_folder_path / f"{hex_hash}.info"

        # ------------------------------------------------------------- 02
        # check if current runner instance has it
        for _ in self.runner.registered_experiments.values():
            if _.hex_hash == hex_hash:
                # sanity check
                assert _experiment_info_file.exists(), "was expecting this to be present"
                return _

        # ------------------------------------------------------------- 03
        # check if there is some experiment on disk with given hex hash
        # note that this will also register this experiment with current runner instance
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

        # ------------------------------------------------------------- 04
        # raise error as there is no experiment that is monitored for his hex_hash
        raise e.code.CodingError(
            msgs=[f"We expect that you should have already created file "
                  f"{_experiment_info_file}"]
        )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=[
        'view_gui_label', 'view_gui_label_tooltip', 'view_callable_names',
        'associated_jobs'
    ],
    things_not_to_be_cached=['job'],
    things_not_to_be_overridden=['job'],
)
class _Common(m.HashableClass, abc.ABC):

    @property
    @util.CacheResult
    def view_gui_label(self) -> str:
        if isinstance(self, Runner):
            return f"{self.__class__.__module__}.{self.__class__.__name__}"
        elif isinstance(self, Experiment):
            return f"{self.__class__.__module__}:{self.mini_hex_hash}"
        else:
            raise e.code.ShouldNeverHappen(msgs=[])

    @property
    @util.CacheResult
    def view_gui_label_tooltip(self) -> str:
        return f"Hex Hash: {self.hex_hash}\n\n{self.yaml()}"

    @property
    @util.CacheResult
    def view_callable_names(self) -> t.List[str]:
        _ret = self.methods_to_be_used_in_gui_form()
        # skip info_widget as that is controlled by `Experiment.view()` method
        # Skip view as that makes the main form in which the remaining methods are shown
        _ret = [_ for _ in _ret if _ not in ["info_widget", "view"]]
        return _ret

    @property
    @util.CacheResult
    def associated_jobs(self) -> t.Dict[t.Callable, Job]:
        if isinstance(self, Runner):
            return {
                _m: Job(method=_m, runner=self, experiment=None)
                for _m in self.methods_that_can_be_used_by_jobs()
            }
        elif isinstance(self, Experiment):
            return {
                _m: Job(method=_m, runner=self.runner, experiment=self)
                for _m in self.methods_that_can_be_used_by_jobs()
            }
        else:
            raise e.code.ShouldNeverHappen(msgs=[])

    @property
    def job(self) -> Job:
        """
        Shortcut for
        self.associated_jobs[<caller class fn>]
        """

        _caller_name = inspect.stack()[1][3]

        for _k, _v in self.associated_jobs.items():
            if _k.__name__ == _caller_name:
                return _v

        raise e.code.CodingError(
            msgs=[
                f"You have called from method {_caller_name} which is not "
                f"supported by associated jobs ..."
            ]
        )

    @classmethod
    def methods_that_can_be_used_by_jobs(cls) -> t.List[t.Callable]:
        # ------------------------------------------------------ 01
        # act based on type
        if issubclass(cls, Experiment):
            _methods_to_skip = [
                cls.methods_that_can_be_used_by_jobs,
            ]
        elif issubclass(cls, Runner):
            _methods_to_skip = [
                cls.methods_that_can_be_used_by_jobs,
                cls.run,
                cls.get_job_from_cli_run_arg,
            ]
        else:
            raise e.code.ShouldNeverHappen(msgs=[])

        # ------------------------------------------------------ 02
        # some vars
        # attrs to ignore that come from parent class
        _hashable_class_attrs = dir(m.HashableClass)
        _gui_form_methods = cls.methods_to_be_used_in_gui_form()

        # ------------------------------------------------------ 03
        # Loop
        _ret = []
        for _attr in [_ for _ in dir(cls)]:
            # -------------------------------------------------- 03.01
            # ignore things from parent
            if _attr in _hashable_class_attrs:
                continue
            # ignore private things
            if _attr.startswith("_"):
                continue
            # ignore _gui_form_methods
            if _attr in _gui_form_methods:
                continue

            # -------------------------------------------------- 03.02
            # get value
            _value = getattr(cls, _attr)

            # -------------------------------------------------- 03.03
            # if not method skip
            if not inspect.isfunction(_value):
                continue

            # -------------------------------------------------- 03.04
            # ignore some special methods
            if _value in _methods_to_skip:
                continue

            # -------------------------------------------------- 03.05
            # get signature
            _full_arg_spec = inspect.getfullargspec(_value)
            _signature = inspect.signature(_value)
            _parameter_keys = list(_signature.parameters.keys())

            # -------------------------------------------------- 03.06
            # you must have self
            if _full_arg_spec.args[0] != 'self':
                raise e.code.CodingError(
                    msgs=[
                        f"Any method defined in class {cls} is used for job ... ",
                        f"So we expect it to have `self` i.e., it should be instance method",
                        f"If you are using anything special either make it private with `_` or "
                        f"update list `_methods_to_skip` above to skip it ..."
                    ]
                )
            if len(_full_arg_spec.args) > 1:
                raise e.code.CodingError(
                    msgs=[
                        "You are not allowed to use args ... only kwargs are "
                        "allowed used special * notation to use kwargs"
                    ]
                )

            # -------------------------------------------------- 03.07
            # if no other arg it's okay .... note that we allow kwargs
            _ret.append(_value)

        # ------------------------------------------------------ 04
        # return
        return _ret

    @gui.UseMethodInForm(label_fmt="view_gui_label", hide_previously_opened=False, tooltip="view_gui_label_tooltip")
    def view(self) -> "gui.form.HashableMethodsRunnerForm":
        from .. import gui
        if isinstance(self, Experiment):
            return gui.form.HashableMethodsRunnerForm(
                label=self.view_gui_label.split("\n")[0],
                hashable=self,
                close_button=True,
                info_button=True,
                callable_names=self.view_callable_names,
                default_open=True,
            )
        elif isinstance(self, Runner):
            return gui.form.HashableMethodsRunnerForm(
                label=self.view_gui_label.split("\n")[0],
                hashable=self,
                close_button=False,
                info_button=True,
                callable_names=self.view_callable_names,
                default_open=True,
            )
        else:
            raise e.code.ShouldNeverHappen(msgs=[])

    @gui.UseMethodInForm(label_fmt="Job's")
    def associated_jobs_view(self) -> "gui.widget.Widget":
        from .. import gui
        _jobs = self.associated_jobs
        if isinstance(self, Runner):
            _type = "runner"
        elif isinstance(self, Experiment):
            _type = "experiment"
        else:
            raise e.code.ShouldNeverHappen(msgs=[])
        if bool(_jobs):
            _form = gui.form.ButtonBarForm(
                label=f"Jobs for this {_type} ...",
                default_open=True,
            )
            for _k, _j in _jobs.items():
                _form.register(
                    key=_k.__name__, fn=lambda _j=_j: _j.view()
                )
            return _form
        else:
            return gui.widget.Text(
                default_value=f"There are no jobs for this {_type} ...")


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=[],
)
class Experiment(_Common, abc.ABC):
    """
    Check `Job.path` ... define group_by to create nested folders. Also, instances of different Experiment classes can
    be stored in same folder hierarchy if some portion of first strs of group_by matches...

    todo: support tensorboard
      https://www.tensorflow.org/tensorboard/get_started
    todo: support tensorboard.dev
      https://tensorboard.dev/experiments/
    todo: tensorboard projector any common methods
      https://www.tensorflow.org/tensorboard/tensorboard_projector_plugin
    """

    # runner
    runner: "Runner"

    def init(self):
        # ------------------------------------------------------------------ 01
        # call super
        super().init()

        # ------------------------------------------------------------------ 02
        # register self to runner
        self.runner.registered_experiments[self.hex_hash] = self

        # ------------------------------------------------------------------ 03
        # Make sure that it is not s.StorageHashable or any of its fields are not s.StorageHashable
        # Very much necessary check as we are interested in having some Hashable for tracking jobs and not to
        #   use with storage ...
        # This will avoid creating files/folders and doing any IO
        # todo: we disable this as now instance creation of StorageHashable's do not cause IO
        #   confirm this behaviour and delete this code .... the check is commented for now as we
        #   want to allow StorageHashable's to work example with `experiment/downloads.py`
        #   and `experiment/prepared_datas.py`
        # self.check_for_storage_hashable(
        #     field_key=f"{self.experiment.__class__.__name__}"
        # )

        # ------------------------------------------------------------------ 04
        # make <hex_hash>.info for experiment if not present
        self.runner.monitor.make_experiment_info_file(experiment=self)


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=[
        'cwd', 'results_dir', 'flow', 'monitor', 'registered_experiments',
    ],
    things_not_to_be_overridden=['cwd', 'results_dir', 'py_script', 'monitor'],
    # we do not want any fields for Runner class
    restrict_dataclass_fields_to=[],
)
class Runner(_Common, abc.ABC):
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
    def py_script(self) -> pathlib.Path:
        return pathlib.Path(sys.argv[0])

    @property
    @util.CacheResult
    def monitor(self) -> Monitor:
        return Monitor(runner=self)

    @property
    def copy_src_dst(self) -> t.Tuple[str, str]:
        raise e.code.NotYetImplemented(
            msgs=["Cannot use copy cli command", "Please implement property copy_src_dst to use copy cli command"]
        )

    @property
    @util.CacheResult
    def results_dir(self) -> s.Path:
        """
        results dir where results will be stored for this runner
        """
        _py_script = self.py_script
        _folder_name = _py_script.name.replace(".py", "")
        _folder_name += f"_{self.hex_hash[:5]}"
        _ret = s.Path(suffix_path=_folder_name, fs_name='RESULTS')
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    @property
    @util.CacheResult
    def cwd(self) -> s.Path:
        """
        todo: adapt code so that the cwd can be on any other file system instead of CWD
        """
        _py_script = self.py_script
        _ret = s.Path(suffix_path=".", fs_name='CWD')
        e.code.AssertError(
            value1=_ret.local_path.absolute().as_posix(),
            value2=_py_script.parent.absolute().as_posix(),
            msgs=[
                f"This is unexpected ... ",
                f"The cwd for job runner is {_ret.local_path.absolute().as_posix()}",
                f"While the accompanying script is at {_py_script.as_posix()}",
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
    @util.CacheResult
    def registered_experiments(self) -> t.Dict[str, "Experiment"]:
        return dict()

    def init(self):
        # call super
        super().init()

        # setup logger
        import logging
        # note that this should always be local ... dont use `self.cwd`
        _log_file = self.results_dir / "runner.log"
        logger.setup_logging(
            propagate=False,
            level=logging.NOTSET,
            handlers=[
                # logger.get_rich_handler(),
                # logger.get_stream_handler(),
                logger.get_file_handler(_log_file.local_path),
            ],
        )

        # call property flow .... so that some experiments dynamically added to flow are available to Runner
        _ = self.flow

        # make <hex_hash>.info for runner if not present
        self.monitor.make_runner_info_file()

    def get_job_from_cli_run_arg(self, job: str) -> Job:
        # ------------------------------------------------------------ 01
        # read args and validate
        _split_strs = job.split(":")
        if len(_split_strs) in [2, 3]:
            # -------------------------------------------------------- 01.01
            # the runner hash should always match
            e.code.AssertError(
                value1=_split_strs[0], value2=self.hex_hash,
                msgs=[
                    "The runner used is not exactly same"
                ]
            ).raise_if_failed()
            # -------------------------------------------------------- 01.02
            if len(_split_strs) == 2:
                _method = getattr(self.__class__, _split_strs[1])
                return self.associated_jobs[_method]
            else:
                _experiment = self.monitor.get_experiment_from_hex_hash(hex_hash=_split_strs[1])
                _method = getattr(_experiment.__class__, _split_strs[2])
                return _experiment.associated_jobs[_method]
        else:
            raise e.code.CodingError(
                msgs=[
                    "The job str should have format "
                    "<runner-hex-hash:method-name> or <runner-hex-hash:experi-hex-hash:method-name>",
                    f"Found unknown str {job}"
                ]
            )

    def run(self):
        from . import cli

        # make sub_title
        _sub_title = None
        if len(sys.argv) > 1:
            _sub_title = [f"command: {sys.argv[1]}"]
            if sys.argv[1] == "run":
                # this means the arg represent a job
                _job = self.get_job_from_cli_run_arg(job=sys.argv[2])
                _sub_title += [_job.short_name]
                if bool(_job.kwargs):
                    _sub_title += [f"with kwargs: {_job.kwargs}"]
            else:
                if bool(sys.argv[2:]):
                    _sub_title += [f"cli args: {sys.argv[2:]}"]

        # launch
        with richy.StatusPanel(
            tc_log=_LOGGER,
            title=f"Running for py_script: {self.py_script.name!r}",
            sub_title=_sub_title,
            log_task_progress_after=10*60,
        ) as _rp:
            with self(richy_panel=_rp):
                cli.get_app(runner=self)()

    def setup(self):
        _exps = self.registered_experiments
        _rp = self.richy_panel
        for _exp in _rp.track(
            sequence=_exps.values(), task_name=f"setup {len(_exps)} experiments",
        ):
            with _exp(richy_panel=_rp):
                ...
