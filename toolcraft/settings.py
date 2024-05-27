"""
todo: Formalize with a parent Settings class which will store settings in
  `.toolcraft` folder
"""
import numpy as np
import pyarrow as pa  # do not comment this as on unix it causes seg fault
import pathlib
import shutil
import typing as t
import sys
import toml
# noinspection PyUnresolvedReferences,PyCompatibility
import __main__ as main

from . import storage as s

class Settings:

    TC_HOME = pathlib.Path.home() / ".toolcraft"
    TC_CONFIG_FILE = None  # type: pathlib.Path
    TC_CONFIG = None  # type: t.Dict[str, t.Any]

    IS_LSF_MACHINE = bool(shutil.which('bjobs'))
    PYC_DEBUGGING = None  # type: bool

    FILE_SYSTEMS = dict(
        CWD=s.LocalFileSystem(),
    )  # type: t.Dict[str, s.BaseFileSystem]

    # detect if in interactive mode
    INTERACTIVE = not hasattr(main, '__file__')

    # 260 is for windows ... leave 60 for arrow storage
    # todo: adapt code based on OS platform
    FILE_SYSTEMS_PATH_LENGTH = 260 - 60


    # time interval between to check hashes on disk
    # note that this is a list ... any one of the values in list will be picked
    # for determining if to do hash check or not ... this distributes the hash
    # check over time so that there is no time slogging
    CHECK_MIN_HOURS = 100 * 24  # 100 days
    CHECK_MAX_HOURS = 200 * 24  # 200 days
    CHECK_INTERVALS_IN_SEC = list(np.arange(CHECK_MIN_HOURS, CHECK_MAX_HOURS, 3) * 60 * 60)
    # CHECK_INTERVALS_IN_SEC = [1]

    # when you want to debug if auto_hashing feature creates same files in
    # consecutive runs
    DEBUG_HASHABLE_STATE = False

    DO_RULE_CHECK = True
    LOGGER_USE_FILE_HANDLER = False

    @classmethod
    def fields_not_to_be_persisted(cls) -> [str]:
        return [
            "TC_HOME", "TC_CONFIG_FILE", "TC_CONFIG",
            "IS_LSF_MACHINE", "PYC_DEBUGGING", "INTERACTIVE",
            "CHECK_INTERVALS_IN_SEC", "FILE_SYSTEMS",
        ]

    @classmethod
    def load_and_init_fields(cls):

        # check if debugger is used
        cls.PYC_DEBUGGING = False
        gettrace = getattr(sys, 'gettrace', None)
        if gettrace is not None:
            if gettrace():
                cls.PYC_DEBUGGING = True

        # load class fields from settings file
        if not cls.TC_HOME.exists():
            cls.TC_HOME.mkdir(parents=True)
        cls.TC_CONFIG_FILE = cls.TC_HOME / "config.toml"
        if not cls.TC_CONFIG_FILE.exists():
            cls.TC_CONFIG_FILE.touch()
        _config = toml.load(cls.TC_CONFIG_FILE.as_posix())
        for _k, _v in _config.items():
            if _k in cls.__dict__.keys():
                setattr(cls, _k, _v)
            elif _k in cls.fields_not_to_be_persisted():
                raise KeyError(f"Key {_k} in config file is supposed to be not persisted ... Please check code for bugs")
            else:
                raise ValueError(f"Unknown key {_k} in config file")

    @classmethod
    def persist_fields(cls):
        _config = {}
        _fields_not_to_be_persisted = cls.fields_not_to_be_persisted()
        for _k, _v in cls.__dict__.items():
            if _k in _fields_not_to_be_persisted or _k.startswith("_") or callable(_v) or isinstance(_v, (classmethod, property, staticmethod)):
                continue
            _config[_k] = _v
        toml.dump(_config, cls.TC_CONFIG_FILE.open('w'))

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.load_and_init_fields()
        cls.persist_fields()


# this happens at toolcraft library level
# if you override Settings in your library then __init_subclass__ will be triggered
# which in turn sets the fields for your library
Settings.__init_subclass__()
