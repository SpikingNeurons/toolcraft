"""
Call using try_dapr_server_runner.py
As we need to call this from toolcraft cli i.e. when we install it via pip
"""
import dataclasses
import sys

sys.path.append("..\\..")

from toolcraft import marshalling as m
from toolcraft.tools import dapr


@dataclasses.dataclass(frozen=True)
class Test(m.HashableClass):
    a: int


if __name__ == '__main__':
    dapr.launch_dapr_app()