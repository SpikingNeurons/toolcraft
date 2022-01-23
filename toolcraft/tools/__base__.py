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

    Note that refrain from using `toolcraft.logger` and `toolcraft.error` as this
    module is used for cli operations

    todo: Also see if we can use alive_progress

    We might need to support things like
    + printing and colors -> https://typer.tiangolo.com/tutorial/printing/
    + progress bar -> https://typer.tiangolo.com/tutorial/progressbar/
    + fast-api -> typer is fast-api for cli also we will get same color support etc
    + asks for prompt -> https://typer.tiangolo.com/tutorial/prompt/
    + nice terminating -> https://typer.tiangolo.com/tutorial/terminating/

    """

    AVAILABLE_TOOL_CLASSES = {}  # type: t.Dict[str, t.Type[Tool]]

    def __init_subclass__(cls, **kwargs):
        global APP
        # -------------------------------------------------------- 01
        # Validations
        # -------------------------------------------------------- 01.01
        # method tool_name should never be overriden
        if Tool.tool_name != cls.tool_name:
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
