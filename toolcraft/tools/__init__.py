"""
typer library has lot of things I want
todo: read typer docs
  https://typer.tiangolo.com/tutorial/launch/

todo: to expand
  https://typer.tiangolo.com/#other-tools-and-plug-ins

todo: do not use `toolcraft.logger` and `toolcraft.error` instead have your
  own typer based interface as toolcraft.tools deals with only CLI things
  + printing and colors -> https://typer.tiangolo.com/tutorial/printing/
  + progress bar -> https://typer.tiangolo.com/tutorial/progressbar/
  + fast-api -> typer is fast-api for cli also we will get same color
    support etc
  + asks for prompt -> https://typer.tiangolo.com/tutorial/prompt/
  + nice terminating -> https://typer.tiangolo.com/tutorial/terminating/
  [Counter argument] Use rich rich rich
  + we can still use `toolcraft.logger` and `toolcraft.error` which will use `rich` lib
  + while we still use typer for cli, validation, documentation and type completion

"""

import pathlib
import importlib
import sys

from .__base__ import Tool

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
    sys.exit(Tool.run())
