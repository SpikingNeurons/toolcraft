"""
Module related to file systems to be used with `storage.df_file`.
Decides where and how to save dataframes of different storage types.

Currently designed based on file systems of pyarrow.
Used by `storage.df_file` i.e. for dataframe storage.
Note that this is different from file format which is either ipc/feather or
parquet.

todo: can make `storage.file_group` use the file systems to save the
  FileGroup and Folder.

We will also add our own file systems here.

todo: add support https://arrow.apache.org/docs/python/filesystems.html#filesystem-hdfs
  check
    import gcsfs
    import adlfs

todo: This is new (go on to fsspec) even pyarrow file-system allows fsspec and pafs
  offers limited subset of functions of what fsspec offers i.e. related to pa.dataset
  storage ... but other extensive stuff for flie system can come from fsspec
  + https://filesystem-spec.readthedocs.io/en/latest/features.html#caching-files-locally
  Also see the exhaustive implementaions
  + https://github.com/fsspec/filesystem_spec/tree/master/fsspec/implementations

todo: remote caching
  https://www.anaconda.com/blog/fsspec-remote-caching

todo: note that we can safely use this module for
  both Table (mlflow metrics) and FileGroup (mlflow artifacts)
  + file_group uses Folder that can use file system
  + stream and table will use table.Table which is Folder so that can use file_system
  + state will use dapr state and hence no need for file_system there
"""
import pathlib
import typing as t
import pyarrow as pa
import pyarrow.fs as pafs
from .. import error as e
from .. import util


# noinspection PyAbstractClass
class LocalFileSystem(pafs.LocalFileSystem):

    _instance = None

    @classmethod
    def get_instance(cls) -> "LocalFileSystem":
        """
        We need to override this as parent class method is not aware of this
        subclass.
        """
        if cls._instance is None:
            cls._instance = LocalFileSystem()
        else:
            e.validation.ShouldBeInstanceOf(
                value=cls._instance,
                value_types=(LocalFileSystem, ),
                msgs=[
                    f"Make sure that you override pyarrow.localfs or any "
                    f"other code that calls parents get_instance and inits "
                    f"self._instance variable to wrong value ..."
                ]
            )
        return cls._instance

    # def rename(self, path, new_path):
    #     raise NotImplementedError
    #
    # def stat(self, path):
    #     raise NotImplementedError

    def delete(self, path: pathlib.Path, recursive=True) -> bool:
        # this does mean the user is using local file system for
        # which the delete is not implemented
        # todo: this is our version ... is it efficient ??
        return util.pathlib_rmtree(path=path, recursive=recursive, force=True)

    def exists(self, path: pathlib.Path) -> bool:
        return path.exists()


# noinspection PyAbstractClass
class DaskFileSystem(pa.filesystem.DaskFileSystem):
    # def isdir(self, path):
    #     pass
    #
    # def isfile(self, path):
    #     pass
    #
    # def stat(self, path):
    #     pass
    #
    # def rename(self, path, new_path):
    #     pass
    ...


# noinspection PyAbstractClass
class S3FSWrapper(pa.filesystem.S3FSWrapper):
    # def stat(self, path):
    #     pass
    #
    # def rename(self, path, new_path):
    #     pass
    ...


class HadoopFileSystem(pa.hdfs.HadoopFileSystem):
    ...
