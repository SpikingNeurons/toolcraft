"""
This module might eventually become `mlcraft`

todo: `mlflow` and `wandb` are closest things to mlcraft
  + brainstrom USP of mlcraft
    + python gui direct access to memory IPC/Grpc/RDMA will be available
    + solid visual tools and in reach of python developers which shy away from javascript
    + capability to go grpc/http/ftp/ssh/gcs ... etc
    + dapr based side car architecture ... mix and match compute resources
    + powerful HashableClass that gives python user the control
    + heavy pyarrow usage for storing tables that can be stored accross machines
      and queried with pyarrow ...
      also other things like GPU analytics, plasma (in memory store), IPC, RBMA will
      be there as pa.Table's

todo: Models can be stored as artifact i.e. `storage.dec.FileGroup` but then to make it
  live or track its lifecycle get inspiration
  from https://mlflow.org/docs/latest/model-registry.html#

todo: look at heron philosophy ... although here we are basically inspired by popular
  mlflow and want to use dapr https://github.com/georgedimitriadis/Heron
"""
import dataclasses
import pathlib
import typer
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
