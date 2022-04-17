"""
Responsible to test
+ rich logging
+ rich progress bar
+ rich prompt (useful for tools)
+ rich traceback when errors are raised
+ FIleHandler that logs to file on disk

"""
import dataclasses
import enum
import pathlib
import sys
import time
import typing as t

import numpy as np
import pandas as pd
import pyarrow as pa
import rich

from toolcraft import error as e
from toolcraft import logger
from toolcraft import marshalling as m
from toolcraft import settings
from toolcraft import storage as s
from toolcraft import util

sys.path.append("..")

_LOGGER = logger.get_logger()


def f():
    for i in range(100):
        yield i


def _experiment_rich():
    """
    quickly experiment rich lib here
    will not be part final unittests
    """
    from rich.progress import track

    # for n in track(f(), total=100, description="Processing..."):
    #     time.sleep(0.1)


def try_logging():
    _LOGGER.info(
        msg="I am showing some message",
        msgs=[
            "JJKH wegbdkq2zuyhbviu ",
            ["sadas", "sadas", "uiyu", "ewgy"],
            (1, 2, 3, "dfsdf"),
            {
                "ee": 55,
                "gsedf": "dfsd"
            },
        ],
    )


def try_exceptions():
    try:
        raise e.code.CodingError(msgs=[
            "I am wrong ...", "But why ???", {
                1: 1,
                2: 3
            }, ["q", "tt", "yy"]
        ])
    except Exception as _e:
        _LOGGER.exception(msg="Traceback")


def main():
    _experiment_rich()
    try_logging()
    try_exceptions()


if __name__ == "__main__":
    main()
