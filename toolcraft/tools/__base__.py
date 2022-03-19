"""
[Guidelines]
+ We design this using rich lib
+ We have lot of things like progress_bar, prompt which we can use
+ todo: we can have parser based on command_fn signature to ask questions to
    fill up arguments for tool ...
    also we can create documentation in typer style but using rich
+ Get inspirations from
  + https://github.com/python-poetry/poetry/tree/master/poetry/console/commands
  + https://typer.tiangolo.com
  + https://rich.readthedocs.io/en/stable/prompt.html


[Note] No need for typer
  + we can do many things with rich.prompt
    https://rich.readthedocs.io/en/stable/prompt.html
  + Also we want interactive console things we will not be building cli tools
    i.e. this library will not be used as cli based API

"""

import abc
import inspect
import typing as t
from rich import pretty

from .. import error as e

# Rich may be installed in the REPL so that Python data structures are automatically
# pretty printed with syntax highlighting.
# This makes the toolcraft tools console UI colorful
pretty.install()


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
        # -------------------------------------------------------- 01
        # Validations
        # -------------------------------------------------------- 01.01
        # all subclasses must be concrete
        if inspect.isabstract(cls):
            raise Exception(
                f"Class {cls} is not concrete ..."
            )
        # -------------------------------------------------------- 01.02
        # nothing except command_fn should be overridden in subclass
        _command_fn_name = Tool.command_fn.__name__
        _child_class_keys = cls.__dict__.keys()
        for _k in Tool.__dict__.keys():
            if _k == _command_fn_name:
                continue
            if _k.startswith('_'):
                continue
            if _k in _child_class_keys:
                raise e.code.CodingError(
                    msgs=[
                        f"You are not allowed to override {_k} in child class "
                        f"{cls} as it is already defined in parent class {Tool}"
                    ]
                )
        # -------------------------------------------------------- 01.03
        # there can be only one tool class per module
        if cls.tool_name() in cls.AVAILABLE_TOOL_CLASSES.keys():
            raise e.code.CodingError(
                msgs=[
                    f"There is already a tool named {cls.tool_name()} taken by class "
                    f"{cls}",
                    f"you can have only one concrete subclass of {Tool} in "
                    f"module {cls.__module__}"
                ]
            )

        # -------------------------------------------------------- 02
        # store tool classes for future reference ...
        cls.AVAILABLE_TOOL_CLASSES[cls.tool_name()] = cls

    def __init__(self):
        raise e.code.CodingError(
            msgs=[
                "We do not allow to create instances for this class as it needs to "
                "used at class level ..."
            ]
        )

    @classmethod
    def tool_name(cls) -> str:
        """
        There can be ony one tool per module
        """
        return cls.__module__.split(".")[-1]

    @classmethod
    @abc.abstractmethod
    def command_fn(cls, **kwargs):
        """
        + todo: we can have parser based on command_fn signature to ask questions to
            fill up arguments for tool ...
            also we can create documentation in typer style but using rich
        """
        ...
