"""
Refer:
https://github.com/Textualize/rich/blob/master/examples/dynamic_progress.py
https://github.com/Textualize/rich/blob/master/examples/live_progress.py
"""

import dataclasses
import typing as t
import enum
from rich.emoji import EMOJI
from rich import logging as r_logging
from rich import console as r_console
from rich import highlighter as r_highlighter
from rich import live as r_live
from rich import progress_bar as r_progress_bar
from rich import spinner as r_spinner
from rich import style as r_style
from rich import table as r_table
from rich import text as r_text
from rich import progress as r_progress
from rich import status as r_status
from rich import panel as r_panel
from rich import prompt as r_prompt

from .logger import CustomLogger
from . import error as e


class SpinnerType(enum.Enum):
    """
    Refer
    >>> r_spinner.SPINNERS

    Code to generate this enum fields

    from rich import spinner
    for _ in spinner.SPINNERS.keys():
        print(f"\t{_} = enum.auto()")
    """
    dots = enum.auto()
    dots2 = enum.auto()
    dots3 = enum.auto()
    dots4 = enum.auto()
    dots5 = enum.auto()
    dots6 = enum.auto()
    dots7 = enum.auto()
    dots8 = enum.auto()
    dots9 = enum.auto()
    dots10 = enum.auto()
    dots11 = enum.auto()
    dots12 = enum.auto()
    dots8Bit = enum.auto()
    line = enum.auto()
    line2 = enum.auto()
    pipe = enum.auto()
    simpleDots = enum.auto()
    simpleDotsScrolling = enum.auto()
    star = enum.auto()
    star2 = enum.auto()
    flip = enum.auto()
    hamburger = enum.auto()
    growVertical = enum.auto()
    growHorizontal = enum.auto()
    balloon = enum.auto()
    balloon2 = enum.auto()
    noise = enum.auto()
    bounce = enum.auto()
    boxBounce = enum.auto()
    boxBounce2 = enum.auto()
    triangle = enum.auto()
    arc = enum.auto()
    circle = enum.auto()
    squareCorners = enum.auto()
    circleQuarters = enum.auto()
    circleHalves = enum.auto()
    squish = enum.auto()
    toggle = enum.auto()
    toggle2 = enum.auto()
    toggle3 = enum.auto()
    toggle4 = enum.auto()
    toggle5 = enum.auto()
    toggle6 = enum.auto()
    toggle7 = enum.auto()
    toggle8 = enum.auto()
    toggle9 = enum.auto()
    toggle10 = enum.auto()
    toggle11 = enum.auto()
    toggle12 = enum.auto()
    toggle13 = enum.auto()
    arrow = enum.auto()
    arrow2 = enum.auto()
    arrow3 = enum.auto()
    bouncingBar = enum.auto()
    bouncingBall = enum.auto()
    smiley = enum.auto()
    monkey = enum.auto()
    hearts = enum.auto()
    clock = enum.auto()
    earth = enum.auto()
    material = enum.auto()
    moon = enum.auto()
    runner = enum.auto()
    pong = enum.auto()
    shark = enum.auto()
    dqpb = enum.auto()
    weather = enum.auto()
    christmas = enum.auto()
    grenade = enum.auto()
    point = enum.auto()
    layer = enum.auto()
    betaWave = enum.auto()
    aesthetic = enum.auto()

    def __str__(self):
        return self.name


class SpinnerColumn(r_progress.SpinnerColumn):
    """
    An extended SpinnerColumn which can have many states and spinners
    """

    # noinspection PyMissingConstructor
    def __init__(
        self,
        states: t.Dict[str, t.Union[str, r_text.Text, r_spinner.Spinner]],
        start_state_key: str = "start",
        finished_state_key: str = "finished",
        table_column: t.Optional[r_table.Column] = None,
    ):
        # transform states to respective rich elements
        self.states = {}
        for _k, _v in states.items():
            # if str check is spinner and make Spinner else make it Text
            if isinstance(_v, str):
                if _v in r_spinner.SPINNERS.keys():
                    _v = r_spinner.Spinner(name=_v)
                else:
                    _v = r_text.Text.from_markup(_v)
            # if not str then it is Text or Spinner
            self.states[_k] = _v

        # set some keys
        self.start_state_key = start_state_key
        self.finished_state_key = finished_state_key

        # call super __init__ while skipping the immediate parent
        # note that we will not need spinner property
        super(r_progress.SpinnerColumn, self).__init__(table_column=table_column)

    def render(self, task: r_progress.Task) -> r_console.RenderableType:
        # if state is provided in task then use it
        _state_key = task.fields.get("state", None)

        # if state was not provided in task guess it
        if _state_key is None:
            if task.finished:
                _state_key = self.finished_state_key
            else:
                try:
                    _state_key = task.current_state_key
                except AttributeError:
                    # this is firs time for task so set it to start
                    task.current_state_key = self.start_state_key
                    _state_key = task.current_state_key

        # else since state_key is provided by task make sure that
        # it is not finished_state_key ... needed to avoid any race conditions
        else:
            if _state_key == self.finished_state_key:
                raise Exception(
                    f"Please refrain from using `finished_state_key={_state_key}` as "
                    f"this will be automatically set when `task.finished`. "
                    f"This is done to avoid race conditions ..."
                )

        # backup
        task.current_state_key = _state_key  # backup

        # render
        try:
            _current_state = self.states[_state_key]
            if isinstance(_current_state, r_text.Text):
                return _current_state
            elif isinstance(_current_state, r_spinner.Spinner):
                return _current_state.render(task.get_time())
            else:
                raise Exception(f"Unknown type {type(_current_state)}")
        except KeyError:
            raise KeyError(f"Unknown state_key `{_state_key}`. "
                           f"Should be on of {self.states.keys()}")


@dataclasses.dataclass
class Progress:
    """
    Note that this is not ProgressBar nor Progress
    ... we use Progress as attribute
    ... aim is to get task from it so that we can update the columns in Progress
        that represent multiple tasks

    todo: build a asyncio api (with io overhead) or multithreading
      api (with compute overhead) while exploiting `rich.progress.Task` api
    """
    title: str
    columns: t.Dict[str, r_progress.ProgressColumn]
    logger: CustomLogger

    def __post_init__(self):
        # ------------------------------------------------------------ 01
        # make rich progress
        self.rich_progress = r_progress.Progress(
            *list(self.columns.values()),
            # todo: this can use console with record=True so that the progress
            #  can be saved to html or text ... need to explore ...
            console=None,
        )
        # ------------------------------------------------------------ 02
        # make rich table
        self.rich_panel = r_panel.Panel.fit(
            self.rich_progress, title=self.title,
            border_style="green", padding=(2, 2)
        )
        # ------------------------------------------------------------ 03
        # todo: find a way add to r_console.Console so that record=True can be used
        #   may be not possible
        # ------------------------------------------------------------ 04
        # empty container for added tasks
        self.tasks = {}  # type: t.Dict[str, r_progress.Task]

    def add_task(
        self, task_name: str, total: int, color: str = "cyan"
    ) -> r_progress.TaskID:
        _tid = self.rich_progress.add_task(
            description=f"[{color}]{task_name}", total=total,
        )
        for _rt in self.rich_progress.tasks:
            if _rt.id == _tid:
                self.tasks[task_name] = _rt
                break
        return _tid

    def go_live(self, refresh_per_second: int = 10) -> r_live.Live:
        self.logger.info(self.title)
        return r_live.Live(self.rich_panel, refresh_per_second=refresh_per_second)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    @classmethod
    def for_download(cls, title: str, logger: CustomLogger) -> "Progress":
        _progress = Progress(
            title=title,
            columns={
                "file_key": r_progress.TextColumn(
                    "[progress.description]{task.description}"),
                "progress": r_progress.BarColumn(),
                "percentage": r_progress.TextColumn(
                    "[progress.percentage]{task.percentage:>3.0f}%"),
                # todo: combine hash checking here ...
                #  especially better if we are building hash as we progress download
                # "hash_progress": progress.BarColumn(),
                # "hash_percentage": progress.TextColumn(
                #     "[progress.percentage]{task.percentage:>3.0f}%"),
                "download": r_progress.DownloadColumn(),
                "time_remaining": r_progress.TimeRemainingColumn(),
                "status": SpinnerColumn(
                    states={
                        "start": "dots",
                        "finished": EMOJI["white_heavy_check_mark"],
                        "failed": EMOJI["cross_mark"],
                    }
                ),
            },
            logger=logger,
        )

        return _progress


@dataclasses.dataclass
class Status:
    """
    A simple status indicator
    todo: explore adding time elapsed
    todo: explore clubbing multiple Status in one panel
    todo: more complex Status panel

    Refer __main__ of
    >>> r_status.Status

    + prints title with toolcraft.logger
    + then show simple spinner
    + can also log with time stamp (but not sent to logger module)
    """
    title: r_console.RenderableType
    logger: CustomLogger
    spinner: SpinnerType = SpinnerType.dots

    def __post_init__(self):
        self.console = r_console.Console()
        # noinspection PyTypeChecker
        self.status = None  # type: r_status.Status

    def __enter__(self):
        self.logger.info(self.title)
        self.status = self.console.status(
            status=f"[magenta]{self.title}",
            spinner=str(self.spinner),
        )
        self.status.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.status.__exit__(exc_type, exc_val, exc_tb)
        self.status = None

    def log(self, msg: str, log_to_logger: bool = False):
        self.console.log(msg)
        if log_to_logger:
            self.logger.info(msg)

    def update(
        self,
        status: r_console.RenderableType = None,
        spinner: SpinnerType = None,
        spinner_style: r_style.StyleType = None,
        speed: float = None,
    ):
        if self.status is None:
            e.code.CodingError(
                msgs=["Allowed to be called from within with context"]
            )
        self.status.update(
            status=status, spinner=str(spinner),
            spinner_style=spinner_style, speed=speed
        )

