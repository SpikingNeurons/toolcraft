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
import typing as t
import fsspec
import toml

# todo: keep exploring these known_implementationsas they are updated
# noinspection PyUnresolvedReferences,PyProtectedMember
from fsspec.registry import known_implementations

# todo: explore caching
# from fsspec.implementations.cached import CachingFileSystem, \
#     WholeFileCacheFileSystem, SimpleCacheFileSystem, LocalTempFile

# currently, we support (or want to support these file systems)
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.arrow import ArrowFSWrapper
# from fsspec.implementations.sftp import SFTPFileSystem
# from fsspec.implementations.zip import ZipFileSystem
# from fsspec.implementations.tar import TarFileSystem
from gcsfs import GCSFileSystem

# todo: delete `file_system_dirfs.py` file once DirFileSystem is available in fsspec
from .file_system_dirfs import DirFileSystem


from .. import error as e
from .. import util
from .. import logger
from .. import marshalling as m
from .. import settings

_LOGGER = logger.get_logger()

_FILE_SYSTEMS = {}  # type: t.Dict[str, fsspec.AbstractFileSystem]


def available_file_systems() -> t.List[str]:
    return list(settings.TC_CONFIG["file_systems"].keys())


def get_file_system(fs: str) -> fsspec.AbstractFileSystem:
    # --------------------------------------------------------- 01
    # if fs exists in _FILE_SYSTEMS return it
    if fs in _FILE_SYSTEMS.keys():
        return _FILE_SYSTEMS[fs]

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
        _fs_config = _all_fs_config[fs]
    except KeyError:
        # if CWD and it was not there we know the default ... so make one
        if fs == "CWD":
            _all_fs_config[fs] = {
                "protocol": "file", "kwargs": {}
            }
            # update settings and save
            assert id(settings.TC_CONFIG["file_systems"]) == id(_all_fs_config)
            settings.TC_CONFIG_FILE.write_text(toml.dumps(settings.TC_CONFIG))
            # store to current _fs_config
            _fs_config = _all_fs_config[fs]
        # else it is not CWD nor supported so raise error
        else:
            raise e.validation.ConfigError(
                msgs=[
                    f"Please provide file system settings for `{fs}` in dict "
                    f"`file_systems`",
                    f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
                ]
            )
    # make sure that _fs_config is dict
    e.validation.ShouldBeInstanceOf(
        value=_fs_config, value_types=(dict, ), msgs=[
            f"Was expecting dict for file system {fs} configured in settings",
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
                f"Invalid config provided for file system `{fs}` in settings",
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
                f"We expect mandatory setting `protocol` for file system {fs}",
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
    # get kwargs if provided and make sure it is dict
    _kwargs = _fs_config.get("kwargs", {})
    e.validation.ShouldBeInstanceOf(
        value=_kwargs, value_types=(dict, ), msgs=[
            f"Was expecting dict for file system {fs}.kwargs configured in settings",
            f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
        ]
    ).raise_if_failed()

    # --------------------------------------------------------- 06
    # if root_dir is provided check it
    _root_dir = _fs_config.get("root_dir", None)
    if _root_dir is not None:
        e.validation.ShouldBeInstanceOf(
            value=_root_dir, value_types=(str, ), msgs=[
                f"Was expecting str for file system `{fs}` setting `root_dir` ",
                f"Please update file {settings.TC_CONFIG_FILE.as_posix()}"
            ]
        )

    # --------------------------------------------------------- 07
    # load class for protocol
    try:
        _protocol_class = fsspec.get_filesystem_class(_protocol)
    except ImportError as _ie:
        raise e.code.CodingError(
            msgs=[
                f"You need to install some packages", str(_ie)
            ]
        )

    # --------------------------------------------------------- 08
    # make instance
    try:
        _fs = _protocol_class(**_kwargs)
        # Add dir (using DirFileSystem) if specified ...
        if _root_dir is not None:
            # todo: currently we block this for efficiency reasons ... as we might do
            #  lot of small file writes to CWD ... remove this code only if necessary
            if fs == "CWD":
                raise e.validation.ConfigError(
                    msgs=[
                        f"Avoid using setting root_dir for CWD for efficiency",
                        f"We will explore later if we want to enable it"
                    ]
                )
            # wrap with DirFileSystem
            _fs = DirFileSystem(
                path=_root_dir, fs=_fs, **_kwargs
            )
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
    _FILE_SYSTEMS[fs] = _fs
    return _fs


