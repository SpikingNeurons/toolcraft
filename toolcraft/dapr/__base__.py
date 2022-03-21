import os
import enum
import pathlib
import typing as t
from dapr.ext.grpc import App
import sys
import socket
import logging
from dapr.clients import DaprClient

from .. import logger
from .. import error as e
from .. import marshalling as m

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from .. import gui
    from . import helper

_LOGGER = logger.get_logger()


class DaprMode(enum.Enum):
    server = enum.auto()
    launch = enum.auto()
    client = enum.auto()

    @property
    def log_file(self) -> pathlib.Path:
        return Dapr.CWD / f"{self.name}.log"

    @classmethod
    def from_str(cls, dapr_mode: str) -> "DaprMode":
        try:
            return cls[dapr_mode]
        except KeyError:
            raise e.code.CodingError(
                msgs=[f"unknown dapr mode {dapr_mode}",
                      {"allowed strs": [_.name for _ in cls]}]
            )


class Dapr:

    CWD: pathlib.Path = None
    IP: str = None
    GRPC_PORT: int = 50051
    HTTP_PORT: int = 3500
    APP = App()
    MODE: DaprMode = None
    SERVER: "helper.Server" = None
    APP_ID_SERVER = "hashable-server"
    APP_ID_CLIENT = "hashable-client"

    @classmethod
    def as_dict(cls) -> t.Dict:
        return {
            'CWD': Dapr.CWD.as_posix(),
            'IP': Dapr.IP,
            'GRPC_PORT': Dapr.GRPC_PORT,
            'HTTP_PORT': Dapr.HTTP_PORT,
            'MODE': Dapr.MODE.name,
        }

    @classmethod
    def dapr_launch(cls, dapr_mode: str, py_script: pathlib.Path):

        _dapr_mode = DaprMode.from_str(dapr_mode=dapr_mode)

        if _dapr_mode is DaprMode.server:
            os.system(
                f"dapr run "
                f"--app-id {Dapr.APP_ID_SERVER} "
                f"--app-protocol grpc "
                f"--app-port {Dapr.GRPC_PORT} "
                f"python {py_script.absolute().as_posix()} server"
            )
        elif _dapr_mode is DaprMode.client:
            os.system(
                f"dapr run "
                f"--app-id {Dapr.APP_ID_CLIENT} "
                f"--app-protocol grpc "
                f"python {py_script.absolute().as_posix()} client"
            )
        elif _dapr_mode is DaprMode.launch:
            os.system(
                f"python {py_script.absolute().as_posix()} launch"
            )
        else:
            raise e.code.NotSupported(
                msgs=[f"Unsupported dapr mode: {_dapr_mode}"]
            )

    @classmethod
    def get_client(cls) -> DaprClient:
        print(f"{cls.IP}:{cls.GRPC_PORT}", ".....................")
        return DaprClient(
            address=f"{cls.IP}:{cls.GRPC_PORT}"
        )

    @classmethod
    def setup_logging(cls):
        logger.setup_logging(
            propagate=False,
            level=logging.NOTSET,
            handlers=[
                logger.get_rich_handler(),
                logger.get_file_handler(cls.MODE.log_file),
            ],
        )

    def __new__(cls, *args, **kwargs):
        raise e.code.NotAllowed(msgs=[
            f"This class is meant to be used to hold class "
            f"variables only",
            f"Do not try to create instance of {cls} ...",
        ])


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

    def __new__(cls, *args, **kwargs):
        raise e.code.NotAllowed(msgs=[
            f"This class is meant to be used to as it is ...",
            f"Do not try to create instance of {cls} ...",
        ])

    @classmethod
    def _start(cls):
        """
        Some things to do at the start ...
        """

        # show which hashables can be serverd by this server
        _hcs = m.HashableClass.available_concrete_sub_classes()
        _LOGGER.info(
            msg=f"Below {len(_hcs)} hashable classes are available ",
            msgs=[f"{_hc}" for _hc in _hcs]
        )

    @classmethod
    def server(cls):
        """
        Responsible to launch dapr server
        """
        cls._start()
        _LOGGER.info(
            "Dapr server started ...",
            msgs=[Dapr.as_dict()])
        Dapr.APP.run(Dapr.GRPC_PORT)

    @classmethod
    def client(cls):
        """
        To be used on clients
        """
        cls._start()
        _LOGGER.info(
            "Running client ...",
            msgs=[Dapr.as_dict()])

    @classmethod
    def launch(cls):
        """
        will launch jobs on server
        """
        cls._start()
        _LOGGER.info(
            "Launching jobs on server ...",
            msgs=[Dapr.as_dict()])

    @classmethod
    def make_dashboard(
        cls, callable_name: str,
    ) -> "gui.dashboard.DaprClientDashboard":
        from .. import gui
        return gui.dashboard.DaprClientDashboard(
            title="Dapr Client Dashboard ...",
            subtitle=f"Will connect to: {Dapr.IP}:{Dapr.GRPC_PORT}",
            callable_name=callable_name,
        )

    @classmethod
    def run(cls):
        """
        This method should be called from __main__ of the script as it decides what
        to call next
        """

        # --------------------------------------------------- 01
        # if no arg passed assume client mode i.e. client
        if len(sys.argv) == 1:
            sys.argv.append('client')
        # validation
        if len(sys.argv) != 2:
            raise e.validation.NotAllowed(
                msgs=[
                    "Only pass one arg", sys.argv[1:]
                ]
            )
        _dapr_mode = DaprMode.from_str(dapr_mode=sys.argv[1])

        # --------------------------------------------------- 02
        # --------------------------------------------------- 02.01
        # set CWD
        if Dapr.CWD is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.CWD` to be set ...",
                      f"It is currently set to: {Dapr.CWD}"]
            )
        else:
            Dapr.CWD = pathlib.Path(sys.argv[0]).parent
        _LOGGER.info(msg="Dapr current working dir set to: ", msgs=[str(Dapr.CWD)])
        # --------------------------------------------------- 02.02
        # set dapr mode
        if Dapr.MODE is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.MODE` to be set ...",
                      f"Is currently set to: {Dapr.MODE}"]
            )
        else:
            Dapr.MODE = _dapr_mode
        # --------------------------------------------------- 02.03
        # set IP
        if Dapr.IP is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.IP` to be set ...",
                      f"It is currently set to: {Dapr.IP}"]
            )
        if _dapr_mode in [DaprMode.server, DaprMode.launch]:
            Dapr.IP = str(socket.gethostbyname(socket.gethostname()))
        elif _dapr_mode is DaprMode.client:
            try:
                Dapr.IP = os.environ['NXDI']
                if Dapr.IP == "localhost":
                    # todo: find why this happens and if it can be done more elegantly
                    #   Check why this does not resolve to 127.0.0.1
                    # as localhost resolves to 127.0.0.1 and when SERVER is running
                    # on localhost the IP is actually different
                    Dapr.IP = str(socket.gethostbyname(socket.gethostname()))
            except KeyError:
                raise e.code.NotAllowed(
                    msgs=[f"Environment variable NXDI is not set ..."]
                )
        else:
            raise e.code.ShouldNeverHappen(msgs=[])
        # --------------------------------------------------- 02.04
        # set reference to server ... only for client mode
        if Dapr.SERVER is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.SERVER` to be set ...",
                      f"It is currently set to: {Dapr.SERVER}"]
            )
        if _dapr_mode is DaprMode.client:
            from . import helper
            Dapr.SERVER = helper.Server()
        # --------------------------------------------------- 02.05
        # set logging
        Dapr.setup_logging()

        # --------------------------------------------------- 03
        # launch task
        if _dapr_mode is DaprMode.launch:
            cls.launch()
        elif _dapr_mode is DaprMode.server:
            cls.server()
        elif _dapr_mode is DaprMode.client:
            cls.client()
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown {_dapr_mode}"])
