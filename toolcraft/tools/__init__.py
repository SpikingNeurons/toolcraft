"""
typer library has lot of things I want
todo: read typer docs
  https://typer.tiangolo.com/tutorial/launch/

todo: to expand
  https://typer.tiangolo.com/#other-tools-and-plug-ins
"""

import pathlib
import importlib
import typer
import sys

from .__base__ import Tool, APP

# todo: is this needed? Can this be removed?
# this is so that all modules are loaded in tools directory ... so that the
# subclassed classes are loaded and they are available
for f in pathlib.Path(__file__).parent.glob("*.py"):
    # bypass not required things
    if "__" in f.stem:
        continue

    # import
    importlib.import_module(f".{f.stem}", __package__)


if __name__ == '__main__':
    sys.exit(APP())
