import dataclasses
import typing as t
import fsspec
import abc
from fsspec.implementations import local
from fsspec.spec import AbstractFileSystem
from upath import UPath

from .. import marshalling as m
from .. import util



@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['fs', 'upath']
)
class FileSystem(m.HashableClass, abc.ABC):

    # Dir cache storage options can be found here >>> fsspec.spec.DirCache
    use_listings_cache: bool = True
    listings_expiry_time: t.Optional[int] = None
    max_paths: t.Optional[int] = None

    @property
    @abc.abstractmethod
    def fs(self) -> AbstractFileSystem:
        ...

    @property
    @util.CacheResult
    def upath(self) -> UPath:
        """
        generate UPath for Path style
        note this design is good as we can get rid of it when there is official support or better library
          with fsspec and pathlib integration

        todo: we know that UPath creates a fsspec file system instance (self.upath.fs) and we also
          have a file system instance cached in self.fs ... we need to see if we can make them one
        """
        _str = self.fs.unstrip_protocol(".")
        return UPath(...)



@dataclasses.dataclass(frozen=True)
class LocalFileSystem(FileSystem):
    """
    >>> local.LocalFileSystem
    """
    auto_mkdir: bool = False

    @property
    @util.CacheResult
    def fs(self) -> local.LocalFileSystem:
        return local.LocalFileSystem(**self.as_dict(skip_defaults=True))
