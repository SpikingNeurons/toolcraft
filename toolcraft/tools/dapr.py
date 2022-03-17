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

# noinspection PyTypeChecker
_DAPR_CWD = None  # type: pathlib.Path
_DAPR_PORT = 50051
_DAPR_APP = App()
_LOGGER = logger.get_logger()


@_DAPR_APP.method('hashable_receiver_invoke')
def hashable_receiver_invoke(request: InvokeMethodRequest) -> bytes:
    # get from request
    print("ggggggggggggggggggggggggggggggggggggggggggg")
    print(request)
    _metadata = request.metadata
    _data = json.loads(request.data)

    print(_data)

    # confirm if server knows about requested hashable
    _hex_hash = _data['hex_hash']
    _hashable_yaml = _DAPR_CWD / _hex_hash / ".yaml"
    if not _hashable_yaml.exists():
        if 'hashable_yaml' in _data.keys():
            _hashable_yaml.parent.mkdir(parents=True, exist_ok=True)
            _hashable_yaml.touch(exist_ok=False)
            _hashable_yaml.write_text(_data['hashable_yaml'])
        else:
            return HashableReceiverResponse(
                status=Status.NEEDS_HASHABLE_YAML,
                message="Please send hashable yaml ..."
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
        return self.status is Status.STARTED

    @property
    def results_available(self):
        return self.data is not None

    def get_bytes(self) -> bytes:
        return zlib.compress(pickle.dumps(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> "HashableReceiverResponse":
        return pickle.loads(zlib.decompress(data))


class HashableRunner:
    """

    todo: This class might eventually become ... `mlcraft`
      https://pypi.org/project/mlcraft/

    todo: `mlflow` and `wandb` are closest things to mlcraft
      + brainstorm USP of mlcraft
        + python gui direct access to memory IPC/Grpc/RDMA will be available
        + solid visual tools and in reach of python developers which shy away
          from javascript
        + capability to go grpc/http/ftp/ssh/gcs ... etc
        + dapr based side car architecture ... mix and match compute resources
        + powerful HashableClass that gives python user the control
        + heavy pyarrow usage for storing tables that can be stored across machines
          and queried with pyarrow ...
          also other things like GPU analytics, plasma (in memory store), IPC, RBMA will
          be there as pa.Table's

    todo: Models can be stored as artifact i.e. `storage.dec.FileGroup` but then to
      make it live or track its lifecycle get inspiration
      from https://mlflow.org/docs/latest/model-registry.html#

    todo: look at heron philosophy ... although here we are basically inspired by
      popular mlflow and want to use dapr https://github.com/georgedimitriadis/Heron
    """

    @classmethod
    def _start(cls):
        """
        Some things to do at the start ...
        """

        # show which hashables can be served by this server
        _hcs = m.HashableClass.available_concrete_sub_classes()
        _LOGGER.info(
            msg=f"Below {len(_hcs)} hashable classes are available ",
            msgs=[f"{_hc}" for _hc in _hcs]
        )

    @classmethod
    def serve(cls):
        """
        Responsible to launch dapr server
        """
        cls._start()
        _LOGGER.info("Dapr server started ...")
        _DAPR_APP.run(_DAPR_PORT)

    @classmethod
    def view(cls):
        """
        To be used on clients
        """
        cls._start()
        _LOGGER.info("Running client ...")

    @classmethod
    def launch(cls):
        """
        will launch jobs on server
        """
        cls._start()
        _LOGGER.info("Launching jobs on server ...")

    @classmethod
    def run(cls):
        """
        This method should be called from __main__ of the script as it decides what
        to call next
        """
        global _DAPR_CWD

        # --------------------------------------------------- 01
        # validation
        if len(sys.argv) != 2:
            raise e.validation.NotAllowed(
                msgs=[
                    "Only pass one arg", sys.argv[1:]
                ]
            )
        _task_type = sys.argv[1]
        e.validation.ShouldBeOneOf(
            value=_task_type, values=['serve', 'launch', 'view'],
            msgs=["Supply correct task type ..."]
        ).raise_if_failed()

        # --------------------------------------------------- 02
        # find CWD
        if _DAPR_CWD is not None:
            raise e.code.CodingError(
                msgs=["We do not expect _DAPR_CWD to be set ...",
                      f"Found _DAPR_CWD = {_DAPR_CWD}"]
            )
        else:
            _DAPR_CWD = pathlib.Path(sys.argv[0]).parent
        _LOGGER.info(msg="Dapr current working dir set to: ", msgs=[str(_DAPR_CWD)])

        # --------------------------------------------------- 03
        # launch task
        if _task_type == 'launch':
            cls.launch()
        elif _task_type == "serve":
            cls.serve()
        elif _task_type == "view":
            cls.view()
        else:
            raise e.validation.NotAllowed(msgs=[f"Unsupported task_type {_task_type}"])


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
        if task_type == 'serve':
            os.system(
                f"dapr run "
                f"--app-id hashable-receiver "
                f"--app-protocol grpc "
                f"--app-port {_DAPR_PORT} "
                f"python {py_script.absolute().as_posix()} serve"
            )
        elif task_type == 'view':
            os.system(
                f"dapr run "
                f"--app-id hashable-caller "
                f"--app-protocol grpc "
                f"python {py_script.absolute().as_posix()} view"
            )
        elif task_type == 'launch':
            os.system(
                f"python {py_script.absolute().as_posix()} launch"
            )
        else:
            raise e.validation.NotAllowed(
                msgs=[f"Unknown task_type: {task_type}"]
            )
