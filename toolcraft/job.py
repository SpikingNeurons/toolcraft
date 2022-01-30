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

from . import logger
from . import error as e
from . import marshalling as m
from . import util


_LOGGER = logger.get_logger()


@dataclasses.dataclass
class Viewer:
    runner: "JobRunner"
    fn: t.Callable
    fn_kwargs: t.Dict


class JobRunnerClusterType(enum.Enum):
    """
    todo: support ibm_lsf over ssh using https://www.fabfile.org
    """
    ibm_lsf = enum.auto()
    local = enum.auto()


@dataclasses.dataclass
class JobRunnerHelper:

    runner: "JobRunner"
    root_dir: pathlib.Path
    run_file: pathlib.Path
    fn_name: str
    fn_kwargs: t.List[str]
    jobs_from_last_stage: t.List['JobRunnerHelper']

    @property
    @util.CacheResult
    def id(self) -> str:
        """
        This takes in account
        + fn_name
        + fn_kwargs if present
        + hashable hex_hash if present
        """
        _n = "x".join(
            self.storage_dir.absolute(
            ).relative_to(self.root_dir.absolute()).as_posix().split("/")
        )
        return f"jx{_n}"

    @property
    @util.CacheResult
    def storage_dir(self) -> pathlib.Path:
        """
        If job is for hashable then it is not a uni job and hence will be nested

        Note that folder nesting is dependent on `self.fn` signature ...

        Note that if
        where hashable is automatically made first element even if it is not defined
        first ...

        todo: integrate this with storage with partition_columns ...
          note that first pivot will then be hashable name ...
        """
        _fn_signature_params = inspect.signature(self.fn).parameters
        _ret_dir = self.root_dir
        if "hashable" in _fn_signature_params:
            _ret_dir /= self.fn_kwargs_casted["hashable"].hex_hash
        _ret_dir /= self.fn_name
        for _arg_name in _fn_signature_params:
            if _arg_name != "hashable":
                _ret_dir /= f"{_arg_name}_{self.fn_kwargs_casted[_arg_name]}"
        if not _ret_dir.exists():
            _ret_dir.mkdir(parents=True, exist_ok=True)
        return _ret_dir

    def __post_init__(self):

        # ----------------------------------------------- 01
        # get fn
        try:
            self.fn = getattr(self.runner, self.fn_name)
            if not inspect.ismethod(self.fn):
                raise e.code.CodingError(
                    msgs=[
                        f"We expect attribute {self.fn_name} to be method in class "
                        f"{self.runner,__class__}, but instead it is of type "
                        f"{type(self.fn)}"
                    ]
                )
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"Command `{self.fn_name}` is not available for class "
                    f"{self.runner.__class__}. Please implement a method with that "
                    f"name in class {self.runner.__class__}"
                ]
            )

        # ----------------------------------------------- 02
        # make fn kwargs and add hashable instance if needed
        _fn_signature_params = inspect.signature(self.fn).parameters
        self.fn_kwargs_casted = {}
        # loop over all command line tokens
        for _a in self.fn_kwargs:
            try:
                # get as str
                [_arg_name, _arg_value] = _a.split("=")

                # get annotation type
                _ann_type = _fn_signature_params[_arg_name].annotation

                # if _arg_name is hashable then create hashable instance
                if _arg_name == "hashable":
                    _ann_type: m.HashableClass
                    e.validation.ShouldBeSubclassOf(
                        value=_ann_type, value_types=(m.HashableClass, ),
                        msgs=[
                            f"If using hashable kwarg then always annotate it with "
                            f"some subclass of {m.HashableClass} ..."
                        ]
                    )
                    _hashable = _ann_type.from_yaml(
                        self.root_dir / f"{_arg_value}.info"
                    )
                    self.fn_kwargs_casted[_arg_name] = _hashable

                # else should be a simple type int, str, or float
                else:
                    e.validation.ShouldBeOneOf(
                        value=_ann_type, values=[int, float, str],
                        msgs=[
                            f"Annotation type for kwarg `{_arg_name}` of function "
                            f"{self.fn} is wrong"
                        ]
                    )
                    self.fn_kwargs_casted[_arg_name] = _ann_type(_arg_value)

            # exception if improper command line token
            except ValueError:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Supply args as `<arg_name>=<arg_values>` with no spaces "
                        "around `=`",
                        f"Found incompatible token `{_a}`"
                    ]
                )

    def __call__(self):
        if '__helper__' in self.runner.__dict__.keys():
            raise e.code.CodingError(
                msgs=[
                    f"We do not expect __helper__ to be set ..."
                ]
            )
        self.runner.__dict__['__helper__'] = self
        return self.fn(**self.fn_kwargs_casted)

    def launch_on_cluster(self):
        # ------------------------------------------------------------- 01
        # make command to run on cli
        _command = f"python {self.run_file.name} " \
                   f"{self.fn_name} {' '.join(self.fn_kwargs)}"

        # ------------------------------------------------------------- 02
        if self.runner.cluster_type is JobRunnerClusterType.local:
            os.system(_command)
        elif self.runner.cluster_type is JobRunnerClusterType.ibm_lsf:
            _log = self.storage_dir / ".log"
            _nxdi_prefix = f'bsub -oo {_log.as_posix()} -J {self.id} '
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
class JobRunner:
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
    @util.CacheResult
    def id(self) -> str:
        return self.helper.id

    @property
    @util.CacheResult
    def storage_dir(self) -> pathlib.Path:
        return self.helper.storage_dir

    @property
    def helper(self) -> JobRunnerHelper:
        if '__helper__' in self.__dict__.keys():
            return self.__dict__['__helper__']
        else:
            raise e.code.CodingError(
                msgs=[
                    f"This is property is available only when job is running on "
                    f"cluster, as this hidden variable is updated only while jobs "
                    f"run on cluster ... check {JobRunnerHelper.__call__}"
                ]
            )

    def log_artifact(self, name: str, data: t.Any):
        _file = self.storage_dir / "artifacts" / name
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
            )
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
        return []

    def run(self):
        _run_file = pathlib.Path(sys.argv[0])
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
