"""
This file is just until you do not install toolcraft with pip install ...
"""
import sys
import pathlib

sys.path.append("..")

from toolcraft.tools import dapr


if __name__ == '__main__':
    _file = "try_dapr_server.py"
    dapr.DaprTool.command_fn(pathlib.Path(_file))
