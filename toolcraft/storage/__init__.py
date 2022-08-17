"""
Understand storage module:
+ file_system >> will assist fifo to use fsspec smartly
+ folder.Folder >>
  + Can manage its children ...
  + uses file_system to detect where to keep files and folders
  + children can Folder/FileGroup/FileFolder/Table
+ file_group.FileGroup >> Will have fixed number of files i.e. deterministic behaviour
+ file_folder.FileFolder >> can dynamically add remove files
+ table.Table >> full pyarrow tables
+ stream >> interface pending
+ state >> most likely will use dapr state
  + might be eventually get rid of disk based StateFIle

todo: storage in point of view of mlflow (also see top of individual module for
  more explanation)
  + table >> mlflow metrics
  + stream (streamed table) >> mlflow does not offer this
  + state >> mlflow tags
  + fifo.FileFolder >> mlflow artifacts

"""

from . import file_system
from .__base__ import StorageHashable
from .file_group import (
    SELECT_TYPE,
    USE_ALL,
    DownloadFileGroup,
    FileGroup,
    FileGroupConfig,
    FileGroupFromPaths,
    NpyFileGroup,
    TempFileGroup,
)
from .file_system import FileSystemConfig, Path
from .folder import Folder
from .state import Config, Info, Suffix
from .table import Filter, Table, make_expression

# a call so that the CWD FileSystem is loaded if defined in config.toml or else it
# will add default CWD FileSystem ... also it will save it to config.toml
FileSystemConfig.get("CWD")
assert "CWD" in file_system.available_file_systems(
), "must be there by now ..."
