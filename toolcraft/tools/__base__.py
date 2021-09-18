"""
Get inspirations from
https://github.com/python-poetry/poetry/tree/master/poetry/console/commands

"""

import abc
import inspect
import typer
import typing as t

from .. import error as e
from .. import logger

APP = typer.Typer(name="toolcraft")
_LOGGER = logger.get_logger()


class Tool(abc.ABC):

    AVAILABLE_TOOL_CLASSES = {}  # type: t.Dict[str, t.Type[Tool]]

    def __init_subclass__(cls, **kwargs):
        global APP
        # -------------------------------------------------------- 01
        # Validations
        # -------------------------------------------------------- 01.01
        # all subclasses must be concrete
        if inspect.isabstract(cls):
            e.code.CodingError(
                msgs=[
                    f"Class {cls} is not concrete ..."
                ]
            )
        # -------------------------------------------------------- 01.02
        # there can be only one tool class per module
        else:
            if cls.tool_name() in cls.AVAILABLE_TOOL_CLASSES.keys():
                e.code.CodingError(
                    msgs=[
                        f"you can have only one concrete subclass of {Tool} in "
                        f"module {cls.__module__}"
                    ]
                )
        # -------------------------------------------------------- 01.03
        # you need to define `command_fn` method in order to register it with
        # `typer_app`
        if Tool.command_fn.__name__ not in cls.__dict__.keys():
            e.code.CodingError(
                msgs=[
                    f"Please override method `{Tool.command_fn.__name__}` in "
                    f"class {cls}."
                ]
            )

        # -------------------------------------------------------- 02
        # store tool classes for future reference ...
        cls.AVAILABLE_TOOL_CLASSES[cls.tool_name()] = cls

        # -------------------------------------------------------- 03
        # register command_fn in typer_app
        APP.command(name=cls.tool_name())(cls.command_fn)

        # -------------------------------------------------------- 04
        # log
        # _LOGGER.info(
        #     msg=f"Registered tool `{cls.tool_name()}`"
        # )

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
