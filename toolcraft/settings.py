"""
todo: Formalize with a parent Settings class which will store settings in
  `.toolcraft` folder
"""
import numpy as np
import pyarrow as pa  # do not comment this as on unix it causes seg fault
import pathlib
import platform
import toml
import typing as t
import sys
# noinspection PyUnresolvedReferences,PyCompatibility
import __main__ as main

DO_RULE_CHECK = True

ENV_DIR = pathlib.Path(sys.exec_prefix)

try:
    import dearpygui.dearpygui as dpg
    DPG_WORKS = True
    # todo: instead of import call some code in dearpygui to raise errors ... so that in except block
    #   we can set `DPG_WORKS = False`
except ImportError:
    DPG_WORKS = False


# platform
PLATFORM = platform.uname()  # type: platform.uname_result


# check if debugger is used
PYC_DEBUGGING = False
gettrace = getattr(sys, 'gettrace', None)
if gettrace is not None:
    if gettrace():
        PYC_DEBUGGING = True

# detect if in interactive mode
INTERACTIVE = not hasattr(main, '__file__')

LOGGER_USE_FILE_HANDLER = False

try:
    from keras.api._v2 import keras as tk
    import tensorflow as tf
    TF_KERAS_WORKS = True
except ImportError:
    TF_KERAS_WORKS = False


# make config
TC_HOME = pathlib.Path.home() / ".toolcraft"
if not TC_HOME.exists():
    TC_HOME.mkdir(parents=True)
TC_CONFIG_FILE = TC_HOME / "config.toml"
if not TC_CONFIG_FILE.exists():
    TC_CONFIG_FILE.touch()
TC_CONFIG = toml.load(TC_CONFIG_FILE.as_posix())


class FileHash:
    # time interval between to check hashes on disk
    # note that this is a list ... any one of the values in list will be picked
    # for determining if to do hash check or not ... this distributes the hash
    # check over time so that there is no time slogging
    _MIN_HOURS = 10 * 24  # 10 days
    _MAX_HOURS = 15 * 24  # 15 days
    CHECK_INTERVALS_IN_SEC = list(np.arange(_MIN_HOURS, _MAX_HOURS, 3) * 60 * 60)
    # CHECK_INTERVALS_IN_SEC = [1]

    # when you want to debug if auto_hashing feature creates same files in
    # consecutive runs
    DEBUG_HASHABLE_STATE = False

