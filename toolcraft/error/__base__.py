import inspect
import re
import yaml
from rich.console import Console
from rich.traceback import Traceback, Trace

from .. import logger


# todo: for python 3 there is special method Exception().with_traceback() see
#  if can be used .... also for stack trace instead if using inspect see if
#  Exception().__traceback__ can be used
#  check PEP 3109 https://www.python.org/dev/peps/pep-3109/

_LOGGER = logger.get_logger()

_SKULL_EMOJI = "💀"
_EXCEPTION_HEADER = f"{_SKULL_EMOJI} >>> {{header}} <<< {_SKULL_EMOJI}"


def camel_case_split(identifier):
    matches = re.finditer(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


class _CustomException(Exception):
    """
    todo: use `rich` libs traceback interface etc
    """
    # If not a validator then you need to explicitly raise instead of calling
    _RAISE_EXPLICITLY = False

    def __init__(
        self, *,
        msgs: logger.MESSAGES_TYPE,
    ):

        # -----------------------------------------------------------------01
        # GET LOGGER
        _caller_frame = inspect.currentframe().f_back.f_back
        _logger = logger.get_logger(
            module=inspect.getmodule(_caller_frame)
        )

        # -----------------------------------------------------------------02
        # MESSAGES RELATED
        # make header and set is as message
        _header = " ".join(camel_case_split(self.__class__.__name__)).upper()
        _header = _EXCEPTION_HEADER.format(header=_header)
        # call super to set the header as short message
        _msg = _header + "\n" + "\n--- ".join([str(_) for _ in msgs])
        super().__init__(f"{_msg}")

        # -----------------------------------------------------------------03
        # log
        _logger.error(msg=_header, msgs=msgs)
        # log with rich
        # todo: doing this here as the error does not appear on console
        #   need to investigate how to use RichHandler to log to file as well as console
        _console = Console()
        # this can be done only in try catch block as traceback is not available
        # _console.print_exception(show_locals=False, width=None)
        _rich_print = "\n" + _header
        if msgs is not None:
            _rich_print += "\n" + yaml.dump(msgs)
        _console.print(_rich_print)

        # -----------------------------------------------------------------04
        # if the parent i.e. this __init__ was called from child that means the
        # validation failed so set the flag
        self._failed = True

        # -----------------------------------------------------------------05
        # add redundant return for code checker to indicate that this need not
        # be explicitly raised
        return

    def raise_if_failed(self):
        # test if it needs to be raised explicitly
        if self._RAISE_EXPLICITLY:
            from .code import RaiseExplicitly
            raise RaiseExplicitly(
                msgs=[
                    f"Do not call {self.raise_if_failed} for class {self.__class__} "
                    f"as it is configured to be raised explicitly.",
                    f"Instead use keyword `raise`"
                ]
            )

        # raise only if failed i.e. super constructor was called
        try:
            if self._failed:
                raise self
        except AttributeError:
            # no need to raise
            return
