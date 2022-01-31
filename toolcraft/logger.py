"""
Main aim of new logger lib
+ get rid of typer/tqdm/yaspin
+ keep main interface standard
  + always use standard logging handler
  + for file handling totally rely on logging.FileHandler
+ Fancy things can be handled by extending logging.Handler
  + example we will use rich libs handler
+ todo: when used as server make sure to remove rich based cli logger and only have
    the default file handler
    >>>
+ todo: traceback logging only on selected modules
    Brainstorm more on this use case
    https://stackoverflow.com/questions/31949760/how-to-limit-python-traceback-to-specific-files
    + only show traceback that goes through users code (optional toolcraft code)
    + if error is in third party lib then show special error else show the error from
      users code where the trace only includes code from users code
      (with optional toolcraft code)
+ todo: dapr telemetry styled streamed logging needs to be explored
    this will make it possible for gui clients to subscribe to dapr
    server for listen to logs
    (make sure to implement this via extending `logging.Handler`)
+ todo: extend support to textual as an easy update (it is built over rich)
    https://github.com/Textualize/textual
+ todo: eventually delete the deprecated old code file logger_.py
+ todo: find best possible legit way with logging to do efficient emoji mapping
    + have a emoji field in module so that logger can use that
    + explore logging.Filter and logging.Formatter
    + scavange code in
      >>> __emoji_mapping()
"""
import pathlib

import rich
import dataclasses
import typing as t
import types
import inspect
import sys
import logging
import logging.handlers
from rich.logging import RichHandler
from rich import emoji

AVAILABLE_EMOJI = emoji.EMOJI

MESSAGES_TYPE = t.List[
    t.Union[
        str,
        t.List,
        t.Tuple,
        t.Dict,
    ]
]


def get_base_formatter() -> logging.Formatter:
    return logging.Formatter(
        # f'%(short_name)s {Emoji.EMOJI_TIME} %(asctime)s %(name)s: '
        # f'%(message)s'
        f'%(short_name)s: %(message)s'
    )


def get_rich_handler() -> RichHandler:
    """
    per handler do
    + set level
    + set formatter
    + add filters specific to handler
    """
    from rich import print, emoji
    # -------------------------------------------------------- 01
    # get handler
    _h = RichHandler(
        level=logging.NOTSET,
        markup=True,
        rich_tracebacks=True,
    )

    # -------------------------------------------------------- 02
    # set level
    # this is done above so commenting out
    # just keep these lines for reference on how initialize Handlers
    # _h.setLevel(level=logging.NOTSET)

    # -------------------------------------------------------- 03
    # set formatter
    _h.setFormatter(fmt=get_base_formatter())

    # -------------------------------------------------------- 04
    # add filters
    # _h.addFilter(...)

    # -------------------------------------------------------- 05
    # return
    return _h


def get_file_handler(log_file: pathlib.Path) -> logging.FileHandler:
    """
    per handler do
    + set level
    + set formatter
    + add filters specific to handler

    Default behaviour:
    + log files will be created in cwd ... to change this behaviour you need to think

    todo: while using toolcraft.tools we want disable file_handler behaviour so that
      users do not get log files in their working dir while using tools from toolcraft
    """
    # -------------------------------------------------------- 01
    # get handler
    # this can make multiple log files for now stick up with simple things
    # _h = logging.handlers.RotatingFileHandler()
    _h = logging.FileHandler(
        filename=log_file, mode='a', encoding='utf8',
    )

    # -------------------------------------------------------- 02
    # set level
    _h.setLevel(level=logging.NOTSET)

    # -------------------------------------------------------- 03
    # set formatter
    _h.setFormatter(fmt=get_base_formatter())

    # -------------------------------------------------------- 04
    # add filters
    # _h.addFilter(...)

    # -------------------------------------------------------- 05
    # return
    return _h


def setup_logging(
    level: int = logging.NOTSET,
    propagate: bool = False,
    handlers: t.List[logging.Handler] = None,
    filters: t.List[logging.Filter] = None,
):
    """
    Setup handlers, formatters and filters stc. here ...

    todo: read from .toolcraft config.toml file to read settings for how to handle logs
      + which handlers to use
      + which formatters to use
      + which filters to use
      + interactive edit of config file on server from client to disable/enable logs
        ( dont know hoe this will behave on runtime and how to call
         `setup_logging()` multiple times )

    todo: In server mode (i.e. settings.DAPR_SERVE_MODE is True)
      we will need to log only to file ...
      so explore suppressing rich logging or maybe it already happens

    NOTE: do not perform module level handlers/filters ....
      it is easy to implement but fruitless as we do not see any purpose

    Refer logging.basicConfig which does things to root logger we carry similar
    opration with some customizations
    >>> logging.basicConfig

    """
    # thread safety
    # noinspection PyUnresolvedReferences,PyProtectedMember
    logging._acquireLock()
    try:

        # --------------------------------------------------------------- 01
        # get root logger
        _root_logger = logging.root

        # --------------------------------------------------------------- 02
        # remove any handlers or filters
        for _h in _root_logger.handlers[:]:
            _root_logger.removeHandler(_h)
            _h.close()
        for _f in _root_logger.filters[:]:
            _root_logger.removeFilter(_f)

        # --------------------------------------------------------------- 03
        # add filters and handlers to root logger
        if bool(filters):
            for _f in filters:
                _root_logger.addFilter(_f)
        if bool(handlers):
            for _h in handlers:
                _root_logger.addHandler(_h)

        # --------------------------------------------------------------- 04
        # set basic things
        _root_logger.setLevel(level=level)
        _root_logger.propagate = propagate

    # ----
    finally:
        # noinspection PyUnresolvedReferences,PyProtectedMember
        logging._releaseLock()


# make sure that logging is set up before any other loggers are added
# Default behaviour is to log to console using rich handler ...
# If you want to log to file supply log_file kwarg
# call setup_logging from your code again if you want to have other combinations
# for logger
setup_logging(
    handlers=[
        get_rich_handler(),
    ]
)


@dataclasses.dataclass(frozen=True)
class LoggingMeta:
    """

    `short_name`
        + Can be used by filter to add field to LogRecord to display in logs a
          short name instead of module name that will be available via field name
        + also, you can assign emoji as string
    `suppress_logs`
        + In case you want to suppress logs for that module ...
    `bypass_traceback`
        + when exceptions are raised then the tracks for this module are bypassed
        + todo check main docstring above and discussion here
            https://stackoverflow.com/questions/31949760/how-to-limit-python-traceback-to-specific-files
    """
    short_name: str
    suppress_logs: bool = False
    bypass_traceback: bool = False

    def __post_init__(self):

        # todo: implement this is needed
        if self.suppress_logs:
            raise Exception("Not yet supported ...")
        if self.bypass_traceback:
            raise Exception("Not yet supported ...")


# All the logger meta info can be exploited in custom logging.Filters
# todo: do when needed
# Also note that this also helps in making sure that get_logger is called only
# once in module using syntax `_LOGGER = logger.get_logger(...)
_ALL_LOGGERS_META = {}  # type: t.Dict[str, LoggingMeta]

# just for precaution call with no name so that we are sure that first
# logging.Logger instance created is for root, and it is backed up
# Also can be used for logging here, although it might not be needed
_LOGGER = logging.getLogger()
_ALL_LOGGERS_META[_LOGGER.name] = LoggingMeta(short_name="root")


def __emoji_mapping():
    # todo: have a emoji field in module so that logger can use that
    # a mapping for replacing text with emoji
    #      https://emojipedia.org/
    #      http://shapecatcher.com/
    #      ✅  ❎ ❌ 👍  ✔ ✘ ❎ ✅ ✅ ✅ ⌛ ⏳ ⚿ 🗝️ 🔑 🔐 🔒 🔰 🌡️ 🗺️
    #      📈 📉 📊 🧬 ϻ  ƝƝ 📥 📩 📤 ⬇️🔻 📂 🌀
    _MODULE_EMOJI_MAPPING = {
        "__main__": "🎬",
        "__base__": "⭐",
        "util": "🛠️",
        "logger": "📝",
        "scandal": "🕵️",
        "tensorflow": "ƮϜ",
        "experiment": "🧪",
        "marshalling": "🔄",
        "storage": "💾",
        "dataset": "⌸",
        "crypto": "🗝️",
        "error": "☠",
        "core": "🥝",
        "visual": "📉",
        "model": "ƝƝ",
        "download": "📥",
        "file_group": "📂",
        "tf_chkpt": "🌀",
        "analysis": "👁️",
    }

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

    class Formatters:
        default = logging.Formatter(
            # f'%(emoji_level)s {Emoji.EMOJI_TIME} %(asctime)s %(name)s: '
            # f'%(message)s'
            f'%(emoji_level)s %(name)s: %(message)s'
        )

    class EmojiMapperFilter(logging.Filter):
        # todo is this efficient way
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


def get_logger(
    module: t.Optional[
        t.Union[types.ModuleType, str]
    ] = None,
    meta: LoggingMeta = None,
) -> logging.Logger:
    """

    Args:
        module: Even if not passed we can extract it ...
        meta: Can have many usages ... check docstring for
          >>> LoggingMeta

    Returns:

    """
    # ------------------------------------------------------------ 01
    # get globals
    global _ALL_LOGGERS_META

    # ------------------------------------------------------------ 02
    # automatically extract module
    if module is None:
        module = inspect.getmodule(inspect.currentframe().f_back)

    # if module is str try to import it
    if isinstance(module, str):
        module = sys.modules[module]

    # ------------------------------------------------------------ 03
    # make sure that logger name is always module name
    # we do not want to complicate things like earlier code to modify name to emoji
    # instead we will book keep meta info here ... so that if needed you can use some
    # custom logging.Filter to add it to LogRecord
    _logger_name = module.__name__
    if _logger_name in _ALL_LOGGERS_META.keys():
        _LOGGER.warning(msg=f"Make sure that this is called only once per module "
                            f"i.e. `_LOGGER = logger.get_logger(...)`")
        raise KeyError(
            f"There is already a module with name {_logger_name} registered with meta "
            f"info {_ALL_LOGGERS_META[_logger_name]}"
        )
    # if meta not provided assign with empty meta
    if meta is None:
        # noinspection PyArgumentList
        meta = LoggingMeta(short_name=_logger_name)
    # backup
    _ALL_LOGGERS_META[_logger_name] = meta

    # ------------------------------------------------------------ 04
    # make and return logger
    return logging.getLogger(_logger_name)
