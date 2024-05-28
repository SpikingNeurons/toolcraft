import dataclasses
import typing as t
import abc
from fsspec.implementations import local
from fsspec.spec import AbstractFileSystem
from upath import UPath

from .. import marshalling as m
from .. import util
from .. import error as e


def get_fs_from_toml_config(d: t.Dict) -> "BaseFileSystem":
    _fs_protocol_string = d["url"].split("://")[0]
    return {
        "local": LocalFileSystem,
        "file": LocalFileSystem,
    }[_fs_protocol_string](**d)


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['fs', 'upath'],
    things_not_to_be_overridden=['fs'],
)
class BaseFileSystem(m.HashableClass, abc.ABC):

    url: str

    # Dir cache storage options can be found here >>> fsspec.spec.DirCache
    use_listings_cache: bool = True
    listings_expiry_time: t.Optional[int] = None
    max_paths: t.Optional[int] = None

    @property
    @util.CacheResult
    def fs(self) -> AbstractFileSystem:
        return self.upath.fs

    @property
    @util.CacheResult
    def upath(self) -> UPath:
        """
        generate UPath for Path style
        note this design is good as we can get rid of it when there is official support or better library
          with fsspec and pathlib integration
        """
        _kwargs = self.as_dict(skip_defaults=True)
        del _kwargs["url"]
        return UPath(self.url, **_kwargs)

    def init_validate(self):

        # call super
        super().init_validate()

        # validate protocol
        _fs_protocol_string = self.url.split("://")[0]
        if isinstance(self, LocalFileSystem):
            e.validation.ShouldBeOneOf.check(
                value=_fs_protocol_string, values=local.LocalFileSystem.protocol,
                notes=[f"protocol string did not match for class {self.__class__}"]
            )
        else:
            raise e.code.NotSupported(notes=[f"protocol {_fs_protocol_string} is not supported"])




@dataclasses.dataclass(frozen=True)
class LocalFileSystem(BaseFileSystem):
    """
    >>> local.LocalFileSystem
    """
    auto_mkdir: bool = False
