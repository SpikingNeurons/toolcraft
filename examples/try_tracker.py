"""
Here we test features of m.Tracker
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
from rich import print

from toolcraft import logger
from toolcraft import marshalling as m
from toolcraft import richy, settings
from toolcraft import storage as s
from toolcraft import util
from toolcraft.storage import Path, file_system
from toolcraft.storage.table import Filter
from toolcraft.storage.table import make_expression as me

sys.path.append("..")

settings.DEBUG_HASHABLE_STATE = False

_LOGGER = logger.get_logger()


def main():
    ...


if __name__ == "__main__":
    main()
