"""
Call using run_runner.py
Eventually we need to call this from toolcraft cli i.e. when we install it via pip
"""
import dataclasses
import sys

sys.path.append("..\\..")
from toolcraft.tools import dapr

from toolcraft import marshalling as m
from toolcraft import dapr


@dataclasses.dataclass(frozen=True)
class Test(m.HashableClass):
    a: int
    b: float

    @dapr.Invoke()
    def request_1(self):
        ...



class HashableRunner(dapr.HashableRunner):
    ...


if __name__ == '__main__':
    HashableRunner.run()
