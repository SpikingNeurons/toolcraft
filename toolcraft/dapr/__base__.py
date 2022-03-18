import pathlib
import typing as t
from dapr.ext.grpc import App
import sys

from .. import logger
from .. import error as e
from .. import marshalling as m

_LOGGER = logger.get_logger()


class Dapr:

    CWD: pathlib.Path = None
    PORT: int = 50051
    APP = App()
    MODE: t.Literal['server', 'launch', 'client'] = None

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
        _LOGGER.info("Dapr server started ...")
        Dapr.APP.run(Dapr.PORT)

    @classmethod
    def client(cls):
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
        _dapr_mode = sys.argv[1]
        e.validation.ShouldBeOneOf(
            value=_dapr_mode, values=['server', 'launch', 'client'],
            msgs=["Supply correct task type ..."]
        ).raise_if_failed()

        # --------------------------------------------------- 02
        # --------------------------------------------------- 02.01
        # find CWD
        if Dapr.CWD is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.CWD` to be set ...",
                      f"Is set to: {Dapr.CWD}"]
            )
        else:
            Dapr.CWD = pathlib.Path(sys.argv[0]).parent
        _LOGGER.info(msg="Dapr current working dir set to: ", msgs=[str(Dapr.CWD)])
        # --------------------------------------------------- 02.02
        # set dapr mode
        if Dapr.MODE is not None:
            raise e.code.CodingError(
                msgs=["We do not expect `Dapr.MODE` to be set ...",
                      f"Is set to: {Dapr.MODE}"]
            )
        else:
            Dapr.MODE = _dapr_mode

        # --------------------------------------------------- 03
        # launch task
        if _dapr_mode == 'launch':
            cls.launch()
        elif _dapr_mode == "server":
            cls.server()
        elif _dapr_mode == "client":
            cls.client()
        else:
            raise e.validation.NotAllowed(msgs=[f"Unsupported task_type {_dapr_mode}"])
