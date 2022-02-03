import dataclasses
import typing as t
import sys

sys.path.append("..")

from toolcraft import marshalling as m
from toolcraft import util


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['f1']
)
class A(m.HashableClass):
    a: int

    @util.CacheResult
    def f1(self):
        ...


@dataclasses.dataclass(frozen=True)
class B(A):
    a: int
    def f1(self):
        ...


@dataclasses.dataclass(frozen=True)
@m.RuleChecker(
    things_to_be_cached=['f2']
)
class C(B):
    d: int

    @util.CacheResult
    def f2(self):
        ...



if __name__ == '__main__':
    print(A.__dict__['__rule_checker__'])
    # print(B.__dict__['__rule_checker__'])
    print(C.__dict__['__rule_checker__'])

    _ar = A.__dict__['__rule_checker__']
    _cr = C.__dict__['__rule_checker__']

    print("...")

    for _ in m.Tracker.available_sub_classes():
        print(_)
