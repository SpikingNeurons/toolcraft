"""
module to hold helper classes to be used by our `toolcraft.dapr` module
"""
import os
import dataclasses
import typing as t

from .. import marshalling as m
from .. import error as e
from .. import logger
from . import invoke
from .__base__ import DaprMode

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class Server(m.HashableClass):
    """
    Use this class to query or retrieve any stats from server ...
    """
    @property
    def group_by(self) -> t.List[str]:
        return ["server"]

    @invoke.Invoke()
    def read_logs(self, num_bytes: int, dapr_mode: str) -> str:
        _log_file = DaprMode.from_str(dapr_mode).log_file
        if not _log_file.exists():
            return f"Log file `{_log_file.as_posix()}` not yet created ..."
        try:
            _file_size = os.stat(_log_file).st_size
            with _log_file.open(mode='rb') as _f:
                # for fast read we seek to read only last chunk of data
                if _file_size > num_bytes:
                    _f.seek(-num_bytes, os.SEEK_END)
                return _f.read().decode()
        except Exception as _ex:
            return f"Some error occurred while reading \n" \
                   f"log file {_log_file.as_posix()}: \n\n {_ex}"
