"""
Here we test features of m.Tracker
"""

import dataclasses
import enum
import pathlib
import sys
import time
import typing as t
from rich import print


sys.path.append("..")

import numpy as np
import pandas as pd
import pyarrow as pa
from toolcraft import marshalling as m
from toolcraft import settings
from toolcraft import storage as s
from toolcraft import util, richy, logger
from toolcraft.storage import file_system, Path
from toolcraft.storage.table import Filter
from toolcraft.storage.table import make_expression as me

settings.DEBUG_HASHABLE_STATE = False

_LOGGER = logger.get_logger()


def main():
    ...

if __name__ == '__main__':
    main()
