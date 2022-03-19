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
from ..dapr import Dapr

_LOGGER = logger.get_logger()


def launch_dapr_app():
    """
    Why pickle ??
      + client is made up of python so there is no reason not to use pickle
      + With respect to pyarrow Table
        pa.serialize and pa.deserialize is deprecated as pickle protocol 5
        supports everything ... so pickling is better way for us

    todo: stream large data (we need to figure this out)
      + look for https://arrow.apache.org/docs/python/ipc.html
      + also lookout for pyarrow flight which uses grpc but also has more
        capability of reading dataframe from multiple servers

    todo: DaprClient.invoke_method data kwarg is used to send kwargs for hashable method
      Note that they are serialized with json.dumps instead of pickle.dumps as there
      is encoding problem ... as of now request data sent to server will be small so
      we might not need to worry

    """

    # detect if called from main
    # noinspection PyUnresolvedReferences,PyProtectedMember
    _mod = sys._getframe(1).f_globals["__name__"]
    if _mod != '__main__':
        raise e.validation.NotAllowed(
            msgs=[
                f"Function {launch_dapr_app} is intended to be called from __main__ "
                f"of your main script"
            ]
        )

    # get script path
    _script_path = pathlib.Path(
        traceback.extract_stack(limit=4)[-2].filename
    )

    # import script ... no need as the main script will handle it
    # _module_name = _script_path.name.split(".")[0]
    # importlib.import_module(_module_name)



    # set the session dir
    _session_name = _script_path.name.split(".")[0]
    if settings.DAPR_SESSION_DIR is None:
        settings.DAPR_SESSION_DIR = _script_path.parent / _session_name
    else:
        raise e.code.CodingError(
            msgs=[
                f"There is already a session running with name `{_session_name}`"
            ]
        )

    # log before launch
    _LOGGER.info(
        msg=f"Running DAPR app `hashable-receiver` in dir {_script_path.parent}"
    )
    _LOGGER.info(
        msg=f"Listen to this IP {socket.gethostbyname(socket.gethostname())}:{_DAPR_PORT}"
    )

    # launch
    _DAPR_APP.run(app_port=_DAPR_PORT)


class DaprTool(Tool):
    """
    This will launch toolcraft in server mode on remote machines
    It will update settings to indicate serving mode ...
    We will also disable any gui ... as servers will not render gui
    """

    @classmethod
    def command_fn(
        cls, py_script: pathlib.Path, task_type: t.Literal['serve', 'view', 'launch'],
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
            msgs=[{'py_script': py_script.as_posix(), 'task_type': task_type}]
        )

        # final call to dapr sidecar
        if task_type == 'server':
            os.system(
                f"dapr run "
                f"--app-id hashable-receiver "
                f"--app-protocol grpc "
                f"--app-port {Dapr.PORT} "
                f"python {py_script.absolute().as_posix()} server"
            )
        elif task_type == 'view':
            os.system(
                f"dapr run "
                f"--app-id hashable-caller "
                f"--app-protocol grpc "
                f"python {py_script.absolute().as_posix()} client"
            )
        elif task_type == 'launch':
            os.system(
                f"python {py_script.absolute().as_posix()} launch"
            )
        else:
            raise e.validation.NotAllowed(
                msgs=[f"Unknown task_type: {task_type}"]
            )
