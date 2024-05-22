import dataclasses
import typing as t
import fsspec

from .. import marshalling as m


@dataclasses.dataclass(frozen=True)
class DirCacheStorageOptions(m.HashableClass):
    """
    Dir cache storage options can be found here
    >>> fsspec.spec.DirCache
    """

    use_listings_cache: bool = True
    listings_expiry_time: t.Optional[int] = None
    max_paths: t.Optional[int] = None


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['fs']
)
class FileSystem(m.HashableClass):

    ...
