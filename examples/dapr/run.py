"""
Call using run_runner.py
Eventually we need to call this from toolcraft cli i.e. when we install it via pip
"""
import dataclasses
import sys

sys.path.append("..\\..")
from toolcraft.tools import dapr

from toolcraft import marshalling as m
from toolcraft.tools import dapr


class HashableRunner(dapr.HashableRunner):
    ...


if __name__ == '__main__':
    HashableRunner.run()
