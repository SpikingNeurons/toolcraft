"""
A tool to save config in users dir.
Can ask users while running their projects for first time.
+ In CLI we can ask questions
+ When in Flutter Ui we can use `config` icon to configure settings and also
  force user at start to feel mandatory config

We will be using maybe `toml` to save settings in users dir. Also need to
figure out how android apps and web apps save settings in users dir

todo:
  typer has you covered to get and store config
    - https://typer.tiangolo.com/tutorial/app-dir/
  It can also ask for prompts
    - https://typer.tiangolo.com/tutorial/prompt/

"""
import pathlib
import typer
import toml

from . import Tool
from .. import error as e


class ConfigTool(Tool):

    @classmethod
    def command_fn(
        cls,
        # file_name: str = typer.Option(
        #     ...,
        #     help="The toml style file name to load.",
        # )
    ):
        typer.echo(f"Called tool {cls.tool_name()}")
