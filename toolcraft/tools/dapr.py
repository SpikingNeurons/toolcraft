
import pathlib
import typer
import socket
import shutil
import importlib
import typing as t
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
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

_PORT = 50051
_DAPR_APP = App()


class Status(enum.Enum):
    NEEDS_HASHABLE_YAML = enum.auto()
    STARTED = enum.auto()
    PROCESSING = enum.auto()
    COMPLETED = enum.auto()


class HashableReceiverResponse(t.NamedTuple):
    """
    Extend this class to provide more methods that can be used to build gui etc.
    But note that we cannot add more fields to this tuple and might not be needed as
      simple design is best ...

    todo: In long run we will remove pickle and see if the tuple can be sent as json
       with the data as protobuf which can be deserialized on client
       {
          'class_name': <>,
          'module_name': <>,
          'data': <protobuf>,
       }
    """
    status: Status
    message: str
    data: t.Union[pa.Table, t.Dict] = None

    @property
    def is_completed(self):
        return self.status is Status.COMPLETED

    @property
    def is_processing(self):
        return self.status in [Status.PROCESSING, Status.STARTED]

    @property
    def just_started(self):
        """
        Use on first invoke ...
        """
        return self.status is Status.STARTED

    @property
    def results_available(self):
        return self.data is not None

    def get_bytes(self) -> bytes:
        return zlib.compress(pickle.dumps(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> "HashableReceiverResponse":
        return pickle.loads(zlib.decompress(data))


@_DAPR_APP.method('hashable_receiver_invoke')
def hashable_receiver_invoke(request: InvokeMethodRequest) -> bytes:
    # get from request
    _metadata = request.metadata
    _data = json.loads(request.data)

    # confirm if server knows about requested hashable
    _hex_hash = _data['hex_hash']
    _hashable_yaml = settings.DAPR_SESSION_DIR / _hex_hash / ".yaml"
    if not _hashable_yaml.exists():
        if 'hashable_yaml' in _data.keys():
            _hashable_yaml.parent.mkdir(parents=True, exist_ok=True)
            _hashable_yaml.touch(exist_ok=False)
            _hashable_yaml.write_text(_data['hashable_yaml'])
        else:
            return HashableReceiverResponse(
                status=Status.NEEDS_HASHABLE_YAML, message="Please send hashable yaml ..."
            ).get_bytes()

    # load hashable
    print(_hashable_yaml)
    return HashableReceiverResponse(
        status=Status.STARTED, message="Just started"
    ).get_bytes()


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
        typer.echo(f"Function {launch_dapr_app} is intended to be called from __main__ "
                   f"of your main script")
        raise typer.Abort()

    # get script path
    _script_path = pathlib.Path(
        traceback.extract_stack(limit=4)[-2].filename
    )

    # check if script is called from same dir
    if pathlib.Path.cwd() != _script_path.parent:
        typer.echo(f"The script dir is {_script_path.parent.as_posix()}")
        typer.echo(f"While current working dir is {pathlib.Path.cwd().as_posix()}")
        typer.echo(f"We expect both to match ... please call this script from "
                   f"same dir as `{_script_path.name}`")
        raise typer.Abort()

    # import script ... no need as the main script will handle it
    # _module_name = _script_path.name.split(".")[0]
    # importlib.import_module(_module_name)

    # show which hashables can be served by this server
    _hcs = m.HashableClass.available_concrete_sub_classes()
    typer.echo(f"Below {len(_hcs)} classes are supported by this server")
    for _hc in _hcs:
        typer.echo(f"  >> {_hc}")

    # indicates that toolcraft and libs/apps that will use it are running on server
    if settings.DAPR_SERVE_MODE:
        typer.echo("This is coding error ...")
        typer.echo(f"Setting DAPR_SERVE_MODE was not expected to be set to True ")
        raise typer.Abort()
    settings.DAPR_SERVE_MODE = True

    # set the session dir
    _session_name = _script_path.name.split(".")[0]
    if settings.DAPR_SESSION_DIR is None:
        settings.DAPR_SESSION_DIR = _script_path.parent / _session_name
    else:
        typer.echo("This is some bug ...")
        typer.echo(f"There is already a session running with name "
                   f"`{_session_name}`")
        raise typer.Abort()

    # log before launch
    typer.echo(f"Running DAPR app hashable-receiver in dir {_script_path.parent}")
    typer.echo(
        f"Listen to this IP {socket.gethostbyname(socket.gethostname())}:{_PORT}")

    print("gffffffffffffff")


class DaprTool(Tool):
    """
    This will launch toolcraft in server mode on remote machines
    It will update settings to indicate serving mode ...
    We will also disable any gui ... as servers will not render gui
    """

    @classmethod
    def command_fn(
        cls,
        py_script: pathlib.Path = typer.Argument(
            default=...,
            help="Python script to run",
        ),
    ):

        # todo: add git version check for toolcraft and any library that uses toolcraft
        #   This ensures that the client and server libraries are in sync
        #   Refer mlflow to see if this can be done

        # check if python script available
        if not py_script.exists():
            typer.echo(f"Cannot find py_script {py_script.absolute().as_posix()}")
            raise typer.Abort()

        # check if dapr installed
        if shutil.which("dapr") is None:
            typer.echo("dapr is not installed")
            raise typer.Abort()

        # log details
        typer.echo(f"Called tool {cls.tool_name()}")

        # final call to dapr sidecar
        os.system(
            f"dapr run "
            f"--app-id hashable-receiver "
            f"--app-protocol grpc "
            f"--app-port {_PORT} "
            f"-- "
            # here we call code from python directly
            f"python {py_script.absolute().as_posix()}"
        )
