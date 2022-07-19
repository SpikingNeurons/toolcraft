import dataclasses
import typing as t
import sys

sys.path.append("..")

from toolcraft import marshalling as m
from toolcraft import util


@dataclasses.dataclass(frozen=True)
class XX(m.HashableClass):
    ...


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['f1']
)
class A(m.YamlRepr):
    a: int

    @util.CacheResult
    def f1(self):
        ...


@dataclasses.dataclass(frozen=True)
class B(A):
    a: int

    @util.CacheResult
    def f1(self):
        ...


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['f2']
)
class C(B):
    d: int

    def f1(self):
        ...

    @util.CacheResult
    def f2(self):
        ...


if __name__ == '__main__':
    x = C(1,2)
    # rule check will trigger only when first HashableClass instance is created
    # above instance will get created but rule check will not trigger ...
    XX()
