# coding=utf-8
"""
todo: [*** deprecate this ***]

[Guidelines]
+ we will always stick to python `logging` module for logging
  while fancy things can be achieved by extending logging.Handler
+ the `rich` lib will be used for logging to console ...
  and also for progress bars and spinners
+ dapr telemetry styled streamed logging needs to be explored
+ Note that typer based is only used in `toolcraft.tools` as we need some
  cli, validation and documentation features ... but we can use `rich` only for
  logging part while avoiding typer's echo interface

NOTE: we do not use scandal.error as it is not possible here

todo: rich log handler
  https://rich.readthedocs.io/en/stable/logging.html

todo: removing exceptions is difficult ... as it is problematic to import
  .error module ... we can just pretty log the exceptions instead

todo: adapt logger to use `toolcraft.dapr.tracker` telemetry for distributed logging

todo: Need to dump tqdm and yaspin (never use typer)
  + toolcraft is not intended for CLI as it has a GUI
  + for server we need file logging so no use for yaspin
  + in rare case of cli base toolcraft usage maybe add lightweight support for
    alive_progress instead (new but fun lib with yaspin+tqdm features)
  + type is pure cli tool and we use it only to run toolcraft on servers with
    command prompt ... never be tempted to introduce it here ... as it is clearly
    out of scope

todo: move to rich/textual instead of yaspin or tqdm https://github.com/Textualize
  + https://github.com/Textualize/rich
  + https://github.com/Textualize/textual
  You can provide rich console to hashable classes and have pretty tracebacks,
  multiple progress bars: https://rich.readthedocs.io/en/latest/protocol.html

todo: never use typer
  + we only use it with toolcraft.tools for using with CLI
  + maybe handle this all with rich prompt and let that dependency go
"""

import logging
from tqdm.auto import tqdm
import typing as t
import inspect
import types
import pathlib
from logging import config as lc
from logging import handlers
import textwrap
from datetime import datetime
import sys
import io
from yaspin.core import Yaspin
from . import settings

if settings.DPG_WORKS:
    import dearpygui.dearpygui as dpg

_LOGGER_STREAM = sys.stdout

WRAP_WIDTH = 150
SPINNER_TITLE_WIDTH = WRAP_WIDTH

MESSAGES_TYPE = t.List[
    t.Union[
        str,
        t.List,
        t.Tuple,
        t.Dict,
    ]
]


class ProgressBar(tqdm):
    """
    todo: try alive_progress (yaspin+tqdm features)
    """

    # noinspection PyShadowingBuiltins
    def __init__(
        self, *,
        iterable: t.Iterable = None,
        desc: str = None,
        total: t.Union[int, float] = None,
        leave: bool = True,
        file: t.Union[io.TextIOWrapper, io.StringIO] = sys.stdout,
        ncols: int = WRAP_WIDTH,
        mininterval: float = 0.1,
        maxinterval: float = 10.0,
        miniters: t.Union[int, float] = None,
        ascii: t.Union[str, bool] = None,
        unit: str = ' it',
        unit_scale: t.Union[bool, int, float] = False,
        dynamic_ncols: bool = True,
        smoothing: float = 0.3,
        bar_format: str = None,
        initial: int = 0,
        position: int = None,
        postfix: dict = None,
        unit_divisor: float = 1000,
        write_bytes: bool = None,
        lock_args: tuple = None,
        nrows: int = None,
        colour: str = None,
        delay: float = 0,
        gui: bool = False,
    ):
        """
        Refer to super class init for allowed kwargs
        >>> tqdm.__init__

        As and when we need some kwargs from there we will document them here
        and use it ...

        iterable  : iterable, optional
            Iterable to decorate with a progressbar.
            Leave blank to manually manage the updates.
        desc  : str, optional
            Prefix for the progressbar.
        total  : int or float, optional
            The number of expected iterations. If unspecified,
            len(iterable) is used if possible. If float("inf") or as a last
            resort, only basic progress statistics are displayed
            (no ETA, no progressbar).
            If `gui` is True and this parameter needs subsequent updating,
            specify an initial arbitrary large positive number,
            e.g. 9e9.
        leave  : bool, optional
            If [default: True], keeps all traces of the progressbar
            upon termination of iteration.
            If `None`, will leave only if `position` is `0`.
        file  : `io.TextIOWrapper` or `io.StringIO`, optional
            Specifies where to output the progress messages
            (default: sys.stderr). Uses `file.write(str)` and `file.flush()`
            methods.  For encoding, see `write_bytes`.
        ncols  : int, optional
            The width of the entire output message. If specified,
            dynamically resizes the progressbar to stay within this bound.
            If unspecified, attempts to use environment width. The
            fallback is a meter width of 10 and no limit for the counter and
            statistics. If 0, will not print any meter (only stats).
        mininterval  : float, optional
            Minimum progress display update interval [default: 0.1] seconds.
        maxinterval  : float, optional
            Maximum progress display update interval [default: 10] seconds.
            Automatically adjusts `miniters` to correspond to `mininterval`
            after long display update lag. Only works if `dynamic_miniters`
            or monitor thread is enabled.
        miniters  : int or float, optional
            Minimum progress display update interval, in iterations.
            If 0 and `dynamic_miniters`, will automatically adjust to equal
            `mininterval` (more CPU efficient, good for tight loops).
            If > 0, will skip display of specified number of iterations.
            Tweak this and `mininterval` to get very efficient loops.
            If your progress is erratic with both fast and slow iterations
            (network, skipping items, etc) you should set miniters=1.
        ascii  : bool or str, optional
            If unspecified or False, use unicode (smooth blocks) to fill
            the meter. The fallback is to use ASCII characters " 123456789#".
        disable  : bool, optional
            Whether to disable the entire progressbar wrapper
            [default: False]. If set to None, disable on non-TTY.
        unit  : str, optional
            String that will be used to define the unit of each iteration
            [default: it].
        unit_scale  : bool or int or float, optional
            If 1 or True, the number of iterations will be reduced/scaled
            automatically and a metric prefix following the
            International System of Units standard will be added
            (kilo, mega, etc.) [default: False]. If any other non-zero
            number, will scale `total` and `n`.
        dynamic_ncols  : bool, optional
            If set, constantly alters `ncols` and `nrows` to the
            environment (allowing for window resizes) [default: False].
        smoothing  : float, optional
            Exponential moving average smoothing factor for speed estimates
            (ignored in GUI mode). Ranges from 0 (average speed) to 1
            (current/instantaneous speed) [default: 0.3].
        bar_format  : str, optional
            Specify a custom bar string formatting. May impact performance.
            [default: '{l_bar}{bar}{r_bar}'], where
            l_bar='{desc}: {percentage:3.0f}%|' and
            r_bar='| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, '
              '{rate_fmt}{postfix}]'
            Possible vars: l_bar, bar, r_bar, n, n_fmt, total, total_fmt,
              percentage, elapsed, elapsed_s, ncols, nrows, desc, unit,
              rate, rate_fmt, rate_noinv, rate_noinv_fmt,
              rate_inv, rate_inv_fmt, postfix, unit_divisor,
              remaining, remaining_s, eta.
            Note that a trailing ": " is automatically removed after {desc}
            if the latter is empty.
        initial  : int or float, optional
            The initial counter value. Useful when restarting a progress
            bar [default: 0]. If using float, consider specifying `{n:.3f}`
            or similar in `bar_format`, or specifying `unit_scale`.
        position  : int, optional
            Specify the line offset to print this bar (starting from 0)
            Automatic if unspecified.
            Useful to manage multiple bars at once (eg, from threads).
        postfix  : dict or *, optional
            Specify additional stats to display at the end of the bar.
            Calls `set_postfix(**postfix)` if possible (dict).
        unit_divisor  : float, optional
            [default: 1000], ignored unless `unit_scale` is True.
        write_bytes  : bool, optional
            If (default: None) and `file` is unspecified,
            bytes will be written in Python 2. If `True` will also write
            bytes. In all other cases will default to unicode.
        lock_args  : tuple, optional
            Passed to `refresh` for intermediate output
            (initialisation, iterating, and updating).
        nrows  : int, optional
            The screen height. If specified, hides nested bars outside this
            bound. If unspecified, attempts to use environment height.
            The fallback is 20.
        colour  : str, optional
            Bar colour (e.g. 'green', '#00ff00').
        delay  : float, optional
            Don't display until [default: 0] seconds have elapsed.
        gui  : bool, optional
            WARNING: internal parameter - do not use.
            Use tqdm.gui.tqdm(...) instead. If set, will attempt to use
            matplotlib animations for a graphical output [default: False].

        """
        # call super
        super().__init__(
            iterable=iterable, desc=desc, total=total, leave=leave, file=file,
            ncols=ncols, mininterval=mininterval, maxinterval=maxinterval,
            miniters=miniters, ascii=ascii, disable=settings.DISABLE_PROGRESS_BAR,
            unit=unit, unit_scale=unit_scale, dynamic_ncols=dynamic_ncols,
            smoothing=smoothing, bar_format=bar_format, initial=initial,
            position=position, postfix=postfix, unit_divisor=unit_divisor,
            write_bytes=write_bytes, lock_args=lock_args, nrows=nrows,
            colour=colour, delay=delay, gui=gui,
        )

    def __enter__(self) -> "ProgressBar":

        # hide if any spinner is running
        _s = Spinner.get_last_spinner()
        if _s is not None:
            _s.hide()

        # call super and return
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, tb):

        # show if any spinner was hidden during __enter__
        _s = Spinner.get_last_spinner()
        if _s is not None:
            _s.show()

        # call super and return
        return super().__exit__(exc_type, exc_value, tb)

    def hook_for_urlretrive(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.

        To be used with
        >>> from urllib import request
        >>> request.urlretrieve()
        """
        if tsize is not None:
            # noinspection PyAttributeOutsideInit
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


class Spinner(Yaspin):
    """
    todo: try alive_progress (yaspin+tqdm features)

    todo: find use case and see where to use ;)
    The spinner also works with generator .... but note that the the
    generator should be iterated completely or else there will be side effects:
    def f():
        with logger.Spinner(title="title") as spinner:
            for i in range(10):
                spinner.info(msg=f"info {i}")
                yield i
    ii = f()
    for i in ii:
        ...
        # break  # uncomment this to see side effects
    """
    COLOR = "yellow"
    SPINNER_WRAP_WIDTH = int(WRAP_WIDTH*1.5)
    TILDA_PREFIX = "~ "
    NESTED_SPINNERS_STORE = []  # type: t.List[Spinner]

    @property
    def log_to_file(self) -> bool:
        """
        Log if file logger is available and there is only one logger in
        NESTED_SPINNERS_STORE
        """
        if len(self.NESTED_SPINNERS_STORE) > 1:
            return False
        return True

    def __init__(
        self, *,
        title: str,
        logger: "Logger",
        timeout_seconds: int = None,
        track_timeout_seconds: int = None,
        hard_timeout_seconds: int = None,
        spinner=None,
        text="",
        on_color=None,
        attrs=None,
        reversal=False,
        side="left",
        sigmap=None,
    ):
        """
        Get spinner for displaying status for long running tasks.

        Args:
            title:
            logger:
            timeout_seconds:
            track_timeout_seconds:
            hard_timeout_seconds:
            spinner:
            text:
            on_color:
            attrs:
            reversal:
            side:
            sigmap:
        """
        self.title = title
        self.logger = logger
        self.timeout_seconds = timeout_seconds
        self.track_timeout_seconds = track_timeout_seconds
        self.hard_timeout_seconds = hard_timeout_seconds
        # noinspection PyTypeChecker
        self.started_at = None  # type: datetime
        # noinspection PyTypeChecker
        self.last_timeout_at = None  # type: datetime
        # noinspection PyTypeChecker
        self.last_track_timeout_at = None  # type: datetime

        # variable to track if user wants top use self.completed method
        # always True unless the user states in self.completed() if it failed
        self.success = True

        # variable to indicate that spinner is aborted
        self.aborted = False

        # create prefix based on nesting level
        self.prefix = "  " + \
                      self.TILDA_PREFIX * (len(self.NESTED_SPINNERS_STORE) + 1)

        # skip time related
        self.skip_time_for_current_step = 0
        self.skip_time_from_start = 0

        # init init_validate
        self.init_validate()

        # call super
        super().__init__(
            spinner=spinner,
            text=text,
            color=self.COLOR,
            on_color=on_color,
            attrs=attrs,
            reversal=reversal,
            side=side,
            sigmap=sigmap,
        )

        # init some variables
        # noinspection PyTypeChecker
        self.started_at = None  # type: datetime
        # noinspection PyTypeChecker
        self.last_timeout_at = None  # type: datetime
        # noinspection PyTypeChecker
        self.last_track_timeout_at = None  # type: datetime

    def __enter__(self) -> "Spinner":
        # every time we enter set it to True, because we cannot guarantee if
        # the user does not use self.completed() method
        # Variable to track if user wants to use self.completed method
        # Always True unless the user states in self.completed() if it failed
        self.success = True

        # hide parent spinner if present then append in next step
        if bool(self.NESTED_SPINNERS_STORE):
            self.NESTED_SPINNERS_STORE[-1].hide()
        self.NESTED_SPINNERS_STORE.append(self)

        # store some timings
        self.started_at = datetime.now()
        self.last_timeout_at = self.started_at
        self.last_track_timeout_at = self.started_at

        # skip time related
        self.skip_time_for_current_step = 0
        self.skip_time_from_start = 0

        # log to file, console and spinner console
        _msg = f"{self.title} started ..."
        _prefix = Emoji.PROCESS_START_PREFIX
        if self.log_to_file:
            self.logger.info(msg=_msg, prefix=_prefix)
        self.log_on_spinner_console(
            msg=_msg, prefix=_prefix, annotate_with_time_elapsed=False)

        # call super
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # skip time related
        self.skip_time_for_current_step = 0
        self.skip_time_from_start = 0

        # just make sure
        self.stop()

        # call super
        _ret = super().__exit__(exc_type, exc_val, exc_tb)

        # if aborted return immediately ... no need to indicate if success or
        # fail
        if self.aborted:
            return _ret

        # log to file, console and spinner console
        _delta = datetime.now() - self.started_at
        _msg = f"{self.title} finished in {_delta.total_seconds():.2f} sec ..."
        _prefix = Emoji.SUCCESS_PREFIX if self.success else Emoji.FAIL_PREFIX
        self.log_on_spinner_console(
            msg=_msg, prefix=_prefix, annotate_with_time_elapsed=False)
        if self.log_to_file:
            self.logger.info(msg=_msg, prefix=_prefix)

        # pop out from nested store and then show parent spinner in next step
        # No
        try:
            self.NESTED_SPINNERS_STORE.pop()
        except IndexError:
            raise IndexError(
                f"This is some coding bug ... SHOULD NEVER HAPPEN"
            )
        if bool(self.NESTED_SPINNERS_STORE):
            self.NESTED_SPINNERS_STORE[-1].show()

        # return
        return _ret

    def init_validate(self):

        # check message lengths if provided as we will not wrap them
        if len(self.title) > SPINNER_TITLE_WIDTH:
            raise Exception(
                f"Spinner title is too long {len(self.title)} > "
                f"{SPINNER_TITLE_WIDTH}"
            )

    def annotate_with_time_elapsed(self, *, msg: str) -> str:
        _delta = datetime.now() - self.started_at
        return f"{_delta.total_seconds(): 4.0f} sec | {msg}"

    def log_on_spinner_console(
        self, *, msg: str,
        prefix: str,
        msgs: MESSAGES_TYPE = None,
        annotate_with_time_elapsed: bool = True,
    ):
        # just to reduce boiler plate code ... also change text of spinner
        # runner
        self.text = f"{msg[:self.SPINNER_WRAP_WIDTH]} ..."

        # add time delta
        if annotate_with_time_elapsed:
            msg = self.annotate_with_time_elapsed(msg=msg)

        wrap_msgs = parse_msgs(
            msg=msg, msgs=msgs, prefix=f"{self.prefix}{prefix}",
            wrap_width=self.SPINNER_WRAP_WIDTH,
        )
        # logs to console only
        for _msg in wrap_msgs:
            self.write(_msg)

    def info(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        annotate_with_time_elapsed: bool = True,
    ):
        self.log_on_spinner_console(
            msg=msg, msgs=msgs, prefix=Emoji.SPINNER_INFO_PREFIX,
            annotate_with_time_elapsed=annotate_with_time_elapsed
        )

    def abort(self):
        # so that __exit__ can take action
        self.aborted = True

        # todo: removed as it console logger looks cluttered with spinner aborts
        # log to file, console and spinner console
        # _delta = datetime.now() - self.started_at
        # _msg = f"(aborted) " \
        #        f"{self.title} aborted after {_delta.total_seconds():.2f} " \
        #        f"sec ..."
        # self.log_on_spinner_console(
        #     msg=_msg, prefix=Emoji.ABORT_PREFIX,
        #     annotate_with_time_elapsed=False)
        # if self.log_to_file:
        #     self.logger.info(msg=_msg, prefix=Emoji.ABORT_PREFIX)

        # stop spinner
        self.stop()

    def timeout(self) -> bool:

        # get the delta time elapsed
        _delta = datetime.now() - self.last_timeout_at

        # check if timed out
        if _delta.total_seconds() < self.timeout_seconds + \
                self.skip_time_for_current_step:
            return False
        else:
            # note we reset timeout so you can reuse it ... if you intend to
            # exit after timeout use the return True value to exit .... but
            # note that by default next call will return False if less than
            # self.timeout_seconds as we reset the self.last_timeout_at
            self.last_timeout_at = datetime.now()
            return True

    def track_timeout(self) -> bool:

        # get the delta time elapsed
        _delta = datetime.now() - self.last_track_timeout_at

        # check if timed out
        if _delta.total_seconds() < self.track_timeout_seconds + \
                self.skip_time_for_current_step:
            return False
        else:
            self.last_track_timeout_at = datetime.now()
            return True

    def hard_timeout(self) -> bool:

        # get the delta time elapsed
        _delta = datetime.now() - self.started_at

        # return
        return _delta.total_seconds() >= self.hard_timeout_seconds + \
            self.skip_time_from_start

    def time_elapsed_in_sec(self) -> int:
        return int((datetime.now() - self.started_at).total_seconds())

    def skip_time(self, skip_time_in_sec: int):
        self.skip_time_for_current_step = skip_time_in_sec
        self.skip_time_from_start += skip_time_in_sec

    @classmethod
    def get_last_spinner(cls) -> t.Union[None, "Spinner"]:
        if bool(cls.NESTED_SPINNERS_STORE):
            return cls.NESTED_SPINNERS_STORE[-1]
        else:
            return None


class Logger:
    """
    Note we will always use pythons inbuilt logging
    But for extra stuff we will use/extend `logging.Handler` interface and setup it in
    `Logger.setup_handlers`

    This class provided methods like info, warning etc. to finally log things.
    Although handlers and filters might handle this well we might want dapr
    """

    @property
    def level(self) -> int:
        return self.log.level

    @level.setter
    def level(self, value: int):
        self.log.setLevel(value)

    @property
    def propagate(self) -> bool:
        return self.log.propagate

    @propagate.setter
    def propagate(self, value: bool):
        self.log.propagate = value

    @property
    def emoji_name(self) -> str:
        global _MODULE_EMOJI_MAPPING
        # replace with emojis
        _emoji_logger_name = module_name_to_emoji(self.module.__name__)

        # if running from external python script add the python file name
        if self.module.__name__ == "__main__":
            _emoji_logger_name = \
                f"{_emoji_logger_name} " \
                f"({pathlib.Path(self.module.__file__).name})"

        # return
        return _emoji_logger_name

    def __init__(
        self,
        module: types.ModuleType,
        level: int = logging.NOTSET,
        propagate: bool = False,
    ):
        """

        Args:
            module: module to log for
            level:
              default is show all logs ...
              all handlers can log for logs above or at same level
            propagate: propagate log to handlers of parent loggers
        """
        global _LOGGER

        # ---------------------------------------------------- 01
        # validate ... check if in LOGGERS dict
        if module.__name__ in _LOGGERS.keys():
            raise KeyError(
                f"Logger for module {module.__name__} was already "
                f"registered in _LOGGERS dict ... Make sure you are "
                f"using `get_logger()` method instead of creating instances "
                f"on your own."
            )

        # ---------------------------------------------------- 02
        # save references
        self.module = module

        # ---------------------------------------------------- 03
        # make and keep instance of logging logger
        self.log = logging.getLogger(self.emoji_name)

        # ---------------------------------------------------- 04
        # set log level and propagate
        self.level = level
        self.propagate = propagate

        # ---------------------------------------------------- 05
        # add emoji filter
        self.log.addFilter(EmojiMapperFilter())

        # ---------------------------------------------------- 06
        # Check for global key _LOGGER if set properly ...
        # NOTE: If LOGGER variable is not available that means we are
        #       creating Logger for this (i.e. logger.py) module. Then in
        #       that case we need to use `self`.
        if "_LOGGER" not in globals().keys():
            assert self.module.__name__ == __name__, \
                f"Note that the first logger to get created is for the " \
                f"module same as this file i.e. {__name__}. Also in that " \
                f"case the global var _LOGGER should not be set in that case."
            _LOGGER = self
        else:
            assert self.module.__name__ != __name__, \
                f"This should not happen as if global var _LOGGER is " \
                f"available then then no other module can have name " \
                f"{__name__}"

        # ---------------------------------------------------- xx
        # Send message using the LOGGER for `logger.py`
        # _LOGGER.info(
        #     msg=f"Logger configured for:",
        #     msgs=[
        #         {
        #             "module": self.module.__name__,
        #             "display name": _emoji_logger_name,
        #         }
        #     ]
        # )

    def setup_handlers(
        self,
        # level
        level: bool = logging.NOTSET,
        # stream
        use_stream_handler: bool = True,
        stream_handler_level: int = logging.DEBUG,
        stream_handler_format: logging.Formatter = Formatters.default,
        # for logging to file
        use_file_handler: bool = False,
        max_log_file_size: int = 1 * 1024 * 1024,  # 1 MB
        max_log_file_backups: int = 5,
        log_dir: pathlib.Path = None,
        file_handler_level: int = logging.DEBUG,
        file_handler_format: logging.Formatter = Formatters.default,
        # todo: add special handler for this by extending `logging.Handler` and
        #  making it work alongside dapr.pubsub or dapr.tracker
        # todo: explore `toolcraft.dapr.tracker` to have log listener widgets binded
        #  with `use_segregated_logging` feature ... we can have pubsub model where the
        #  logger widgets are subscribed to telemetry of dapr server
        #  For now easy thing is to see log dir and create same number of widgets as
        #  there are files inside log dir
        use_remote_handler: bool = False,
        remote_handler_level: int = logging.DEBUG,
        remote_handler_format: logging.Formatter = Formatters.default,
        # segregate logging ... currently only used by file handler
        use_segregated_logging: bool = False,
    ):
        # -------------------------------------------------- 01
        # remove handlers if any
        self.log.handlers.clear()

        # -------------------------------------------------- 02
        # set level
        self.level = level

        # -------------------------------------------------- 03
        # stream handler
        if use_stream_handler:
            # get stream handler
            _sh = logging.StreamHandler(_LOGGER_STREAM)
            # configure stream handler
            _sh.setLevel(stream_handler_level)
            _sh.setFormatter(stream_handler_format)
            # register handler
            self.log.addHandler(_sh)

        # -------------------------------------------------- 04
        # file handler
        if use_file_handler:
            # check if log dir provided
            if log_dir is None:
                raise Exception(
                    "Please provide log dir if you are using file handler ..."
                )
            # create dir
            log_dir.mkdir(parents=True, exist_ok=True)
            # log file
            _log_file_name = f"{self.module.__name__}.logs" \
                if use_segregated_logging else "common.logs"
            # make handler
            _fh = handlers.RotatingFileHandler(
                log_dir / _log_file_name, encoding="utf-8", maxBytes=max_log_file_size,
                backupCount=max_log_file_backups,
            )
            # set fh
            _fh.setLevel(file_handler_level)
            _fh.setFormatter(file_handler_format)
            # register
            self.log.addHandler(_fh)

        # -------------------------------------------------- 04
        # pubsub handler
        if use_remote_handler:
            raise Exception("remote handler is not yet supported ...")

    # level: 10
    def debug(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.debug(_msg)

    # level: 20
    def info(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.info(_msg)

    # level: 30
    def warning(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.warning(_msg)

    # level: 40
    def error(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX,
        no_wrap: bool = False,
    ):
        wrap_msgs = parse_msgs(
            msg=msg, msgs=msgs, prefix=prefix, no_wrap=no_wrap)
        for _msg in wrap_msgs:
            self.log.error(_msg)

    # level: 50
    def critical(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.critical(_msg)


def get_logger(
    module: t.Optional[
        t.Union[types.ModuleType, str]
    ] = None
) -> Logger:
    # global dict to store _LOGGERS
    global _LOGGERS

    # automatically extract module
    if module is None:
        module = inspect.getmodule(inspect.currentframe().f_back)

    # if module is str try to import it
    if isinstance(module, str):
        module = sys.modules[module]

    # if not registered register
    if module.__name__ not in _LOGGERS.keys():
        _LOGGERS[module.__name__] = Logger(module)

    # return the logger instance stored in container
    return _LOGGERS[module.__name__]


# ******************************* ONE TIME ************************************
# logger for logger module
# noinspection PyTypeChecker
# Note that getting logger is equivalent to
#   LOGGER = Logger(__name__)
# And hence in next step we do direct assignment
# There are three places where you see this LOGGER
# - Here
# - Next step
# - in __post_init__ method of Logger
# todo: can this be don any simpler
_LOGGER = get_logger()  # type: Logger

# configure logger if loading for first time
# container to store all loggers in application
__ONE_TIME = False
if not __ONE_TIME:
    __ONE_TIME = True

    # todo: we should not be taking control of the users tensorflow
    #  environment. We need to seek permission before doing so ... explore later
    # if tensorflow is available then update the tensorflow logger
    try:
        # todo: commenting as it causes dependencies
        # noinspection PyUnresolvedReferences
        # import tensorflow
        # _tfl = tensorflow.get_logger()
        # _tfl.setLevel(logging.ERROR)
        # _tfl.parent.setLevel(logging.ERROR)
        ...
    except ImportError as ie:
        ...

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        # 'formatters': {
        #     'standard': {
        #       'format': '%(asctime)s [%(levelname).4s] %(name)s: %(message)s'
        #     },
        # },
        # 'handlers': {
        #     'default': {
        #         'level': logging.NOTSET,
        #         'formatter': 'standard',
        #         'class': 'logging.StreamHandler',
        #     },
        # },
        # 'loggers': {
        #     '': {
        #         'handlers': ['default'],
        #         'level': logging.NOTSET,
        #         'propagate': True
        #     },
        #     'tensorflow': {
        #         'handlers': ['default'],
        #         'level': logging.ERROR,
        #         'propagate': False
        #     },
        #     'scandal.dataset': {
        #         'handlers': ['default'],
        #         'level': logging.INFO,
        #         'propagate': False
        #     },
        # }
    }

    lc.dictConfig(LOGGING_CONFIG)


def try_spinner_logger_from_class():
    import time
    from random import randint

    ll = get_logger()

    ll.info(msg="try_spinner_logger")

    class TrySpinnerDec:

        # noinspection PyMethodMayBeStatic
        def long_running_function(self):
            with Spinner(
                logger=ll,
                title="Downloading",
                timeout_seconds=1,
            ) as spinner:
                for i in range(3):
                    spinner.text = f"Downloading {i} ..."
                    spinner.wait_over()
                    spinner.info(msg=f"Some information {i}")
                    time.sleep(2)  # time consuming code

                    with Spinner(
                        title="BlaBlaBla",
                        logger=ll,
                    ) as spinner1:
                        for i1 in range(3):
                            spinner1.text = f"BlaBlaBla {i1} ..."
                            spinner1.info(msg=f"BlaBlaBla Some information"
                                              f" {i1}")
                            time.sleep(2)  # time consuming code

                        success = randint(0, 1)
                        spinner1.success = success

                success = randint(0, 1)
                spinner.success = success

    TrySpinnerDec().long_running_function()
