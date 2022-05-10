"""
todo: deprecate in favour of dapr module
"""
import abc
import datetime
import enum
import inspect
import typing as t
import dataclasses
import subprocess
import yaml
import sys
import pickle
import hashlib
import types

from . import logger
from . import error as e
from . import marshalling as m
from . import util
from . import storage as s
from . import richy

try:
    import tensorflow as tf
    from tensorflow.python.training.tracking import util as tf_util
except ImportError:
    tf = None
    tf_util = None


_LOGGER = logger.get_logger()
_MONITOR_FOLDER = "monitor"
_EXPERIMENT_KWARG = "experiment"


@dataclasses.dataclass
class Viewer:
    runner: "Runner"
    fn: t.Callable
    fn_kwargs: t.Dict


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
        data["time"] = datetime.datetime.now()
        _LOGGER.info(msg=f"Creating tag {self.path}")
        self.path.write_text(text=yaml.safe_dump(data))

    def read(self) -> t.Dict[str, t.Any]:
        if not self.path.exists():
            raise e.code.CodingError(
                msgs=[f"Tag at {self.path} does not exist ..."]
            )
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
    todo: we might want these tags to be save state on some state server ...
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
    def artifacts_path(self) -> s.Path:
        _ret = self.path / "artifacts"
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
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
        for _j in self.wait_on:
            if isinstance(_j, Job):
                _wait_on_jobs += [_j]
            else:
                _wait_on_jobs += _j.bottom_jobs
        return _wait_on_jobs

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        """
        Note that folder nesting is dependent on `self.fn` signature ...

        todo: integrate this with storage with partition_columns ...
          note that first pivot will then be experiment name ...
        """
        _ret = self.runner.cwd
        _ret /= self.method.__func__.__name__
        for _key in inspect.signature(self.method).parameters.keys():
            _value = self.method_kwargs[_key]
            if _key == _EXPERIMENT_KWARG:
                _ret /= _value.hex_hash
            else:
                _ret /= str(_value)
        if not _ret.exists():
            _ret.mkdir(create_parents=True)
        return _ret

    def __init__(
        self,
        runner: "Runner",
        method: t.Callable,
        method_kwargs: t.Dict[str, t.Union["Experiment", int, float, str]] = None,
        wait_on: t.List[t.Union["Job", "SequentialJobGroup", "ParallelJobGroup"]] = None,
    ):
        # assign some vars
        self.runner = runner
        # noinspection PyTypeChecker
        self.method = method  # type: types.MethodType
        self.method_kwargs = method_kwargs or {}
        self.wait_on = wait_on or []  # type: t.List[t.Union[Job, SequentialJobGroup, ParallelJobGroup]]
        # noinspection PyTypeChecker
        self._flow_id = None  # type: str

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

        # make sure that all kwargs are supplied
        _required_keys = list(inspect.signature(self.method).parameters.keys())
        _required_keys.sort()
        _provided_keys = list(self.method_kwargs.keys())
        _provided_keys.sort()
        if _required_keys != _provided_keys:
            raise e.code.CodingError(
                msgs=[
                    f"We expect method_kwargs has all keys required by method "
                    f"{self.method} ",
                    f"Also so not supply any extra kwargs ...",
                    dict(
                        _required_keys=_required_keys, _provided_keys=_provided_keys
                    ),
                ]
            )

        # some special methods cannot be used for job
        # noinspection PyUnresolvedReferences
        e.validation.ShouldNotBeOneOf(
            value=method.__func__, values=runner.methods_that_cannot_be_a_job(),
            msgs=["Some special methods cannot be used as job ..."]
        ).raise_if_failed()

        # if _EXPERIMENT_KWARG present
        if _EXPERIMENT_KWARG in self.method_kwargs.keys():
            # get
            _experiment = self.method_kwargs[_EXPERIMENT_KWARG]
            # make sure that it is not s.StorageHashable or any of its fields are
            # not s.StorageHashable
            _experiment.check_for_storage_hashable(
                field_key=f"{_experiment.__class__.__name__}"
            )
            # make <hex_hash>.info if not present
            self.runner.monitor.make_experiment_info_file(experiment=_experiment)

    def __call__(self, cluster_type: JobRunnerClusterType):
        # check health
        self.check_health()

        # if finished or failed earlier return
        # Note that we already log error or info if lob is finished or failed in
        # above call to check_health
        if self.is_finished or self.is_failed:
            return

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
        _start = datetime.datetime.now()
        _LOGGER.info(
            msg=f"Starting job on worker machine ...",
            msgs=[
                {
                    "flow-id": self.flow_id,
                    "job-id": self.job_id,
                    "started": _start.ctime(),
                }
            ]
        )
        self.tag_manager.started.create()
        self.tag_manager.running.create()
        _failed = False
        try:
            for _wj in self.wait_on_jobs:
                if not _wj.is_finished:
                    raise e.code.CodingError(
                        msgs=[f"Wait-on job with flow-id {_wj.flow_id} and job-id "
                              f"{_wj.job_id} is supposed to be finished ..."]
                    )
            self.method(**self.method_kwargs)
            self.tag_manager.running.delete()
            self.tag_manager.finished.create()
            _end = datetime.datetime.now()
            _LOGGER.info(
                msg=f"Successfully finished job on worker machine ...",
                msgs=[
                    {
                        "flow-id": self.flow_id,
                        "job-id": self.job_id,
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
            _end = datetime.datetime.now()
            _LOGGER.info(
                msg=f"Failed job on worker machine ...",
                msgs=[
                    {
                        "flow-id": self.flow_id,
                        "job-id": self.job_id,
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
        _kwargs_as_cli_strs = []
        for _k, _v in self.method_kwargs.items():
            if _k == _EXPERIMENT_KWARG:
                _v = _v.hex_hash
            _kwargs_as_cli_strs.append(
                f"{_k}={_v}"
            )
        _command = [
            "python", self.runner.py_script, self.method.__func__.__name__, *_kwargs_as_cli_strs
        ]

        # ------------------------------------------------------------- 02
        # launch
        # todo: might be feasible only with `local` not sure about `ibm_lsf`
        #   + figure out how `subprocess.run` kwargs can be used to pull the console rendered by subprocess i.e.
        #     things like rich ui can be grabbed and streamed
        #   + explore logger handlers with extra kwargs to grab streams using `subprocess.run`
        # ------------------------------------------------------------- 02.01
        if cluster_type is JobRunnerClusterType.local:
            subprocess.run(_command)
        # ------------------------------------------------------------- 02.03
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
                _nxdi_prefix += ["-w", f'"{_wait_on}"']
            _command = _nxdi_prefix + _command
            subprocess.run(_command)

        # ------------------------------------------------------------- 02.04
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[f"Unsupported cluster_type {cluster_type}"]
            )

        # ------------------------------------------------------------- 03
        # log
        _LOGGER.info(
            msg=f"Launching jobs from main machine with below command...",
            msgs=[_command]
        )

    @classmethod
    def from_cli(
        cls,
        runner: "Runner",
    ) -> "Job":
        # test if running on machines that execute jobs ...
        if runner.is_on_main_machine:
            raise e.code.CodingError(
                msgs=[
                    "This call is available only for jobs submitted to server ... "
                    "it cannot be accessed by instance which launches jobs ..."
                ]
            )

        # fetch from args
        _method_name = sys.argv[1]
        _method = getattr(runner, _method_name)
        _method_signature = inspect.signature(_method)
        _method_kwargs = {}
        for _arg in sys.argv[2:]:
            _key, _str_val = _arg.split("=")
            if _key == _EXPERIMENT_KWARG:
                _val = runner.monitor.get_experiment_from_hex_hash(hex_hash=_str_val)
            else:
                _val = _method_signature.parameters[_key].annotation(_str_val)
            _method_kwargs[_key] = _val

        # search job from runner.flow
        _search_job = None
        for _stage in runner.flow.stages:
            for _j in _stage.all_jobs:
                if _j.method == _method and _j.method_kwargs == _method_kwargs and _j.runner == runner:
                    if _search_job is not None:
                        raise e.code.CodingError(
                            msgs=[
                                "Multiple jobs match for the given cli kwargs"
                            ]
                        )
                    _search_job = _j

        # if no job found raise
        if _search_job is None:
            raise e.code.ShouldNeverHappen(
                msgs=["We expect to find a matching job ..."]
            )

        # return
        return _search_job

    def check_health(self):
        # if job has already started
        _job_info = {"flow-id": self.flow_id, "job-id": self.job_id, "path": self.path.full_path}
        if self.is_started:
            # if job was finished then skip
            if self.is_finished:
                _LOGGER.info(
                    msg=f"Job is already completed so skipping call ...",
                    msgs=[_job_info]
                )
                return
            if self.is_failed:
                _LOGGER.error(
                    msg=f"Previous job has failed so skipping call ...",
                    msgs=["Delete previous calls files to make this call work ...",
                          _job_info]
                )
                return
            if self.is_running:
                raise e.code.CodingError(
                    msgs=[
                        "This is bug ... there is ongoing job running ...",
                        "Either you have abruptly killed previous jobs or you "
                        "have run same job multiple times ...",
                        "Also teh job might have failed and you missed to catch "
                        "exception and set failed tag appropriately ... in that case "
                        "check logs",
                        _job_info,
                    ]
                )
        else:
            # if started tag does not exist then other tags should not exist
            if self.is_running:
                e.code.CodingError(
                    msgs=[
                        "Found tag for `running` ... we expect it to not be present "
                        "as the job was never started",
                        _job_info
                    ]
                )
            if self.is_finished:
                e.code.CodingError(
                    msgs=[
                        "Found tag for `finished` ... we expect it to not be present "
                        "as the job was never started",
                        _job_info
                    ]
                )
            if self.is_failed:
                e.code.CodingError(
                    msgs=[
                        "Found tag for `failed` ... we expect it to not be present "
                        "as the job was never started",
                        _job_info
                    ]
                )

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

    def save_artifact(self, name: str, data: t.Any):
        """
        todo: make this compatible for all type of path
        """
        _file = self.artifacts_path / name
        if _file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"Artifact {name} already exists ... cannot write"
                ]
            )

        with open(_file.local_path.as_posix(), 'wb') as _file:
            pickle.dump(data, _file)

    def load_artifact(self, name: str) -> t.Any:
        """
        todo: make this compatible for all type of path
        """

        _file = self.artifacts_path / name

        if not _file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"Artifact {name} does not exists ... cannot load"
                ]
            )

        with open(_file.local_path.as_posix(), 'rb') as _file:
            return pickle.load(_file)


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
            _len = len(self.jobs)
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
                _j.wait_on.append(_pj)
            else:
                for __j in _j.top_jobs:
                    __j.wait_on.append(_pj)


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
        _len = len(self.stages)
        for _stage_id, _stage in enumerate(self.stages):
            _stage.flow_id = f"#[{_stage_id:0{_len}d}]"

    def __call__(self, cluster_type: JobRunnerClusterType):
        """
        todo: we might want this to be called from client machine and submit jobs via
          ssh ... rather than using instance on cluster to launch jobs
          This will also help to have gui in dearpygui
        """
        # just check health of all jobs
        _sp = richy.ProgressStatusPanel(
            title=f"Checking health of all jobs first ...", tc_log=_LOGGER
        )
        with _sp:
            _p = _sp.progress
            _s = _sp.status
            _s.update(spinner_speed=1.0, spinner=None, status="started ...")
            _jobs = []
            for _stage in self.stages:
                _jobs += _stage.all_jobs
            _job: Job
            for _job in _p.track(
                sequence=_jobs, task_name=f"check health"
            ):
                _s.update(status=f"check health for {_job.flow_id} ...")
                _job.check_health()

        # call jobs ...
        if cluster_type is JobRunnerClusterType.local:
            # tracker containers
            _completed_jobs = []
            _all_jobs = []
            for _stage in self.stages:
                _all_jobs += _stage.all_jobs

            # loop over all jobs in flow
            for _j in _all_jobs:
                # extract wait on jobs that need to finished before calling _j
                _wait_jobs = []
                for _wo in _j.wait_on:
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
            _sp = richy.ProgressStatusPanel(
                title=f"Launch stages on `{cluster_type.name}`", tc_log=_LOGGER
            )
            with _sp:
                _p = _sp.progress
                _s = _sp.status
                _s.update(spinner_speed=1.0, spinner=None, status="started ...")
                for _stage_id, _stage in enumerate(self.stages):
                    _jobs = _stage.all_jobs
                    _job: t.Union[Job, ParallelJobGroup]
                    for _job in _p.track(
                        sequence=_jobs, task_name=f"stage {_stage_id:03d}"
                    ):
                        _s.update(
                            spinner_speed=1.0,
                            spinner=None, status=f"launching {_job.flow_id} ..."
                        )
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

    def view(self):
        # import
        from . import gui

        # define dashboard class
        @dataclasses.dataclass
        class FlowDashboard(gui.dashboard.BasicDashboard):
            theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()

            title_text: gui.widget.Text = gui.widget.Text(default_value=f"Flow for {self.runner.py_script}")

            container: gui.widget.Group = gui.widget.Group()

        # make dashboard
        _dashboard = FlowDashboard(title="Flow Dashboard")

        # add stages
        with _dashboard.container:
            for _i, _stage in enumerate(self.stages):
                gui.widget.CollapsingHeader(label=f"Stage {_i}")

        # run
        _dashboard.run()


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
            # noinspection PyTypeChecker
            return m.HashableClass.get_class(_experiment_info_file).from_yaml(
                _experiment_info_file
            )
        else:
            raise e.code.CodingError(
                msgs=[f"We expect that you should have already created file "
                      f"{_experiment_info_file}"]
            )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['cwd', 'job', 'flow', 'monitor', 'registered_experiments'],
    things_not_to_be_overridden=['cwd', 'job', 'monitor', 'get_another_job'],
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
        import pathlib
        return pathlib.Path(sys.argv[0]).name

    @property
    @util.CacheResult
    def monitor(self) -> Monitor:
        return Monitor(runner=self)

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
        if self.is_on_main_machine:
            raise e.code.CodingError(
                msgs=[
                    "This job is available only for jobs submitted to server ... "
                    "it cannot be accessed by instance which launches jobs ..."
                ]
            )
        else:
            return Job.from_cli(runner=self)

    @property
    @util.CacheResult
    def registered_experiments(self) -> t.List["Experiment"]:
        return []

    def setup(self):
        _exps = self.registered_experiments
        _LOGGER.info(
            f"Setting up {len(_exps)} experiments registered for this runner ...")
        for _exp in _exps:
            _exp.setup()

    @classmethod
    def methods_that_cannot_be_a_job(cls) -> t.List[t.Callable]:
        return [cls.run, cls.init, cls.clone, cls.get_another_job]

    def get_another_job(
        self, method: t.Callable, method_kwargs: t.Dict[str, t.Union["Experiment", int, float, str]] = None
    ):
        """
        In some cases you might want to access results from other job so this is the method for it.
        The only restriction is that the requested job must be completed ...
        """
        _job = Job(runner=self, method=method, method_kwargs=method_kwargs)
        if not _job.is_finished:
            raise e.code.CodingError(
                msgs=[
                    "The job you are requesting is not finished",
                    "Please check the `flow` as jobs that are completed can only be accessed",
                ]
            )
        return _job

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

    @classmethod
    def class_init(cls):
        # ------------------------------------------------------- 01
        # call super
        super().class_init()

        # ------------------------------------------------------- 02
        # test fn signature
        # loop over attributes
        for _attr in [_ for _ in cls.__dict__.keys() if not _.startswith("_")]:
            # --------------------------------------------------- 02.01
            # get cls attr value
            _val = getattr(cls, _attr)

            # --------------------------------------------------- 02.02
            # ignore some special methods
            if _val in cls.methods_that_cannot_be_a_job():
                continue

            # --------------------------------------------------- 02.03
            # skip if not function
            if not inspect.isfunction(_val):
                continue

            # --------------------------------------------------- 02.04
            # get signature
            _signature = inspect.signature(_val)
            _parameter_keys = list(_signature.parameters.keys())

            # --------------------------------------------------- 02.05
            # loop over parameters
            for _parameter_key in _parameter_keys:
                # ----------------------------------------------- 02.05.01
                # if _EXPERIMENT_KWARG parameter
                if _parameter_key == _EXPERIMENT_KWARG:
                    # _EXPERIMENT_KWARG must be first
                    if _EXPERIMENT_KWARG != _parameter_keys[1]:
                        raise e.validation.NotAllowed(
                            msgs=[
                                f"If using `{_EXPERIMENT_KWARG}` kwarg in function "
                                f"{_val} make sure that it is first kwarg i.e. it "
                                f"immediately follows after self"
                            ]
                        )
                    # _EXPERIMENT_KWARG annotation must be subclass of Experiment
                    # todo: sometimes sting annotations are used so they cannot be checked ... fix this
                    #   for now we bypass
                    _ann = _signature.parameters[_EXPERIMENT_KWARG].annotation
                    if not isinstance(_ann, str):
                        e.validation.ShouldBeSubclassOf(
                            value=_ann,
                            value_types=(Experiment, ),
                            msgs=[f"Was expecting annotation for kwarg "
                                  f"`{_EXPERIMENT_KWARG}` to be proper subclass"]
                        ).raise_if_failed()
                # ----------------------------------------------- 02.05.02
                # if self continue
                elif _parameter_key == "self":
                    continue
                # ----------------------------------------------- 02.05.03
                # else make sure that annotation is int, float or str ...
                else:
                    e.validation.ShouldBeSubclassOf(
                        value=_signature.parameters[_parameter_key].annotation,
                        value_types=(int, float, str),
                        msgs=["We restrict annotation types for proper "
                              "kwarg serialization so that they can be passed over "
                              "cli ... and can also determine path for storage",
                              f"Check kwarg `{_parameter_key}` defined in function "
                              f"`{cls.__name__}.{_val.__name__}`"]
                    ).raise_if_failed()

    def run(self, cluster_type: JobRunnerClusterType):
        if self.is_on_main_machine:
            self.flow(cluster_type)
        else:
            self.job(cluster_type)

    def view(self):
        self.flow.view()


@dataclasses.dataclass(frozen=True)
class Experiment(m.HashableClass):

    # runner
    runner: Runner

    def init(self):
        # call super
        super().init()

        # register self to runner
        self.runner.registered_experiments.append(self)

    def setup(self):
        _LOGGER.info(f" >> Setup experiment: {self.hex_hash}")
