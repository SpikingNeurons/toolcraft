"""
todo: Formalize with a parent Settings class which will store settings in
  `.toolcraft` folder
"""

import numpy as np
import pathlib
import toml
import typing as t
import sys
# noinspection PyUnresolvedReferences,PyCompatibility
import __main__ as main

# serving mode (dapr server)
DAPR_SERVE_MODE = False
# noinspection PyTypeChecker
DAPR_SESSION_DIR = None  # type: pathlib.Path


# check if debugger is used
PYC_DEBUGGING = False
gettrace = getattr(sys, 'gettrace', None)
if gettrace is not None:
    if gettrace():
        PYC_DEBUGGING = True

# detect if in interactive mode
INTERACTIVE = not hasattr(main, '__file__')

DISABLE_PROGRESS_BAR = False
LOGGER_USE_FILE_HANDLER = False

try:
    import dearpygui.dearpygui as dpg
    DPG_WORKS = True
except ImportError:
    DPG_WORKS = False


# make config
TC_HOME = pathlib.Path.home() / ".toolcraft"
_config_file = TC_HOME / "config.toml"
if _config_file.exists():
    TC_CONFIG = toml.load(_config_file.as_posix())
    if "dirs" not in TC_CONFIG.keys():
        raise Exception(
            f"Missing mandatory `dirs` setting in toolcraft config file at "
            f"`{_config_file.as_posix()}`"
        )
else:
    raise Exception(
        f"missing toolcraft config file at {_config_file.as_posix()}"
    )

STATIC_CODE_CHECK = TC_CONFIG['STATIC_CODE_CHECK']


_root_dnd = pathlib.Path(TC_CONFIG["dirs"]["DND"])
_root_del = pathlib.Path(TC_CONFIG["dirs"]["DEL"])
if not _root_dnd.exists():
    _root_dnd.mkdir(parents=True, exist_ok=True)
if not _root_del.exists():
    _root_del.mkdir(parents=True, exist_ok=True)


class Dir:
    ROOT_DND = _root_dnd
    ROOT_DEL = _root_del
    DOWNLOAD = ROOT_DND / "Download"
    TEMPORARY = ROOT_DEL / "_tmp"


class FileHash:
    # time interval between to check hashes on disk
    # note that this is a list ... any one of the values in list will be picked
    # for determining if to do hash check or not ... this distributes the hash
    # check over time so that there is no time slogging
    _MIN_HOURS = 10 * 24  # 10 days
    _MAX_HOURS = 15 * 24  # 15 days
    CHECK_INTERVALS_IN_SEC = \
        np.arange(_MIN_HOURS, _MAX_HOURS, 3) * 60 * 60
    # CHECK_INTERVALS_IN_SEC = [1]

    # when you want to debug if auto_hashing feature creates same files in
    # consecutive runs
    DEBUG_HASHABLE_STATE = False
