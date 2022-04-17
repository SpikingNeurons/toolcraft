import dataclasses
import sys
import typing as t

from toolcraft import marshalling as m
from toolcraft import util

sys.path.append("..")


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(things_to_be_cached=["f1"])
class A(m.HashableClass):
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
@m.RuleChecker(things_to_be_cached=["f2"])
class C(B):
    d: int

    @util.CacheResult
    def f2(self):
        ...


if __name__ == "__main__":

    x = C(1, 2)
