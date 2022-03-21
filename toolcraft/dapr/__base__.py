import dataclasses
import os
import enum
import pathlib
import typing as t
import sys
import socket
import logging
import dapr
from dapr import clients
from dapr.ext.grpc import App

from .. import logger
from .. import error as e
from .. import util
from .. import marshalling as m

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from .. import gui
    from . import helper

_LOGGER = logger.get_logger()


class DaprMode(m.FrozenEnum, enum.Enum):
    server = enum.auto()
    launch = enum.auto()
    client = enum.auto()

    @property
    def log_file_name(self) -> str:
        return f"{self.name}.log"

    @classmethod
    def from_str(cls, dapr_mode: str) -> "DaprMode":
        try:
            return cls[dapr_mode]
        except KeyError:
            raise e.code.CodingError(
                msgs=[f"unknown dapr mode {dapr_mode}",
                      {"allowed strs": [_.name for _ in cls]}]
            )


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['app', 'server', 'log_file'],
    things_not_to_be_cached=['client'],
)
class _Dapr(m.HashableClass):
    """
    Refer for dapr settings
    >>> dapr.conf.global_settings
    >>> dapr.conf.settings
    """

    # our settings
    PY_SCRIPT: str
    MODE: DaprMode
    APP_ID_SERVER: str = "hashable-server"
    APP_ID_CLIENT: str = "hashable-client"

    # dapr related settings
    DAPR_RUNTIME_HOST: str = '127.0.0.1'
    APP_PORT: int = 2008
    # HTTP_APP_PORT: int = 3000
    # GRPC_APP_PORT: int = 3010
    # DAPR_HTTP_PORT: int = 3500
    # DAPR_GRPC_PORT: int = 50001
    DAPR_API_TOKEN: str = None
    DAPR_API_VERSION: str = 'v1.0'
    DAPR_API_METHOD_INVOCATION_PROTOCOL: t.Literal['grpc', 'http'] = 'grpc'
    DAPR_HTTP_TIMEOUT_SECONDS: int = 60

    @property
    def cwd(self) -> pathlib.Path:
        return pathlib.Path(self.PY_SCRIPT).parent

    @property
    @util.CacheResult
    def app(self) -> "App":
        return App()

    @property
    def client(self) -> "clients.DaprClient":
        if self.MODE is not DaprMode.client:
            raise e.code.NotAllowed(
                msgs=[f"Use client property only for {DaprMode.client}"]
            )
        return clients.DaprClient(
            # f"{self.DAPR_RUNTIME_HOST}:{self.DAPR_GRPC_PORT}"
        )

    @property
    @util.CacheResult
    def log_file(self) -> pathlib.Path:
        return self.cwd / self.MODE.log_file_name

    @property
    @util.CacheResult
    def server(self) -> "helper.Server":
        from . import helper
        if self.MODE is not DaprMode.client:
            raise e.code.NotAllowed(
                msgs=[f"Use server property only for {DaprMode.client}"]
            )
        return helper.Server()

    def init(self):

        # sync settings
        self.sync_with_dapr_settings()

        # setup logging
        logger.setup_logging(
            propagate=False,
            level=logging.INFO,
            handlers=[
                logger.get_rich_handler(),
                logger.get_stream_handler(),
                logger.get_file_handler(self.log_file),
            ],
        )

    def dapr_launch(self, py_script: pathlib.Path):

        _dapr_mode = self.MODE

        if _dapr_mode is DaprMode.server:
            os.system(
                f"dapr run "
                f"--app-id {DAPR.APP_ID_SERVER} "
                f"--app-protocol grpc "
                f"--app-port {DAPR.APP_PORT} "
                f"-- "
                f"python {py_script.absolute().as_posix()} server"
            )
        elif _dapr_mode is DaprMode.client:
            os.system(
                f"dapr run "
                f"--app-id {DAPR.APP_ID_CLIENT} "
                f"--app-protocol grpc "
                f"--app-port {DAPR.APP_PORT} "
                f"-- "
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

    def sync_with_dapr_settings(self):
        # todo: this is not elegant but dapr python-sdk is still not mature ...
        #  track things when version > 1.5.0 and update
        _settings = dapr.conf.settings
        _settings.DAPR_RUNTIME_HOST = self.DAPR_RUNTIME_HOST
        # _settings.HTTP_APP_PORT = self.HTTP_APP_PORT
        # _settings.GRPC_APP_PORT = self.GRPC_APP_PORT
        # _settings.DAPR_HTTP_PORT = self.DAPR_HTTP_PORT
        # _settings.DAPR_GRPC_PORT = self.DAPR_GRPC_PORT
        _settings.DAPR_API_TOKEN = self.DAPR_API_TOKEN
        _settings.DAPR_API_VERSION = self.DAPR_API_VERSION
        _settings.DAPR_API_METHOD_INVOCATION_PROTOCOL = \
            self.DAPR_API_METHOD_INVOCATION_PROTOCOL
        _settings.DAPR_HTTP_TIMEOUT_SECONDS = self.DAPR_HTTP_TIMEOUT_SECONDS

    @classmethod
    def make(cls) -> "_Dapr":
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

        # --------------------------------------------------- 02
        # get some vars
        # --------------------------------------------------- 02.01
        # get cwd
        _py_script = sys.argv[0]
        # --------------------------------------------------- 02.02
        # get mode
        _dapr_mode = DaprMode.from_str(dapr_mode=sys.argv[1])
        # --------------------------------------------------- 02.03
        # get dapr_runtime_host
        if _dapr_mode in [DaprMode.server, DaprMode.launch]:
            _dapr_runtime_host = str(socket.gethostbyname(socket.gethostname()))
        elif _dapr_mode is DaprMode.client:
            try:
                _dapr_runtime_host = os.environ['NXDI']
                if _dapr_runtime_host == "localhost":
                    # todo: find why this happens and if it can be done more elegantly
                    #   Check why this does not resolve to 127.0.0.1
                    # as localhost resolves to 127.0.0.1 and when SERVER is running
                    # on localhost the IP is actually different
                    # _dapr_runtime_host = \
                    #     str(socket.gethostbyname(socket.gethostname()))
                    _dapr_runtime_host = "127.0.0.1"
            except KeyError:
                raise e.code.NotAllowed(
                    msgs=[f"Environment variable NXDI is not set ..."]
                )
        else:
            raise e.code.ShouldNeverHappen(msgs=[])
        # --------------------------------------------------- 02.05
        # create _Dapr instance and return
        return _Dapr(PY_SCRIPT=_py_script, MODE=_dapr_mode,
                     DAPR_RUNTIME_HOST=_dapr_runtime_host)


DAPR = _Dapr.make()  # type: _Dapr


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
            msgs=[DAPR.as_dict()])
        DAPR.app.run(app_port=DAPR.APP_PORT)

    @classmethod
    def client(cls):
        """
        To be used on clients
        """
        cls._start()
        _LOGGER.info(
            "Running client ...",
            msgs=[DAPR.as_dict()])

    @classmethod
    def launch(cls):
        """
        will launch jobs on server
        """
        cls._start()
        _LOGGER.info(
            "Launching jobs on server ...",
            msgs=[DAPR.as_dict()])

    @classmethod
    def make_dashboard(
        cls, callable_name: str,
    ) -> "gui.dashboard.DaprClientDashboard":
        from .. import gui
        return gui.dashboard.DaprClientDashboard(
            title="Dapr Client Dashboard ...",
            subtitle=f"Will connect to: {DAPR.DAPR_RUNTIME_HOST}:{DAPR.DAPR_GRPC_PORT}",
            callable_name=callable_name,
        )

    @classmethod
    def run(cls):
        """
        This method should be called from __main__ of the script as it decides what
        to call next
        """
        global DAPR
        # launch task
        _dapr_mode = DAPR.MODE
        if _dapr_mode is DaprMode.launch:
            cls.launch()
        elif _dapr_mode is DaprMode.server:
            cls.server()
        elif _dapr_mode is DaprMode.client:
            cls.client()
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown {_dapr_mode}"])
