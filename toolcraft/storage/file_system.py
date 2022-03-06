"""
Module related to file systems to be used with `storage.df_file`.
Decides where and how to save dataframes of different storage types.

Currently designed based on file systems of pyarrow.
Used by `storage.df_file` i.e. for dataframe storage.
Note that this is different from file format which is either ipc/feather or
parquet.

todo: can make `storage.file_group` use the file systems to save the
  FileGroup and Folder.

We will also add our own file systems here.

todo: add support https://arrow.apache.org/docs/python/filesystems.html#filesystem-hdfs
  check
    import gcsfs
    import adlfs

todo: This is new (go on to fsspec) even pyarrow file-system allows fsspec and pafs
  offers limited subset of functions of what fsspec offers i.e. related to pa.dataset
  storage ... but other extensive stuff for flie system can come from fsspec
  + https://filesystem-spec.readthedocs.io/en/latest/features.html#caching-files-locally
  Also see the exhaustive implementaions
  + https://github.com/fsspec/filesystem_spec/tree/master/fsspec/implementations

todo: remote caching
  https://www.anaconda.com/blog/fsspec-remote-caching

todo: note that we can safely use this module for
  both Table (mlflow metrics) and FileGroup (mlflow artifacts)
  + file_group uses Folder that can use file system
  + stream and table will use table.Table which is Folder so that can use file_system
  + state will use dapr state and hence no need for file_system there
"""
import dataclasses
import pathlib
import typing as t
import fsspec
import os
import toml
import pyarrow as pa

# todo: keep exploring these known_implementationsas they are updated
# noinspection PyUnresolvedReferences,PyProtectedMember
from fsspec.registry import known_implementations

# todo: explore caching
# from fsspec.implementations.cached import CachingFileSystem, \
#     WholeFileCacheFileSystem, SimpleCacheFileSystem, LocalTempFile

# todo: pyarrow ... may be not needed as pa.dataset accepts any file system and maybe
#  we dont need anything more ... if we use native pyarrow file systems with a wrapper
#  for fsspec then we are limited to local, S3 and Hadoop ... monitor evlution of
#  this library they might eventually drop that lib and grow more dependant on fsspec
#  https://arrow.apache.org/docs/python/filesystems.html
# from pyarrow.fs import PyFileSystem, FSSpecHandler
# pa_fs = PyFileSystem(FSSpecHandler(fs))

# currently, we support (or want to support these file systems)
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.arrow import ArrowFSWrapper
# from fsspec.implementations.sftp import SFTPFileSystem
# from fsspec.implementations.zip import ZipFileSystem
# from fsspec.implementations.tar import TarFileSystem
from gcsfs import GCSFileSystem

from .. import error as e
from .. import logger
from .. import settings

_LOGGER = logger.get_logger()

_FILE_SYSTEMS = {}  # type: t.Dict[str, fsspec.AbstractFileSystem]
_FILE_SYSTEMS_CONFIG = {}  # type: t.Dict[str, t.Dict]


@dataclasses.dataclass
class Path:
    """
    todo: chmod and dir permissions
      On certain file systems we can do it and we can exploit **kwargs of
      fsspec.AbstractFileSystem or else add our custom methods overe here

    todo: Explore and implement fsspec.AbstractFileSystem
        for _ in dir(fsspec.AbstractFileSystem):
        if _.startswith("_"):
            continue
        print(f"    >>> fsspec.AbstractFileSystem.{_}")
    >>> fsspec.AbstractFileSystem.cat
    >>> fsspec.AbstractFileSystem.cat_file
    >>> fsspec.AbstractFileSystem.cat_ranges
    >>> fsspec.AbstractFileSystem.checksum
    >>> fsspec.AbstractFileSystem.clear_instance_cache
    >>> fsspec.AbstractFileSystem.copy
    >>> fsspec.AbstractFileSystem.cp
    >>> fsspec.AbstractFileSystem.cp_file
    >>> fsspec.AbstractFileSystem.created
    >>> fsspec.AbstractFileSystem.current
    >>> fsspec.AbstractFileSystem.delete
    >>> fsspec.AbstractFileSystem.disk_usage
    >>> fsspec.AbstractFileSystem.download
    >>> fsspec.AbstractFileSystem.du
    >>> fsspec.AbstractFileSystem.end_transaction
    >>> fsspec.AbstractFileSystem.exists
    >>> fsspec.AbstractFileSystem.expand_path
    >>> fsspec.AbstractFileSystem.find
    >>> fsspec.AbstractFileSystem.from_json
    >>> fsspec.AbstractFileSystem.get
    >>> fsspec.AbstractFileSystem.get_file
    >>> fsspec.AbstractFileSystem.get_mapper
    >>> fsspec.AbstractFileSystem.glob
    >>> fsspec.AbstractFileSystem.head
    >>> fsspec.AbstractFileSystem.info
    >>> fsspec.AbstractFileSystem.invalidate_cache
    >>> fsspec.AbstractFileSystem.isdir
    >>> fsspec.AbstractFileSystem.isfile
    >>> fsspec.AbstractFileSystem.lexists
    >>> fsspec.AbstractFileSystem.listdir
    >>> fsspec.AbstractFileSystem.ls
    >>> fsspec.AbstractFileSystem.makedir
    >>> fsspec.AbstractFileSystem.makedirs
    >>> fsspec.AbstractFileSystem.mkdir
    >>> fsspec.AbstractFileSystem.mkdirs
    >>> fsspec.AbstractFileSystem.modified
    >>> fsspec.AbstractFileSystem.move
    >>> fsspec.AbstractFileSystem.mv
    >>> fsspec.AbstractFileSystem.open
    >>> fsspec.AbstractFileSystem.pipe
    >>> fsspec.AbstractFileSystem.pipe_file
    >>> fsspec.AbstractFileSystem.protocol
    >>> fsspec.AbstractFileSystem.put
    >>> fsspec.AbstractFileSystem.put_file
    >>> fsspec.AbstractFileSystem.read_block
    >>> fsspec.AbstractFileSystem.rename
    >>> fsspec.AbstractFileSystem.rm
    >>> fsspec.AbstractFileSystem.rm_file
    >>> fsspec.AbstractFileSystem.rmdir
    >>> fsspec.AbstractFileSystem.root_marker
    >>> fsspec.AbstractFileSystem.sep
    >>> fsspec.AbstractFileSystem.sign
    >>> fsspec.AbstractFileSystem.size
    >>> fsspec.AbstractFileSystem.sizes
    >>> fsspec.AbstractFileSystem.start_transaction
    >>> fsspec.AbstractFileSystem.stat
    >>> fsspec.AbstractFileSystem.tail
    >>> fsspec.AbstractFileSystem.to_json
    >>> fsspec.AbstractFileSystem.touch
    >>> fsspec.AbstractFileSystem.transaction
    >>> fsspec.AbstractFileSystem.ukey
    >>> fsspec.AbstractFileSystem.upload
    >>> fsspec.AbstractFileSystem.walk
    """
    suffix_path: str
    fs_name: str
    details: t.Dict = None

    # HOME = pathlib.Path.home()

    def __post_init__(self):
        # set some vars for faster access
        self.fs, self.fs_config = get_file_system_details(self.fs_name)
        self.sep = self.fs.sep  # type: str
        self.root_path = self.fs_config['root_dir']  # type: str
        self.full_path = self.root_path + self.sep + self.suffix_path
        self.name = self.suffix_path.split(self.sep)[-1]
        e.io.LongPath(path=self.full_path, msgs=[]).raise_if_failed()

        # do any validations if needed
        ...

    def __str__(self) -> str:
        return f"{self.fs_name}::{self.suffix_path}"

    def __repr__(self) -> str:
        return self.__str__()

    def __truediv__(self, other: str) -> "Path":
        if other.find(self.sep) != -1:
            raise e.code.CodingError(
                msgs=[
                    f"we do not allow seperator `{self.sep}` in the token `{other}`"
                ]
            )
        _suffix = self.suffix_path
        if _suffix != "":
            _suffix += self.sep + other
        else:
            _suffix = other
        return Path(suffix_path=_suffix, fs_name=self.fs_name)

    def __add__(self, other: str) -> "Path":
        if other.find(self.sep) != -1:
            raise e.code.CodingError(
                msgs=[
                    f"we do not allow seperator {self.sep} in the token {other}"
                ]
            )
        return Path(suffix_path=self.suffix_path + other, fs_name=self.fs_name)

    @classmethod
    def get_root(cls, fs_name: str) -> "Path":
        _fs, _fs_config = get_file_system_details(fs_name=fs_name)
        return Path(
            fs_name=fs_name, suffix_path=""
        )

    def exists(self) -> bool:
        return self.fs.exists(path=self.full_path)

    def isdir(self) -> bool:
        return self.fs.isdir(path=self.full_path)

    def isfile(self) -> bool:
        return self.fs.isfile(path=self.full_path)

    def mkdir(self, create_parents: bool = True, **kwargs):
        self.fs.mkdir(path=self.full_path, create_parents=create_parents, **kwargs)

    def delete(self, recursive: bool = False, maxdepth: int = None):
        return self.fs.delete(
            path=self.full_path, recursive=recursive, maxdepth=maxdepth)

    def stat(self) -> t.Dict:
        return self.fs.stat(path=self.full_path)

    def open(
        self, mode: str,
        block_size=None,
        cache_options=None,
        compression=None,
    ):
        return self.fs.open(
            path=self.full_path,
            mode=mode,
            # todo: use below options
            block_size=block_size,
            cache_options=cache_options,
            compression=compression)

    def write_text(self, text: str):
        with self.fs.open(path=self.full_path, mode='w') as _f:
            _f.write(text)

    def append_text(self, text: str):
        with self.fs.open(path=self.full_path, mode='a') as _f:
            _f.write(text)

    def read_text(self) -> str:
        with self.fs.open(path=self.full_path, mode='r') as _f:
            return _f.read()

    def _post_process_res(self, _res) -> t.List["Path"]:
        """
        None _k[_k.find(self.full_path):] or _[_.find(self.full_path):] just strips
          extra things added by file system when crawling directory ... this is not
          needed as anyway we will know it ...
          If optimization needed do only is needed based on file_system
           - (for example LocalFileSystem it is needed)

        """
        _root_path = self.root_path
        if self.fs_name == "CWD":
            # we replace `.` with cwd
            # todo: also test for linux
            _root_path = _root_path.replace(".", os.getcwd().replace("\\", "/"))

        if isinstance(_res, dict):
            return [
                Path(
                    suffix_path=_k.replace(_root_path, ""),
                    fs_name=self.fs_name, details=_v)
                for _k, _v in _res.items()
            ]
        elif isinstance(_res, list):
            return [
                Path(suffix_path=_.replace(_root_path, ""), fs_name=self.fs_name)
                for _ in _res
            ]
        else:
            raise e.code.NotSupported(
                msgs=[f"Unknown type {type(_res)}"]
            )

    def find(
        self, path: str = ".",
        maxdepth: int = None, withdirs: bool = False, detail: bool = False
    ) -> t.List["Path"]:
        _path = self.full_path if path == "." else self.full_path + self.sep + path
        _res = self.fs.find(
            path=_path, maxdepth=maxdepth, withdirs=withdirs, detail=detail
        )
        return self._post_process_res(_res)

    def glob(
        self, pattern: str, detail: bool = False
    ) -> t.List["Path"]:
        _pattern = self.full_path + "/" + pattern
        _res = self.fs.glob(path=_pattern, detail=detail)
        return self._post_process_res(_res)

    def walk(
        self,  path: str = ".", maxdepth: int = None, detail: bool = False
    ) -> t.List["Path"]:
        _path = self.full_path if path == "." else self.full_path + self.sep + path
        for _ in self.fs.walk(
            path=_path, maxdepth=maxdepth, detail=detail
        ):
            yield Path(
                suffix_path=_[0].replace(self.root_path, ""), fs_name=self.fs_name
            ), self._post_process_res(_[1]), self._post_process_res(_[2])
            # return self._post_process_res(_res)

    def ls(
        self, path: str = ".", detail: bool = False
    ) -> t.List["Path"]:
        _path = self.full_path if path == "." else self.full_path + self.sep + path
        _res = self.fs.ls(path=_path, detail=detail)
        return self._post_process_res(_res)

    def is_dir_empty(self) -> bool:
        return len(self.ls()) == 0

    def rm(
        self, path: t.Union[str, t.List[str]] = ".",
        recursive: bool = False, maxdepth: int = None
    ):
        if isinstance(path, str):
            path = [path]
        _new_path = []
        for _p in path:
            _new_path.append(
                self.full_path if _p == "." else self.full_path + self.sep + _p
            )
        self.fs.rm(path=_new_path, recursive=recursive, maxdepth=maxdepth)

    def rm_file(self, path: str = "."):
        _path = self.full_path if path == "." else self.full_path + self.sep + path
        self.fs.rm_file(path=_path)

    def rmdir(self, path: str = "."):
        _path = self.full_path if path == "." else self.full_path + self.sep + path
        return self.fs.rmdir(path=_path)


def available_file_systems() -> t.List[str]:
    return list(settings.TC_CONFIG["file_systems"].keys())


def get_file_system_details(fs_name: str) -> t.Tuple[fsspec.AbstractFileSystem, t.Dict]:
    # --------------------------------------------------------- 01
    # if fs exists in _FILE_SYSTEMS return it
    if fs_name in _FILE_SYSTEMS.keys():
        return _FILE_SYSTEMS[fs_name], _FILE_SYSTEMS_CONFIG[fs_name]

    # --------------------------------------------------------- 02
    # check in settings if any file_system is provided
    try:
        _all_fs_config = settings.TC_CONFIG["file_systems"]
    except KeyError:
        # if not add an empty dict and save it to config
        _all_fs_config = {}
        # update settings and save
        settings.TC_CONFIG["file_systems"] = _all_fs_config
        settings.TC_CONFIG_FILE.write_text(toml.dumps(settings.TC_CONFIG))

    # --------------------------------------------------------- 03
    # now check for specific fs
    try:
        _fs_config = _all_fs_config[fs_name]
    except KeyError:
        # if CWD and it was not there we know the default ... so make one
        if fs_name == "CWD":
            _all_fs_config[fs_name] = {
                "protocol": "file", "root_dir": ".", "kwargs": {"auto_mkdir": True}
            }
            # update settings and save
            assert id(settings.TC_CONFIG["file_systems"]) == id(_all_fs_config)
            settings.TC_CONFIG_FILE.write_text(toml.dumps(settings.TC_CONFIG))
            # store to current _fs_config
            _fs_config = _all_fs_config[fs_name]
        # else it is not CWD nor supported so raise error
        else:
            raise e.validation.ConfigError(
                msgs=[
                    f"Please provide file system settings for `{fs_name}` in dict "
                    f"`file_systems`",
                    f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
                ]
            )
    # make sure that _fs_config is dict
    e.validation.ShouldBeInstanceOf(
        value=_fs_config, value_types=(dict, ), msgs=[
            f"Was expecting dict for file system {fs_name} configured in settings",
            f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
        ]
    ).raise_if_failed()

    # --------------------------------------------------------- 04
    # make sure that there we know thw settings i.e. they should be one or more
    # of these three
    for _k in _fs_config.keys():
        e.validation.ShouldBeOneOf(
            value=_k, values=["protocol", "kwargs", "root_dir"],
            msgs=[
                f"Invalid config provided for file system `{fs_name}` in settings",
                f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
            ]
        ).raise_if_failed()

    # --------------------------------------------------------- 04
    # make sure that we have mandatory setting protocol
    try:
        _protocol = _fs_config["protocol"]
    except KeyError:
        raise e.validation.ConfigError(
            msgs=[
                f"We expect mandatory setting `protocol` for file system {fs_name}",
                f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
            ]
        )
    # test if it is known
    e.validation.ShouldBeOneOf(
        value=_protocol, values=known_implementations.keys(),
        msgs=[
            "Unsupported file system protocol ..."
        ]
    ).raise_if_failed()

    # --------------------------------------------------------- 05
    # check for mandatory root_dir
    try:
        _root_dir = _fs_config["root_dir"]
    except KeyError:
        raise e.validation.ConfigError(
            msgs=[
                f"We expect mandatory setting `root_dir` for file system {fs_name}",
                f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
            ]
        )
    # validate type
    e.validation.ShouldBeInstanceOf(
        value=_root_dir, value_types=(str, ), msgs=[
            f"Was expecting str for file system `{fs_name}` setting `root_dir` ",
            f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
        ]
    ).raise_if_failed()
    # if CWD make sure that root_dir always start with .
    if fs_name == "CWD":
        if not _root_dir.startswith("."):
            raise e.validation.NotAllowed(
                msgs=[
                    f"For CWD file_system always make sure that root_dir starts with "
                    f"'.', found {_root_dir}"
                ]
            )

    # --------------------------------------------------------- 06
    # get kwargs if provided and make sure it is dict
    _kwargs = _fs_config.get("kwargs", {})
    e.validation.ShouldBeInstanceOf(
        value=_kwargs, value_types=(dict, ), msgs=[
            f"Was expecting dict for file system {fs_name}.kwargs configured in "
            f"settings",
            f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
        ]
    ).raise_if_failed()

    # --------------------------------------------------------- 07
    # load class for protocol
    try:
        _protocol_class = fsspec.get_filesystem_class(_protocol)
    except ImportError as _ie:
        raise e.code.CodingError(
            msgs=[
                f"You need to install some packages",
                {
                    "raised_error": str(_ie)
                }
            ]
        )

    # --------------------------------------------------------- 08
    # make instance
    try:
        _fs = _protocol_class(**_kwargs)
    except TypeError as _te:
        raise e.code.CodingError(
            msgs=[
                f"Invalid kwargs supplied ... Class {_protocol_class} "
                f"cannot recognize them ...",
                f"Please update file {settings.TC_CONFIG_FILE.as_posix()}",
                {
                    "raised_error": str(_te)
                }
            ]
        )

    # --------------------------------------------------------- 09
    # if root_dir in fs_config end with sep then raise error as we will be adding it
    if _fs_config["root_dir"].endswith(_fs.sep):
        raise e.code.NotAllowed(
            msgs=[
                f"Please do not supply seperator `{_fs.sep}` at end for root_dir "
                f"in config files. As we will take care of that ..."
            ]
        )

    # --------------------------------------------------------- 09
    # backup and return
    _FILE_SYSTEMS[fs_name] = _fs
    _FILE_SYSTEMS_CONFIG[fs_name] = _fs_config
    return _FILE_SYSTEMS[fs_name], _FILE_SYSTEMS_CONFIG[fs_name]
