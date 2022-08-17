"""
This file is just helpful until you do not install toolcraft with pip install ...
todo: delete this file after `toolcraft.tools` is available via pip install
"""
import pathlib
import sys

from toolcraft import settings
from toolcraft.tools import dapr

sys.path.append("..\\..")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("client")
    if len(sys.argv) != 2:
        raise Exception("Only pass one arg")
    if sys.argv[1] not in ["server", "launch", "client"]:
        raise Exception(f"Unsupported value {sys.argv[1]}")
    _file = "run.py"
    # noinspection PyTypeChecker
    dapr.DaprTool.command_fn(pathlib.Path(_file), dapr_mode=sys.argv[1])
