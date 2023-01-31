import enum
import typing as t
import dataclasses
import time
import sys
import asyncio
import os
import pathlib
import numpy as np
sys.path.append("..")

from toolcraft import job
from toolcraft import settings
from toolcraft import util
from toolcraft import logger
from toolcraft import gui
from toolcraft import marshalling as m

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class A(m.HashableClass):

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hook up get
        util.HookUp(
            cls=cls,
            method=cls.get_data,
            pre_method=cls.get_data_pre_runner,
            post_method=cls.get_data_post_runner,
        )

    def get_data_pre_runner(self):
        print("A", self.__class__, "get data pre runner")

    def get_data(self):
        print("A", self.__class__, "get data")

    def get_data_post_runner(self, *, hooked_method_return_value: t.Any):
        print("A", self.__class__, "get data post runner")


@dataclasses.dataclass(frozen=True)
class B(A):

    def get_data(self):
        super().get_data()
        print("B", self.__class__, "get data")

    def get_data_post_runner(self, *, hooked_method_return_value: t.Any):
        super().get_data_post_runner(hooked_method_return_value=hooked_method_return_value)
        print("B", self.__class__, "get data post runner")


def main():
    print("A"*30)
    a = A()
    a.get_data()
    print("B"*30)
    b = B()
    b.get_data()


if __name__ == '__main__':
    main()
