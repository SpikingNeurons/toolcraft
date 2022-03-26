"""
todo: deprecate in favour of dapr module
"""

import enum
import pathlib
import inspect
import typing as t
import dataclasses
import os
import sys
import pickle
import types

from . import logger
from . import error as e
from . import marshalling as m
from . import util
from . import storage as s


_LOGGER = logger.get_logger()


@dataclasses.dataclass
class Viewer:
    runner: "JobRunner"
    fn: t.Callable
    fn_kwargs: t.Dict


class JobRunnerClusterType(m.FrozenEnum, enum.Enum):
    """
    todo: support ibm_lsf over ssh using https://www.fabfile.org
    """
    ibm_lsf = enum.auto()
    local = enum.auto()


@dataclasses.dataclass(frozen=True)
class Job:
    method: types.MethodType
    method_kwargs: t.Dict[str, t.Union[m.HashableClass, int, float, str]] = \
        dataclasses.field(default_factory=dict)
    jobs_from_last_stage: t.List["Job"] = \
        dataclasses.field(default_factory=list)

    @property
    @util.CacheResult
    def id(self) -> str:
        """
        This takes in account
        + fn_name
        + fn_kwargs if present
        + hashable hex_hash if present
        """
        _n = self.path.suffix_path.replace("/", "x")
        return f"jx{_n}"

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

    @property
    @util.CacheResult
    def runner(self) -> "JobRunner":
        try:
            # noinspection PyTypeChecker
            _ret = self.method.__self__  # type: JobRunner
        except Exception as _ex:
            raise e.code.CodingError(
                msgs=[
                    f"Doesn't seem like a method of an instance ...", _ex
                ]
            )
        e.validation.ShouldBeInstanceOf(
            value=_ret, value_types=(JobRunner, ),
            msgs=[f"expected method to be from a instance of any subclass "
                  f"of {JobRunner}"]
        ).raise_if_failed()
        return _ret

    def __post_init__(self):
        # some special methods cannot be used for job
        _runner = self.runner
        e.validation.ShouldNotBeOneOf(
            value=self.method, values=[
                _runner.class_init, _runner.log_artifact,
                _runner.run_flow, _runner.run, _runner.viewer,
            ],
            msgs=["Some special methods cannot be used as job ..."]
        ).raise_if_failed()

        # make <hex_hash>.info if not present
        _infos_folder = _runner.cwd / "infos"
        if not _infos_folder.exists():
            _infos_folder.mkdir()
        if "hashable" in self.method_kwargs.keys():
            _hashable = self.method_kwargs["hashable"]
            _info_file = _infos_folder / f"{_hashable.hex_hash}.info"
            if not _info_file.exists():
                _info_file.write_text(_hashable.yaml())

    def __call__(self) -> t.Any:
        _ret = self.method(**self.method_kwargs)
        return _ret

    def launch_on_cluster(self):
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
            if bool(self.jobs_from_last_stage):
                _wait_on = \
                    " && ".join([f"done({_.id})" for _ in self.jobs_from_last_stage])
                _wait_over = f'-w "{_wait_on}" '
            os.system(_nxdi_prefix + _command)
        else:
            raise e.code.ShouldNeverHappen(
                msgs=[f"Unsupported cluster_type {self.runner.cluster_type}"]
            )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['cwd', 'job'],
    things_not_to_be_overridden=['cwd', 'job']
)
class JobRunner(m.HashableClass):
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
        return sys.argv[0]

    @property
    @util.CacheResult
    def cwd(self) -> s.Path:
        """
        todo: adapt code so that the cwd can be on any other file system instead of CWD
        """
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
        return _ret

    @property
    @util.CacheResult
    def job(self) -> Job:
        """
        Note that this job is available only on server i.e. to the submitted job on
        cluster ... on job launching machine access to this property will raise error

        Note this can read cli args and construct `method` and `method_kwargs` fields
        """

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
            return Job(method=_method, method_kwargs=_method_kwargs)

    @classmethod
    def class_init(cls):
        # ------------------------------------------------------- 01
        # call super
        super().class_init()

        # ------------------------------------------------------- 02
        # test fn signature
        # loop over attributes
        for _attr in [_ for _ in dir(cls) if not _.startswith("_")]:
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
                # ----------------------------------------------- 02.04.03
                # else make sure that annotation is int, float or str ...
                else:
                    e.validation.ShouldBeSubclassOf(
                        value=_signature.parameters[_parameter_key].annotation,
                        value_types=(int, float, str),
                        msgs=["Was restrict annotation types for proper "
                              "kwarg serialization so that they can be passed over "
                              "cli ... and can also determine path for storage"]
                    ).raise_if_failed()

    def log_artifact(self, name: str, data: t.Any):
        _file = self.path / "artifacts" / name
        if _file.exists():
            raise e.code.CodingError(
                msgs=[
                    f"Artifact {name} already exists ... cannot write"
                ]
            )
        with open(_file.as_posix(), 'wb') as _file:
            pickle.dump(data, _file)

    def run_flow(self, run_file: pathlib.Path, root_dir: pathlib.Path):

        # ------------------------------------------ 01
        # tuple to job make
        def _tuple_2_job(
            _t: t.Tuple[t.Callable, t.Dict], _prev_js,
        ) -> JobRunnerHelper:

            # -------------------------------------- 01.01
            # resolve tuple
            (_fn, _fn_kwargs) = _t
            # make sure that _fn is not one of reserved methods
            e.validation.ShouldNotBeOneOf(
                value=_fn, values=[self.flow, ],
                msgs=[
                    f"We do not expect you to reserve methods in the flow ..."
                ]
            ).raise_if_failed()
            # check if all kwargs are supplied
            for _sk in inspect.signature(_fn).parameters.keys():
                if _sk not in _fn_kwargs.keys():
                    raise e.code.CodingError(
                        msgs=[
                            f"You did not supply kwarg `{_sk}` while defining flow ..."
                        ]
                    )
            # check is some non-supported kwargs are supplied
            for _dk in _fn_kwargs.keys():
                if _dk not in inspect.signature(_fn).parameters.keys():
                    raise e.code.CodingError(
                        msgs=[
                            f"Supplied key `{_dk}` if not valid kwarg for method {_fn}"
                        ]
                    )

            # -------------------------------------- 01.02
            # check
            if not inspect.ismethod(_fn):
                raise e.code.CodingError(
                    msgs=[
                        f"Please provide method of JobRunner instance ...",
                        f"Found unrecognized {_t}"
                    ]
                )

            # -------------------------------------- 01.03
            # make command
            # noinspection PyUnresolvedReferences
            _fn_name = _fn.__func__.__name__
            _fn_kwargs_str_list = []
            for _k, _v in _fn_kwargs.items():
                if isinstance(_v, m.HashableClass):
                    # this is our opportunity to create folder and info file
                    _hash_info = root_dir / f"{_v.hex_hash}.info"
                    _hash_dir = root_dir / _v.hex_hash
                    if not _hash_info.exists():
                        _hash_info.write_text(_v.yaml())
                    (root_dir / _v.hex_hash).mkdir(exist_ok=True)
                    # make token
                    _fn_kwargs_str_list.append(
                        f"{_k}={_v.hex_hash}"
                    )
                else:
                    _fn_kwargs_str_list.append(
                        f"{_k}={_v}"
                    )

            # -------------------------------------- 01.04
            # make and return job runner
            return JobRunnerHelper(
                runner=self,
                run_file=run_file,
                root_dir=root_dir,
                fn_name=_fn_name,
                fn_kwargs=_fn_kwargs_str_list,
                jobs_from_last_stage=_prev_js,
            )

        # ------------------------------------------ 02
        # get flow
        _flow = self.flow()

        # ------------------------------------------ 03
        # helper recursive function
        def _run_flow(
            _col_jobs: t.Union[
                t.List[t.List[t.Union[t.Tuple[t.Callable, t.Dict], t.List]]],
                t.Tuple[t.Callable, t.Dict]
            ],
            _msg: str,
            _prev_jobs: t.List[JobRunnerHelper],
        ):
            """
            import typing as t

            ll = [
                [1, [[234, 222, [[123]]]]],
                [2, 3,],
                [4, 5, [[5], [99]]],
                [5, [[6,7,]], [[8], [9, 10], [11]]],
            ]



            def _fn(
                _col_jobs: t.Union[t.List[t.List], int],
                _msg: str,
                _prev_jobs: t.List
            ):

                print(_col_jobs, _msg, _prev_jobs)

                if isinstance(_col_jobs, int):
                    return _col_jobs

                _last_row_prev_jobs = _prev_jobs
                _curr_row_prev_jobs = []

                for _rid, _row_job in enumerate(_col_jobs):
                    if not isinstance(_row_job, list):
                        raise Exception("expected row which is list")
                    _curr_row_prev_jobs = []
                    for _eid, _elem in enumerate(_row_job):
                        _last_job = _fn(_elem, _msg + f'.r{_rid}[{_eid}]', _last_row_prev_jobs)
                        if isinstance(_last_job, list):
                            _curr_row_prev_jobs.extend(_last_job)
                        else:
                            _curr_row_prev_jobs.append(_last_job)
                    _last_row_prev_jobs = _curr_row_prev_jobs

                return _curr_row_prev_jobs



            _fn(ll, "", [])

            """

            # if tuple creat job runner and return
            if isinstance(_col_jobs, tuple):
                return _tuple_2_job(_col_jobs, _prev_jobs)

            # some book-up vars
            _last_row_prev_jobs = _prev_jobs  # type: t.List[JobRunnerHelper]
            _curr_row_prev_jobs = []  # type: t.List[JobRunnerHelper]

            for _rid, _row_job in enumerate(_col_jobs):
                if not isinstance(_row_job, list):
                    raise e.code.CodingError(
                        msgs=[f"expected row which is list, found {type(_row_job)}"]
                    )
                _curr_row_prev_jobs = []
                for _eid, _elem in enumerate(_row_job):
                    _c_msg = _msg + f'.r{_rid}[{_eid}]'
                    _last_job = _run_flow(_elem, _c_msg, _last_row_prev_jobs)
                    if isinstance(_last_job, list):
                        _curr_row_prev_jobs.extend(_last_job)
                    else:
                        _curr_row_prev_jobs.append(_last_job)
                        _LOGGER.info(
                            msg=f"Running job ",
                            msgs=[[f"{_c_msg}", f"{_last_job.id}"]]
                        )
                        _LOGGER.info(
                            msg=f"Will wait over previous jobs ",
                            msgs=[[_.id for _ in _last_row_prev_jobs]]
                        )
                        _last_job.launch_on_cluster()
                _last_row_prev_jobs = _curr_row_prev_jobs

            return _curr_row_prev_jobs

        # ------------------------------------------ 04
        _run_flow(_flow, "", [])

    # noinspection PyMethodMayBeStatic
    def flow(self) -> t.List[
        t.Union[t.Tuple[t.Callable, t.Dict[str, t.Union[str, int, float]]], t.List]
    ]:
        """
        This method will call more jobs and decide the job flow.
        Gets called when script is called without arguments

        Elements within list are run in parallel
        A sequence of lists is run sequentially
        First element of every list waits for last element of element in previous list
          >> Easy way to thing is UI layouts div mechanism
        """
        raise e.validation.NotAllowed(
            msgs=[
                f"Please override this method to define the flow of jobs ..."
            ]
        )

    def run(self):
        _run_file = pathlib.Path(self.py_script)
        _root_dir = _run_file.parent / _run_file.name.replace(".py", "")
        if not _root_dir.exists():
            _root_dir.mkdir()
        if len(sys.argv) == 1:
            return self.run_flow(run_file=_run_file, root_dir=_root_dir)
        else:
            _fn_name = sys.argv[1]
            _helper = JobRunnerHelper(
                runner=self,
                run_file=_run_file,
                root_dir=_root_dir,
                fn_name=_fn_name,
                fn_kwargs=[] if len(sys.argv) <= 2 else sys.argv[2:],
                jobs_from_last_stage=[],
            )
            _helper()

    def viewer(self) -> Viewer:
        """
        Allows you to view what job is doing or already done
        """
        ...
