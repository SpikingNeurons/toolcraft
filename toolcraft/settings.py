"""
todo: Formalize with a parent Settings class which will store settings in
  `.toolcraft` folder
"""

import numpy as np
import pathlib
import toml
import sys
# noinspection PyUnresolvedReferences,PyCompatibility
import __main__ as main


# check if debugger is used
DEBUGGING = False
gettrace = getattr(sys, 'gettrace', None)
if gettrace is not None:
    if gettrace():
        DEBUGGING = True

# detect if in interactive mode
INTERACTIVE = not hasattr(main, '__file__')

try:
    import dearpygui.dearpygui as dpg
    DPG_WORKS = True
except ImportError:
    DPG_WORKS = False


# make config
_config_file = pathlib.Path.home() / ".toolcraft" / "config.toml"
if _config_file.exists():
    _config_data = toml.load(_config_file.as_posix())
    _root_dnd = pathlib.Path(_config_data["dirs"]["DND"])
    _root_del = pathlib.Path(_config_data["dirs"]["DEL"])
    if not _root_dnd.exists():
        _root_del.mkdir(parents=True, exist_ok=True)
    if not _root_del.exists():
        _root_del.mkdir(parents=True, exist_ok=True)
else:
    raise Exception(
        f"Missing toolcraft config file at "
        f"{_config_file.as_posix()}"
    )


class Dir:
    ROOT_DND = _root_dnd
    ROOT_DEL = _root_del
    DOWNLOAD = ROOT_DND / "Download"
    TEMPORARY = ROOT_DEL / "_tmp"
    LOG = ROOT_DEL / "log"


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
