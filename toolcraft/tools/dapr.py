"""
todo: Maybe some of this will become mlcraft
  https://pypi.org/project/mlcraft/
"""
import pathlib
import socket
import shutil
import typing as t
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from dapr.conf import settings as dapr_settings
import os
import pickle
import enum
import zlib
import pyarrow as pa
import json
import traceback
import sys

from . import Tool
from .. import settings
from .. import marshalling as m
from .. import richy
from .. import error as e
from .. import logger
from ..dapr import DAPR

_LOGGER = logger.get_logger()


class DaprTool(Tool):
    """
    This will launch toolcraft in server mode on remote machines
    It will update settings to indicate serving mode ...
    We will also disable any gui ... as servers will not render gui
    """

    @classmethod
    def command_fn(
        cls, py_script: pathlib.Path, dapr_mode: t.Literal['serve', 'view', 'launch'],
    ):

        # todo: add git version check for toolcraft and any library that uses toolcraft
        #   This ensures that the client and server libraries are in sync
        #   Refer mlflow to see if this can be done

        # check if python script available
        e.io.FileMustBeOnDiskOrNetwork(
            path=py_script, msgs=["Please supply python script ..."]
        ).raise_if_failed()

        # check if dapr installed
        if shutil.which("dapr") is None:
            raise e.code.NotAllowed(
                msgs=["dapr is not available on this system"]
            )

        # check if script is called from same dir
        _cwd = pathlib.Path.cwd().absolute().resolve().as_posix()
        _script_dir = py_script.parent.absolute().resolve().as_posix()
        if _cwd != _script_dir:
            raise e.validation.NotAllowed(
                msgs=[
                    "Improper current working dir ...",
                    f"Script dir is {_script_dir}",
                    f"Current working dir is {_cwd}",
                    f"We expect both to match ...",
                    f"Please call this script from same dir as `{py_script.name}`"
                ]
            )

        # log details
        _LOGGER.info(
            msg=f"Calling tool {cls.tool_name()} for",
            msgs=[{'py_script': py_script.as_posix(), 'dapr_mode': dapr_mode}]
        )

        # final call to dapr sidecar
        DAPR.dapr_launch(py_script=py_script)
