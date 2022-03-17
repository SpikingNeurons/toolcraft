"""
This module might eventually become `mlcraft`


"""
import dataclasses
import pathlib
import typing as t

from . import marshalling as m
from . import util
from . import settings
from . import logger


_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class Runner(m.HashableClass):
    """
    Note that this class is at mercy of dapr module and can be used only with
    toolcraft tool `dapr` which is run on server
    """

    @property
    @util.CacheResult
    def store_dir(self) -> pathlib.Path:
        if settings.DAPR_SERVE_MODE:
            return settings.DAPR_SESSION_DIR
        else:
            ...
