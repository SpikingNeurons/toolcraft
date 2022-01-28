"""
Get inspirations from
https://github.com/python-poetry/poetry/tree/master/poetry/console/commands

todo: do not use `toolcraft.logger` and `toolcraft.error` instead have your
  own typer based interface as toolcraft.tools deals with only CLI things
  + printing and colors -> https://typer.tiangolo.com/tutorial/printing/
  + progress bar -> https://typer.tiangolo.com/tutorial/progressbar/
  + fast-api -> typer is fast-api for cli also we will get same color
    support etc
  + asks for prompt -> https://typer.tiangolo.com/tutorial/prompt/
  + nice terminating -> https://typer.tiangolo.com/tutorial/terminating/
  [Counter argument]
  + we can still use `toolcraft.logger` and `toolcraft.error` which will use `rich` lib
  + while we still use typer for cli, validation, documentation and type completion


todo: may be no need for typer
  + we can do many things rich.prompt
  https://rich.readthedocs.io/en/stable/prompt.html
  + Also we want interactive console things we will not be building cli tools
    i.e. this library will not be used as cli based API

todo: As of now typer is helpful to register tools
  Need to investigate nice alternative for thins

"""

import abc
import inspect
import typer
import typing as t

APP = typer.Typer(name="toolcraft")


class Tool(abc.ABC):
    """
    This always is used as class ... no need to create instance of it

    Also, the import automatically registers the tools, so we never intend to call
    explicitly ... just implement command_fn ;)

    Note: never override `tool_name`

    todo: do not allow anyone to make instances of this class ...

    """

    AVAILABLE_TOOL_CLASSES = {}  # type: t.Dict[str, t.Type[Tool]]

    def __init_subclass__(cls, **kwargs):
        global APP
        # -------------------------------------------------------- 01
        # Validations
        # -------------------------------------------------------- 01.01
        # method tool_name should never be overridden
        # todo: dont know how to make this work ... python automatically bounded class
        #   method in subclass ... even id() does not work
        # if id(Tool.tool_name) != id(cls.tool_name:
        # if Tool.tool_name != cls.tool_name:
        # this seems to work the trick is to get the underlying func
        # noinspection PyUnresolvedReferences
        if id(Tool.tool_name.__func__) != id(cls.tool_name.__func__):
            print(Tool.tool_name, cls.tool_name)
            raise Exception(
                f"Please never override method {Tool.tool_name}"
            )
        # -------------------------------------------------------- 01.02
        # all subclasses must be concrete
        if inspect.isabstract(cls):
            raise Exception(
                f"Class {cls} is not concrete ..."
            )
        # -------------------------------------------------------- 01.03
        # there can be only one tool class per module
        else:
            if cls.tool_name() in cls.AVAILABLE_TOOL_CLASSES.keys():
                raise Exception(
                    f"you can have only one concrete subclass of {Tool} in "
                    f"module {cls.__module__}"
                )
        # -------------------------------------------------------- 01.04
        # you need to define `command_fn` method in order to register it with
        # `typer_app`
        if Tool.command_fn.__name__ not in cls.__dict__.keys():
            raise Exception(
                f"Please override method `{Tool.command_fn.__name__}` in "
                f"class {cls}."
            )

        # -------------------------------------------------------- 02
        # store tool classes for future reference ...
        cls.AVAILABLE_TOOL_CLASSES[cls.tool_name()] = cls

        # -------------------------------------------------------- 03
        # register command_fn in typer_app
        APP.command(name=cls.tool_name())(cls.command_fn)

    @classmethod
    def tool_name(cls) -> str:
        """
        There can be ony one tool per module
        """
        return cls.__module__.split(".")[-1]

    @classmethod
    def command_fn(cls, **kwargs):
        raise NotImplementedError(
            f"Please implement this method in the respective "
            f"subclass ..."
        )

    @classmethod
    def log(
        cls,
        msg: str, msgs: t.List[str] = None,
        color: str = typer.colors.BRIGHT_WHITE,
        err: bool = False,
    ):
        """
        todo: May be use `rich` lib here ...
        """
        _tool_name = typer.style(f"{cls.tool_name()}:", fg=color, bold=True)
        typer.echo(f"{_tool_name} {msg}", err=err, color=True)
        if bool(msgs):
            _indent = typer.style("   >>> ", fg=color, bold=True)
            for _m in msgs:
                typer.echo(f"{_indent}{_m}", err=err, color=True)

    @classmethod
    def info(cls, msg: str, msgs: t.List[str] = None):
        cls.log(msg, msgs, typer.colors.GREEN)

    @classmethod
    def abort(cls, msg: str, msgs: t.List[str] = None) -> typer.Abort:
        msg = typer.style(msg, fg=typer.colors.YELLOW)
        cls.log(msg, msgs, typer.colors.BRIGHT_RED, err=True)
        return typer.Abort()
