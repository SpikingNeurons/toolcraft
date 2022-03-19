"""
This file is just helpful until you do not install toolcraft with pip install ...
todo: delete this file after `toolcraft.tools` is available via pip install
"""
import sys
import pathlib

sys.path.append("..\\..")

from toolcraft.tools import dapr
from toolcraft import settings


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Only pass one arg")
    if sys.argv[1] not in ['server', 'launch', 'view']:
        raise Exception(f"Unsupported value {sys.argv[1]}")
    _file = "run.py"
    # noinspection PyTypeChecker
    dapr.DaprTool.command_fn(
        pathlib.Path(_file), task_type=sys.argv[1]
    )
