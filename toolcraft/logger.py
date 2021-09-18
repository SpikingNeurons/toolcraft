# coding=utf-8
"""
NOTE: we do not use scandal.error as it is not possible here

todo: removing exceptions is difficult ... as it is problematic to import
  .error module ... we can just pretty log the exceptions instead
"""

import logging
from tqdm import tqdm
import typing as t
import dataclasses
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
import dearpygui.dearpygui as dpg

# log dirs
# todo: use `tooling.tool.config` to get these settings from user or
#  configure them
LOG_DIR = pathlib.Path("C:\\.log")
MULTIPROCESSING_LOG_DIR = LOG_DIR / "multiprocessing"
# todo: still not supported
MAX_LOG_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# a container to store loggers for the modules
_LOGGERS = {}  # type: t.Dict[str, _LoggerClass]

# a mapping for replacing text with emoji
#      https://emojipedia.org/
#      http://shapecatcher.com/
#      ✅  ❎ ❌ 👍  ✔ ✘ ❎ ✅ ✅ ✅ ⌛ ⏳ ⚿ 🗝️ 🔑 🔐 🔒 🔰 🌡️ 🗺️
#      📈 📉 📊 🧬 ϻ  ƝƝ 📥 📩 📤 ⬇️🔻 📂 🌀
_MODULE_EMOJI_MAPPING = {
    "__main__"   : "🎬",
    "__base__"   : "⭐",
    "util"       : "🛠️",
    "logger"     : "📝",
}

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


class Emoji:

    DEFAULT_PREFIX = "🔊 "
    PROCESS_START_PREFIX = "🏁 "
    PROCESS_STOP_PREFIX = "🛑 "
    TRACEBACK_PREFIX = "⚡ "
    SUCCESS_PREFIX = "✅ "
    ABORT_PREFIX = "🚫 "
    FAIL_PREFIX = "💥 "
    SPINNER_TIMEOUT_PREFIX = "⏳... "
    SPINNER_INFO_PREFIX = "ℹ️ "

    EMOJI_SKULL = "☠️"
    EMOJI_TIME = "⏰"
    EMOJI_NOTSET_LEVEL = "🔆"
    EMOJI_DEBUG_LEVEL = "🐞"
    EMOJI_INFO_LEVEL = "ℹ️"
    EMOJI_WARNING_LEVEL = "⚠️"
    EMOJI_ERROR_LEVEL = "💣"
    EMOJI_CRITICAL_LEVEL = "☢️"


def module_name_to_emoji(module_name: str) -> str:
    global _MODULE_EMOJI_MAPPING
    return ".".join(
        [
            _MODULE_EMOJI_MAPPING.get(v, v)
            for v in module_name.split(".")
        ]
    )


def update_emoji_map(emoji_map: t.Dict[str, str]):
    """
    Use this method wo map new keys and the symbols for logging
    Args:
        emoji_map:

    Returns:

    """
    global _MODULE_EMOJI_MAPPING
    for k, v in emoji_map.items():
        if k in _MODULE_EMOJI_MAPPING.keys():
            raise KeyError(
                f"Key {k} already exists in emoji map with symbol "
                f"{_MODULE_EMOJI_MAPPING[k]}. You cannot override it."
            )
        for _k, _v in _MODULE_EMOJI_MAPPING.items():
            if _v == v:
                raise ValueError(
                    f"Emoji map already has symbol {v} with key {_k}. So you "
                    f"cannot use this value for the new key {k}."
                )
        _MODULE_EMOJI_MAPPING[k] = v


def parse_iterators(
    obj: t.Union[list, tuple, dict],
    nest_level: int = 0,
    wrap_width: int = WRAP_WIDTH,
    no_wrap: bool = False,
) -> t.List[str]:

    # increment for use with recursive calls
    nest_level += 2
    prefix = " " * nest_level + "- "
    _ret = []

    if isinstance(obj, (list, tuple)):
        for o in obj:
            if isinstance(o, (list, tuple, dict)):
                _ret.extend(
                    parse_iterators(o, nest_level)
                )
            else:
                _ret.extend(
                    _wrap_message(
                        msg=f"{o}", prefix=prefix,
                        wrap_width=wrap_width, no_wrap=no_wrap
                    )
                )
    elif isinstance(obj, dict):
        for k, o in obj.items():
            if isinstance(o, (list, tuple, dict)):
                _ret.extend(
                    _wrap_message(
                        msg=f"{k}: ", prefix=prefix,
                        wrap_width=wrap_width, no_wrap=no_wrap
                    )
                )
                _ret.extend(
                    parse_iterators(o, nest_level)
                )
            else:
                _ret.extend(
                    _wrap_message(
                        msg=f"{k}: {o}", prefix=prefix,
                        wrap_width=wrap_width, no_wrap=no_wrap
                    )
                )
    else:
        raise TypeError(
            f"Unrecognized type for value {obj} with type {type(obj)}"
        )

    return _ret


def parse_msgs(
    *,
    msg: str,
    msgs: MESSAGES_TYPE = None,
    prefix: str = Emoji.DEFAULT_PREFIX,
    wrap_width: int = WRAP_WIDTH,
    no_wrap: bool = False,
) -> t.List[str]:
    _ret_msgs = []

    # process msg
    if isinstance(msg, str):
        _ret_msgs.extend(
            _wrap_message(
                msg=msg, prefix=prefix,
                wrap_width=wrap_width, no_wrap=no_wrap
            )
        )
    else:
        raise TypeError(
            f"The attribute msg should always be a str, found {type(msg)}"
        )

    # if no msgs return
    if msgs is None:
        return _ret_msgs

    # loop over and parse msgs
    for i, m in enumerate(msgs):
        if isinstance(m, str):
            _ret_msgs.extend(
                _wrap_message(
                    msg=m, prefix="▫️ ",
                    wrap_width=wrap_width, no_wrap=no_wrap
                )
            )
        elif isinstance(m, (list, tuple, dict)):
            _ret_msgs.extend(
                parse_iterators(
                    m, nest_level=1,
                    wrap_width=wrap_width, no_wrap=no_wrap
                )
            )
        else:
            raise TypeError(
                f"One items at location {i!r} in the msgs list has "
                f"unsupported type {type(m)}. We only allow str, list, tuple, "
                f"and dict"
            )

    # return
    return _ret_msgs


def _wrap_message(
    *, msg: str,
    prefix: str = Emoji.DEFAULT_PREFIX,
    wrap_width: int = WRAP_WIDTH,
    no_wrap: bool = False,
) -> t.List[str]:

    # adjust wrap_width for handling prefix
    wrap_width = wrap_width - len(prefix)

    # if wrap or no wrap
    if no_wrap:
        m_wraps = [msg]
    else:
        m_wraps = textwrap.wrap(msg, width=wrap_width)

    if prefix is None:
        return m_wraps
    else:
        _ret = []
        _empty_prefix = " "*(len(prefix)+1)
        for i, mw in enumerate(m_wraps):
            _prefix = prefix if i == 0 else _empty_prefix
            _ret.append(f"{_prefix}{mw}")
        return _ret


def file_incremental_rename(file: pathlib.Path):
    _files = []
    for f in file.parent.iterdir():
        if f.name.startswith(file.name + "_"):
            _files.append(f)

    _incr_counts = [int(f.name.split("_")[1]) for f in _files] + [1]
    _max_count = max(_incr_counts)

    _renamed_file = file.parent / f"{file.name}_{_max_count+1}"
    file.replace(_renamed_file)


class Formatters:
    default = logging.Formatter(
        # f'%(emoji_level)s {Emoji.EMOJI_TIME} %(asctime)s %(name)s: '
        # f'%(message)s'
        f'%(emoji_level)s %(name)s: %(message)s'
    )


class EmojiMapperFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> int:

        # logging level emoji
        if record.levelno == logging.NOTSET:
            record.emoji_level = Emoji.EMOJI_NOTSET_LEVEL
        elif record.levelno == logging.DEBUG:
            record.emoji_level = Emoji.EMOJI_DEBUG_LEVEL
        elif record.levelno == logging.INFO:
            record.emoji_level = Emoji.EMOJI_INFO_LEVEL
        elif record.levelno == logging.WARNING:
            record.emoji_level = Emoji.EMOJI_WARNING_LEVEL
        elif record.levelno == logging.ERROR:
            record.emoji_level = Emoji.EMOJI_ERROR_LEVEL
        elif record.levelno == logging.CRITICAL:
            record.emoji_level = Emoji.EMOJI_CRITICAL_LEVEL
        else:
            raise Exception("Never possible ...")

        return True


class ProgressBar(tqdm):

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
        disable=False,
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
            miniters=miniters, ascii=ascii, disable=disable, unit=unit,
            unit_scale=unit_scale, dynamic_ncols=dynamic_ncols,
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
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


class Spinner(Yaspin):
    """
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

    todo: Yaspin needs to go in favor of typer
      printing and colors -> https://typer.tiangolo.com/tutorial/printing/
      progress bar -> https://typer.tiangolo.com/tutorial/progressbar/
      fast-api -> typer is fast-api for cli also we will get same color
        support etc
      asks for prompt -> https://typer.tiangolo.com/tutorial/prompt/
      nice terminating -> https://typer.tiangolo.com/tutorial/terminating/
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
        logger: "_LoggerClass",
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


class DpgLogger:
    """
    This class cannot be moved to gui module as it will cause cyclic import

    This can be easy and fun

    For every module there will be instance for dpg_log with unique name
    self.logger_module

    We need to make tab bar for each module and have child window inside
    which we will have this tab bar

    Now when logging module changes the active tab in tab bar will switch and
    the logging text will be scrolled ;)

    Also for progress bar we can have add_progress_bar instead of add_text
    in self._log method

    This will have an effect of dynamic log window which can switch itself ...

    todo: DO all this when grpc is in place and we have client and backend
      code segregated ... do not rush as then there will be performance issue
      ... let logging in backend be synced to client in async updates from
      backend ... may be when we have blazor based UI we can think of this
    """
    def __init__(self, logger_module):
        self.logger_module = logger_module

    def setup(self, parent=None):

        self._auto_scroll = True
        self.filter_id = None
        if parent:
            self.window_id = parent
        else:
            self.window_id = dpg.add_window(
                label="mvLogger", pos=(200, 200), width=500, height=500)
        self.count = 0
        self.flush_count = 1000

        with dpg.group(horizontal=True, parent=self.window_id):
            dpg.add_checkbox(
                label="Auto-scroll",
                default_value=True,
                callback=lambda sender:self.auto_scroll(dpg.get_value(sender)))
            dpg.add_button(
                label="Clear",
                callback=lambda: dpg.delete_item(
                    self.filter_id, children_only=True
                )
            )

        dpg.add_input_text(
            label="Filter",
            callback=lambda sender: dpg.set_value(
                self.filter_id, dpg.get_value(sender)
            ),
            parent=self.window_id)
        self.child_id = dpg.add_child(
            parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        with dpg.theme() as self.trace_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 0, 255))

        with dpg.theme() as self.debug_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 128, 255, 255))

        with dpg.theme() as self.info_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))

        with dpg.theme() as self.warning_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 0, 255))

        with dpg.theme() as self.error_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

        with dpg.theme() as self.critical_theme:
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

    def auto_scroll(self, value):
        self._auto_scroll = value

    def _log(self, message, theme):

        self.count += 1

        if self.count > self.flush_count:
            self.clear()

        new_log = dpg.add_text(
            message, parent=self.filter_id, filter_key=message)
        dpg.set_item_theme(new_log, theme)
        if self._auto_scroll:
            scroll_max = dpg.get_y_scroll_max(self.child_id)
            dpg.set_y_scroll(self.child_id, -1.0)

    def log(self, message):
        self._log(message, self.trace_theme)

    def debug(self, message):
        self._log(message, self.debug_theme)

    def info(self, message):
        self._log(message, self.info_theme)

    def warning(self, message):
        self._log(message, self.warning_theme)

    def error(self, message):
        self._log(message, self.error_theme)

    def critical(self, message):
        self._log(message, self.critical_theme)

    def clear(self):
        dpg.delete_item(self.filter_id, children_only=True)
        self.count = 0


@dataclasses.dataclass
class _LoggerClass:
    module: types.ModuleType
    use_stream_handler: bool = True
    use_file_handler: bool = True
    use_separate_file: bool = False
    use_dpg_logger: bool = False
    level: int = logging.DEBUG
    stream_handler_level: int = logging.DEBUG
    file_handler_level: int = logging.DEBUG
    stream_handler_format: logging.Formatter = Formatters.default
    file_handler_format: logging.Formatter = Formatters.default

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

    def __post_init__(self):
        global _LOGGER

        # init init_validate
        self.init_validate()

        # make logger display name
        _emoji_logger_name = self.emoji_name

        # make and keep instance of logging logger
        self.log = logging.getLogger(_emoji_logger_name)

        # add emoji filter
        self.log.addFilter(EmojiMapperFilter())

        # configure logger level
        self.log.setLevel(self.level)

        # reset handlers
        # todo: this avoids double print of logs in console ... contents of
        #  file are fine but FileHandler propagates to parent which prints
        #  the log again
        self.log.propagate = False

        # configure stream handler
        if self.use_stream_handler:
            # get stream handler
            _sh = logging.StreamHandler(_LOGGER_STREAM)

            # configure stream handler
            _sh.setLevel(self.stream_handler_level)
            _sh.setFormatter(self.stream_handler_format)

            # register handler
            self.log.addHandler(_sh)

        # configure file handler
        if self.use_file_handler:

            # get file
            if not LOG_DIR.exists():
                LOG_DIR.mkdir(parents=True)
            _file_name = f"{self.module.__name__}.logs" \
                if self.use_separate_file else "common.logs"
            _file = LOG_DIR / _file_name

            # get file handler
            _fh = handlers.RotatingFileHandler(
                _file,
                encoding="utf-8",
                maxBytes=MAX_LOG_FILE_SIZE, backupCount=100,
            )

            # configure file handler
            _fh.setLevel(self.file_handler_level)
            _fh.setFormatter(self.file_handler_format)

            # register handler
            self.log.addHandler(_fh)

        # if dpg logger
        if self.use_dpg_logger:
            self.dpg_log = DpgLogger()

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

    def init_validate(self):

        # check if in LOGGERS dict
        if self.module.__name__ in _LOGGERS.keys():
            raise KeyError(
                f"Logger for module {self.module.__name__} was already "
                f"registered in _LOGGERS dict ... Make sure you are "
                f"using `get_logger()` method instead of creating instances "
                f"on your own."
            )

        # check if use_separate_file setting needed
        if not self.use_file_handler:
            if self.use_separate_file:
                raise ValueError(
                    f"Setting self.use_separate_file does not matter as you "
                    f"are not using file handler"
                )

        # check logging levels
        if self.stream_handler_level > self.level:
            raise ValueError(
                f"The stream handler log level is greater than the logger "
                f"level ... this is meaningless ..."
            )

        # check logging levels
        if self.file_handler_level > self.level:
            raise ValueError(
                f"The file handler log level is greater than the logger "
                f"level ... this is meaningless ..."
            )

    # level: 10
    def debug(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.debug(_msg)
            if self.use_dpg_logger:
                self.dpg_log.debug(_msg)

    # level: 20
    def info(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.info(_msg)
            if self.use_dpg_logger:
                self.dpg_log.info(_msg)

    # level: 30
    def warning(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.warning(_msg)
            if self.use_dpg_logger:
                self.dpg_log.warning(_msg)

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
            if self.use_dpg_logger:
                self.dpg_log.error(_msg)

    # level: 50
    def critical(
        self, *, msg: str,
        msgs: MESSAGES_TYPE = None,
        prefix=Emoji.DEFAULT_PREFIX
    ):
        wrap_msgs = parse_msgs(msg=msg, msgs=msgs, prefix=prefix)
        for _msg in wrap_msgs:
            self.log.critical(_msg)
            if self.use_dpg_logger:
                self.dpg_log.critical(_msg)


def get_logger(
    module: t.Optional[
        t.Union[types.ModuleType, str]
    ] = None
) -> _LoggerClass:
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
        _LOGGERS[module.__name__] = _LoggerClass(module)

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
_LOGGER = get_logger()  # type: _LoggerClass

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
