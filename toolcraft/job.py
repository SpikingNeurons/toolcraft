"""
todo: deprecate in favour of dapr module
"""
import abc
import datetime
import enum
import inspect
import typing as t
import dataclasses
import os
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


_LOGGER = logger.get_logger()


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


@dataclasses.dataclass
class TagManager:
    """
    todo: support this for every job ....
    """
    job: "Job"
    started: Tag = Tag(name="started")
    failed: Tag = Tag(name="failed")
    finished: Tag = Tag(name="finished")
    description: Tag = Tag(name="description")


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
    def flow_id(self) -> JobFlowId:
        if self._flow_id is None:
            raise e.code.CodingError(
                msgs=[
                    f"This must be set by {Flow} using its items field ..."
                ]
            )
        return self._flow_id

    @flow_id.setter
    def flow_id(self, value: JobFlowId):
        if self._flow_id is None:
            self._flow_id = value
        else:
            raise e.code.CodingError(
                msgs=[f"This property is already set you cannot set it again ..."]
            )

    @property
    @util.CacheResult
    def id(self) -> str:
        """
        This takes in account
        + fn_name
        + fn_kwargs if present
        + hashable hex_hash if present
        """
        return self.path.suffix_path.replace("/", "x")

    @property
    def is_on_main_machine(self) -> bool:
        return self.runner.is_on_main_machine

    @property
    @util.CacheResult
    def path(self) -> s.Path:
        """
        Note that folder nesting is dependent on `self.fn` signature ...

        todo: integrate this with storage with partition_columns ...
          note that first pivot will then be hashable name ...
        """
        _ret = self.runner.cwd
        _ret /= self.method.__func__.__name__
        for _key in inspect.signature(self.method).parameters.keys():
            _value = self.method_kwargs[_key]
            if _key == "hashable":
                _ret /= _value.hex_hash
            else:
                _ret /= str(_value)
        if not _ret.exists():
            _ret.mkdir(parents=True, exist_ok=True)
        return _ret

    def __init__(
        self,
        runner: "Runner",
        method: t.Callable,
        method_kwargs: t.Dict[str, t.Union[m.HashableClass, int, float, str]] = None,
        wait_on: t.List["JobGroup"] = None,
    ):

        # assign some vars
        self.runner = runner
        # noinspection PyTypeChecker
        self.method = method  # type: types.MethodType
        self.method_kwargs = method_kwargs or {}
        self.wait_on = wait_on or []
        # noinspection PyTypeChecker
        self._flow_id = None  # type: JobFlowId

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

        # some special methods cannot be used for job
        e.validation.ShouldNotBeOneOf(
            value=method, values=[
                runner.class_init, runner.run,
            ],
            msgs=["Some special methods cannot be used as job ..."]
        ).raise_if_failed()

        # make <hex_hash>.info if not present
        _infos_folder = runner.cwd / "infos"
        if not _infos_folder.exists():
            _infos_folder.mkdir()
        if "hashable" in self.method_kwargs.keys():
            _hashable = self.method_kwargs["hashable"]
            _info_file = _infos_folder / f"{_hashable.hex_hash}.info"
            if not _info_file.exists():
                _info_file.write_text(_hashable.yaml())

    def __call__(self):
        if self.is_on_main_machine:
            self._launch_on_cluster()
        else:
            _start = datetime.datetime.now()
            _LOGGER.info(msg=f"Starting job {self.id} at {_start.ctime()}")
            self.method(**self.method_kwargs)
            _end = datetime.datetime.now()
            _LOGGER.info(
                msg=f"Finished job {self.id} at {_start.ctime()}",
                msgs=[
                    {
                        "started": _start.ctime(),
                        "ended": _end.ctime(),
                        "seconds": str((_end - _start).total_seconds())
                    }
                ]
            )

    def _launch_on_cluster(self):
        # ------------------------------------------------------------- 01
        # make command to run on cli
        _kwargs_as_cli_strs = []
        for _k, _v in self.method_kwargs.items():
            if _k == "hashable":
                _v = _v.hex_hash
            _kwargs_as_cli_strs.append(
                f"{_k}={_v}"
            )
        _command = f"python {self.runner.py_script} " \
                   f"{self.method.__func__.__name__} " \
                   f"{' '.join(_kwargs_as_cli_strs)}"

        # ------------------------------------------------------------- 02
        if self.runner.cluster_type is JobRunnerClusterType.local:
            os.system(_command)
        elif self.runner.cluster_type is JobRunnerClusterType.ibm_lsf:
            # todo: when self.path is not local we need to see how to log files ...
            #   should we stream or dump locally ?? ... or maybe figure out
            #   dapr telemetry
            _log = self.path / ".log"
            _nxdi_prefix = f'bsub -oo {_log.local_path.as_posix()} -J {self.id} '
            if bool(self.wait_on):
                _wait_on = \
                    " && ".join([f"done({_.id})" for _ in self.wait_on])
                _nxdi_prefix += f'-w "{_wait_on}" '
            os.system(_nxdi_prefix + _command)
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[f"Unsupported cluster_type {self.runner.cluster_type}"]
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
        _method_name = sys.argv[2]
        _method = getattr(runner, _method_name)
        _method_signature = inspect.signature(_method)
        _method_kwargs = {}
        for _arg in sys.argv[3:]:
            _key, _str_val = _arg.split("=")
            if _key == "hashable":
                _info_file = runner.cwd / "infos" / f"{_str_val}.info"
                if _info_file.exists():
                    _val = _method_signature.parameters[_key].annotation.from_yaml(
                        _info_file
                    )
                else:
                    raise e.code.CodingError(
                        msgs=[f"We expect to have info file {_info_file} "
                              f"in storage"]
                    )
            else:
                _val = _method_signature.parameters[_key].annotation(_str_val)
            _method_kwargs[_key] = _val

        # return
        return Job(
            runner=runner,
            method=_method, method_kwargs=_method_kwargs,
        )

    def log_artifact(self, name: str, data: t.Any):
        _file = self.path / "artifacts" / name
        if _file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"Artifact {name} already exists ... cannot write"
                ]
            )
        # todo: make this compatible for all type of path
        with open(_file.local_path.as_posix(), 'wb') as _file:
            pickle.dump(data, _file)


class JobGroup:
    """
    Job's in this JobGroup will run in parallel and other JobGroup's can
      wait on previous JobGroup's
    We can have multiple JobGroup within
      stages so that we can move ahead with next stages if we only depend on one of
      JobGroup from previous stage
    """

    @property
    def flow_id(self) -> JobGroupFlowId:
        if self._flow_id is None:
            raise e.code.CodingError(
                msgs=[
                    f"This must be set by {Flow} using its items field ..."
                ]
            )
        return self._flow_id

    @flow_id.setter
    def flow_id(self, value: JobGroupFlowId):
        if self._flow_id is None:
            self._flow_id = value
        else:
            raise e.code.CodingError(
                msgs=[f"This property is already set you cannot set it again ..."]
            )

    @property
    @util.CacheResult
    def id(self) -> str:
        """
        A unique id for job group ...
        """
        _job_ids = "-".join([_.id for _ in self.jobs])
        return f"jgx{hashlib.sha256(_job_ids.encode('utf-8')).hexdigest()}"

    @property
    def is_on_main_machine(self) -> bool:
        return self.runner.is_on_main_machine

    def __init__(
        self,
        runner: "Runner",
        jobs: t.List[Job],
    ):
        # save vars
        self.runner = runner
        self.jobs = jobs
        # noinspection PyTypeChecker
        self._flow_id = None  # type: JobGroupFlowId

    def __call__(self):
        if self.is_on_main_machine:
            self._launch_on_cluster()
        else:
            raise e.code.CodingError(
                msgs=["We assume that this will never get called on cluster ",
                      "JobGroup should only get called on main machine ..."]
            )

    def _launch_on_cluster(self):
        # ------------------------------------------------------------- 01
        # make command to run on cli
        # there is nothing to do here as this is just a blank job that waits ...
        _command = ""

        # ------------------------------------------------------------- 02
        if self.runner.cluster_type is JobRunnerClusterType.local:
            ...
        elif self.runner.cluster_type is JobRunnerClusterType.ibm_lsf:
            _nxdi_prefix = f'bsub -J {self.id} '
            if bool(self.jobs):
                _wait_on = \
                    " && ".join([f"done({_.id})" for _ in self.jobs])
                _nxdi_prefix += f'-w "{_wait_on}" '
            os.system(_nxdi_prefix + _command)
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[f"Unsupported cluster_type {self.runner.cluster_type}"]
            )


class Flow:
    """
    This will decide how jobs will be executed on cluster
    Gets called when script is called without arguments

    Elements within list are run in parallel
    A sequence of lists is run sequentially
    First element of every list waits for last element of element in previous list
      >> Easy way to thing is UI layouts div mechanism
    """

    def __init__(
        self,
        stages: t.List[t.List[JobGroup]],
        runner: "Runner",
    ):
        # test if running on main machine which launches jobs
        # there will be only one arg
        if not runner.is_on_main_machine:
            raise e.code.CodingError(
                msgs=[
                    "This property `JobRunner.flow` should make instance of Flow.",
                    "This instance can be create only on main machine from where the "
                    "script is launched",
                    "While when jobs are running on cluster they need not use this "
                    "instance .. instead they will be using Job instance",
                ]
            )

        # save reference
        self.stages = stages
        self.runner = runner

        # set flow ids
        for _stage_id, _stage in enumerate(self.stages):
            for _job_group_id, _job_group in enumerate(_stage):
                _job_group.flow_id = JobGroupFlowId(
                    stage=_stage_id, job_group=_job_group_id,
                )
                for _job_id, _job in enumerate(_job_group.jobs):
                    _job.flow_id = JobFlowId(
                        stage=_stage_id, job_group=_job_group_id, job=_job_id
                    )

    def __call__(self):
        _cluster_type = self.runner.cluster_type
        if _cluster_type is JobRunnerClusterType.local:
            for _stage in self.stages:
                for _job_group in _stage:
                    for _job in _job_group.jobs:
                        _job()
                    _job_group()
        elif _cluster_type is JobRunnerClusterType.ibm_lsf:
            _sp = richy.SimpleStatusPanel(
                title=f"Launch stages on `{_cluster_type.name}`", tc_log=_LOGGER
            )
            with _sp:
                _p = _sp.progress
                _s = _sp.status
                _s.update(spinner_speed=1.0, spinner=None, status="started ...")
                for _stage_id, _stage in enumerate(self.stages):
                    _jobs = []
                    for _job_group in _stage:
                        _jobs += _job_group.jobs
                        _jobs += [_job_group]
                    for _job in _p.track(
                        sequence=_jobs, task_name=f"stage {_stage_id:03d}"
                    ):
                        _s.update(
                            spinner_speed=1.0,
                            spinner=None, status=f"launching {_job.flow_id} ..."
                        )
                        _job()
                _s.update(spinner_speed=1.0, spinner=None, status="finished ...")
        else:
            raise e.code.NotSupported(
                msgs=[f"Not supported {_cluster_type}"]
            )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['cwd', 'job', 'flow'],
    things_not_to_be_overridden=['cwd', 'job']
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
    cluster_type: JobRunnerClusterType

    @property
    def py_script(self) -> str:
        import pathlib
        return pathlib.Path(sys.argv[0]).name

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

        if len(sys.argv) == 1:
            raise e.code.CodingError(
                msgs=[
                    "This job is available only for jobs submitted to server ... "
                    "it cannot be accessed by instance which launches jobs ..."
                ]
            )
        else:
            _method_name = sys.argv[1]
            _method = getattr(self, _method_name)
            _method_signature = inspect.signature(_method)
            _method_kwargs = {}
            for _arg in sys.argv[2:]:
                _key, _str_val = _arg.split("=")
                if _key == "hashable":
                    _info_file = self.cwd / "infos" / f"{_str_val}.info"
                    if _info_file.exists():
                        _val = _method_signature.parameters[_key].annotation.from_yaml(
                            _info_file
                        )
                    else:
                        raise e.code.CodingError(
                            msgs=[f"We expect to have info file {_info_file} "
                                  f"in storage"]
                        )
                else:
                    _val = _method_signature.parameters[_key].annotation(_str_val)
                _method_kwargs[_key] = _val
            return Job(method=_method, method_kwargs=_method_kwargs, runner=self)

    def init(self):
        # call super
        super().init()

        # setup logger
        import logging, pathlib
        logger.setup_logging(
            propagate=False,
            level=logging.NOTSET,
            handlers=[
                logger.get_rich_handler(),
                logger.get_stream_handler(),
                logger.get_file_handler(
                    pathlib.Path(self.py_script.replace(".py", ".log"))
                ),
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
            # skip if not function
            if not inspect.isfunction(_val):
                continue

            # --------------------------------------------------- 02.03
            # get signature
            _signature = inspect.signature(_val)
            _parameter_keys = list(_signature.parameters.keys())

            # --------------------------------------------------- 02.04
            # loop over parameters
            for _parameter_key in _parameter_keys:
                # ----------------------------------------------- 02.04.01
                # if hashable parameter
                if _parameter_key == "hashable":
                    # hashable must be first
                    if "hashable" != _parameter_keys[1]:
                        raise e.validation.NotAllowed(
                            msgs=[
                                f"If using `hashable` kwarg in function {_val} make "
                                f"sure that it is first kwarg i.e. it immediately "
                                f"follows after self"
                            ]
                        )
                    # hashable annotation must be subclass of m.HashableClass
                    e.validation.ShouldBeSubclassOf(
                        value=_signature.parameters["hashable"].annotation,
                        value_types=(m.HashableClass, ),
                        msgs=["Was expecting annotation for kwarg `hashable` to be "
                              "proper subclass"]
                    ).raise_if_failed()
                # ----------------------------------------------- 02.04.02
                # infos is reserved
                elif _parameter_key == "infos":
                    raise e.code.CodingError(
                        msgs=["Refrain from defining attribute `infos` as it is "
                              "reserved for creating folder where we store hashables "
                              "info so that server can build instance from it ..."]
                    )
                # ----------------------------------------------- 02.04.02
                # if self continue
                elif _parameter_key == "self":
                    continue
                # ----------------------------------------------- 02.04.04
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

    def run(self):
        if self.is_on_main_machine:
            self.flow()
        else:
            self.job()
