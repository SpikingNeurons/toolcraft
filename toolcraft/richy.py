"""
Refer:
https://github.com/Textualize/rich/blob/master/examples/dynamic_progress.py
https://github.com/Textualize/rich/blob/master/examples/live_progress.py

todo: add terminal plotting support
  + https://stackoverflow.com/questions/37288421/how-to-plot-a-chart-in-the-terminal
  + either use plotext (adds extra dependency)
  + or use dearpygui frame grabber ... to reuse `toolcraft.gui` module
    this is possible as terminals can display raster images
    Extend StatusPanel for this
"""

from collections.abc import Sized
import dataclasses
import typing as t
import enum
import datetime
import abc
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
from rich import box as r_box
from rich import prompt as r_prompt

from . import logger
from . import util
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

    def get_spinner(
        self,
        text: r_console.RenderableType = "",
        style: t.Optional[r_style.StyleType] = None,
        speed: float = 1.0,
    ) -> r_spinner.Spinner:
        return r_spinner.Spinner(
            name=self.name,
            text=text, style=style, speed=speed,
        )


class SpinnerColumn(r_progress.SpinnerColumn):
    """
    An extended SpinnerColumn which can have many states and spinners
    """

    # noinspection PyMissingConstructor
    def __init__(
        self,
        states: t.Dict[str, t.Union[str, r_text.Text, r_spinner.Spinner, SpinnerType]],
        start_state_key: str = "start",
        finished_state_key: str = "finished",
        table_column: t.Optional[r_table.Column] = None,
    ):
        # transform states to respective rich elements
        self.states = {}
        for _k, _v in states.items():
            if isinstance(_v, SpinnerType):
                _v = _v.get_spinner()
            elif isinstance(_v, str):
                _v = r_text.Text.from_markup(_v)

            # if not str then it is Text or Spinner so directly assign
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
class Widget(abc.ABC):
    refresh_per_second: int = 10
    console: t.Optional[r_console.Console] = None

    def __post_init__(self):
        self._live = r_live.Live(
            self.renderable,
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            transient=True,
        )

    @property
    @abc.abstractmethod
    def renderable(self) -> r_console.RenderableType:
        ...

    def refresh(self, update_renderable: bool = False):
        """

        Args:
            update_renderable: In case you have updates any renderable
              components on the fly

        Returns:

        """
        if self._live is not None:
            if update_renderable:
                self._live.update(
                    renderable=self.renderable, refresh=True
                )
            else:
                self._live.refresh()

    def __enter__(self) -> "Widget":
        _console = self.console
        if _console is None:
            _console = r_console.Console(record=True)
        self._live = r_live.Live(
            self.renderable, refresh_per_second=self.refresh_per_second,
            console=_console
        )
        self._live.start(refresh=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._live.stop()
        self._live = None


@dataclasses.dataclass
class Status(Widget):
    """
    Refer:
    >>> r_status.Status
    >>> r_spinner.Spinner
    """
    title: t.Optional[r_console.RenderableType] = None
    status: r_console.RenderableType = ""
    spinner: SpinnerType = SpinnerType.star
    # spinner_style: Optional[StyleType] = None
    spinner_speed: float = 1.0
    box_type: r_box.Box = r_box.ASCII

    @property
    def renderable(self) -> r_console.RenderableType:
        if self.title is None:
            return self._spinner
        else:
            return r_panel.Panel(
                self._spinner, title=self.title,
                border_style="green",
                # padding=(2, 2),
                expand=True,
                box=self.box_type,
            )

    def __post_init__(self):
        self._spinner = self.spinner.get_spinner(
            text=self.status, speed=self.spinner_speed
        )
        # noinspection PyTypeChecker
        self._time = None  # type: datetime.datetime
        super().__post_init__()

    def __enter__(self) -> "Status":
        super().__enter__()
        self._live.start()
        self._spinner = SpinnerType.dots.get_spinner(text="Started ...")
        self._time = datetime.datetime.now()
        self.refresh(update_renderable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _elapsed_secs = (datetime.datetime.now() - self._time).total_seconds()
        self._spinner = r_text.Text.from_markup(
            f"{EMOJI['white_heavy_check_mark']} "
            f"Finished in {_elapsed_secs} seconds ...")
        self.refresh(update_renderable=True)
        self._live.stop()
        super().__exit__(exc_type, exc_val, exc_tb)

    def update(
        self,
        status: t.Optional[r_console.RenderableType] = None,
        spinner: SpinnerType = None,
        # spinner_style: Optional[StyleType] = None
        spinner_speed: t.Optional[float] = None,
    ):
        if status is not None:
            self.status = status
        if spinner_speed is not None:
            self.spinner_speed = spinner_speed

        if spinner is None:
            self._spinner.update(
                text=status, speed=spinner_speed
            )
        else:
            # todo: When used with StatusPanel
            #   figure this out currently only text update is happening
            #   dont know how spinner can be changed with our API ....
            #   Works with `python -m rich.status` example ...
            #   Note that console which is not widget might be key to solve this
            # noinspection PyAttributeOutsideInit
            self._spinner = spinner.get_spinner(text=status, speed=spinner_speed)
            self.refresh(update_renderable=True)


@dataclasses.dataclass
class Progress(Widget):
    """
    Note that this is not ProgressBar nor Progress
    ... we use Progress as attribute
    ... aim is to get task from it so that we can update the columns in Progress
        that represent multiple tasks

    todo: build a asyncio api (with io overhead) or multithreading
      api (with compute overhead) while exploiting `rich.progress.Task` api
    """
    columns: t.Dict[str, r_progress.ProgressColumn] = None
    title: t.Optional[r_console.RenderableType] = None

    @property
    def renderable(self) -> r_console.RenderableType:
        if self.title is None:
            return self._progress
        else:
            return r_panel.Panel(
                self._progress, title=self.title,
                border_style="green",
                # padding=(2, 2),
                expand=True,
                box=r_box.ASCII,
            )

    def __post_init__(self):
        # ------------------------------------------------------------ 01
        # make rich progress
        if self.columns is None:
            raise e.validation.NotAllowed(
                msgs=["Please supply mandatory columns field"]
            )
        self._progress = r_progress.Progress(
            *list(self.columns.values()),
            console=self.console,
            expand=True,
        )

        # ------------------------------------------------------------ 02
        # todo: find a way add to r_console.Console so that record=True can be used
        #   may be not possible ...
        #   NOTE: record=True can save html .. or dump to text logs

        # ------------------------------------------------------------ 03
        # empty container for added tasks
        self.tasks = {}  # type: t.Dict[str, r_progress.Task]

        # ------------------------------------------------------------ 04
        super().__post_init__()

    def add_task(
        self, task_name: str, total: float, description: str = None
    ) -> r_progress.TaskID:
        _tid = self._progress.add_task(
            description=description or task_name, total=total,
        )
        for _rt in self._progress.tasks:
            if _rt.id == _tid:
                self.tasks[task_name] = _rt
                break
        return _tid

    def update(
        self, task_name: str = None,
        advance: float = None, state: str = None,
        total: float = None, description: str = None
    ):
        if task_name is None:
            if len(self.tasks) == 1:
                task_name = list(self.tasks.keys())[0]
            else:
                raise e.code.NotAllowed(
                    msgs=["You must supply task_name kwarg when number of "
                          "tasks is not one"]
                )
        self._progress.update(
            task_id=self.tasks[task_name].id,
            advance=advance, state=state, total=total,
            description=description,
        )

    def track(
        self,
        sequence: t.Union[
            t.Sequence[r_progress.ProgressType],
            t.Iterable[r_progress.ProgressType]
        ],
        task_name: str,
        total: t.Optional[float] = None,
        description: str = None,
        update_period: float = 0.1,
    ) -> t.Iterable[r_progress.ProgressType]:
        """
        This can be better shortcut for add_task ...
        Specifically to be used directly on iterables ...
        Can add_task and also track it

        total: supply it when length of sequence cannot be guessed
               useful for infinite generators

        task_name:
          use # at end of task_task_name to support auto counter and hence
          reuse of task_name

        Refer:
        >>> r_progress.Progress.track
        >>> r_progress.track
        """
        # ------------------------------------------------------------ 01
        # estimate length
        if total is None:
            if isinstance(sequence, Sized):
                task_total = float(len(sequence))
            else:
                raise ValueError(
                    f"unable to get size of {sequence!r}, please specify 'total'"
                )
        else:
            task_total = total

        # ------------------------------------------------------------ 02
        # process task_name
        if task_name in self.tasks.keys():
            raise e.validation.NotAllowed(
                msgs=[
                    f"There already exists a task named {task_name}"
                ]
            )
        # if # in task name then add counter
        # note adding # will make task name reusable by adding counter
        _ = task_name.split("#")
        if len(_) == 2:
            task_name += str(len([k for k in self.tasks.keys() if k.startswith(_[0])]))

        # ------------------------------------------------------------ 03
        # add task
        self.add_task(task_name=task_name, total=task_total, description=description)

        # ------------------------------------------------------------ 04
        # yield and hence auto track
        # todo: explore --- self.rich_progress.live.auto_refresh
        task_id = self.tasks[task_name].id
        if self._progress.live.auto_refresh:
            # noinspection PyProtectedMember
            with r_progress._TrackThread(
                    self._progress, task_id, update_period) as track_thread:
                for value in sequence:
                    yield value
                    track_thread.completed += 1
        else:
            advance = self._progress.advance
            refresh = self._progress.refresh
            for value in sequence:
                yield value
                advance(task_id, 1)
                refresh()

    @staticmethod
    def simple_progress(
        title: t.Optional[str] = None,
        refresh_per_second: int = 10,
        console: t.Optional[r_console.Console] = None,
    ) -> "Progress":
        return Progress(
            title=title,  # setting this to str will add panel
            columns={
                "text": r_progress.TextColumn(
                    "[progress.description]{task.description}"),
                "progress": r_progress.BarColumn(),
                "percentage": r_progress.TextColumn(
                    "[progress.percentage]{task.percentage:>3.0f}%"),
                "time_elapsed": r_progress.TimeElapsedColumn(),
                "time_remaining": r_progress.TimeRemainingColumn(),
                "status": SpinnerColumn(
                    start_state_key="start",
                    finished_state_key="finished",
                    states={
                        "start": SpinnerType.dots,
                        "finished": EMOJI["white_heavy_check_mark"],
                    }
                ),
            },
            console=console,
            refresh_per_second=refresh_per_second,
        )

    @classmethod
    def simple_track(
        cls,
        sequence: t.Union[
            t.Sequence[r_progress.ProgressType],
            t.Iterable[r_progress.ProgressType]
        ],
        description: str = "Working...",
        total: float = None,
    ) -> t.Iterable[r_progress.ProgressType]:
        """
        Simple progress bar for single task which iterates over sequence

        """
        with cls.simple_progress(title="") as _progress:
            yield from _progress.track(
                sequence=sequence, task_name="single_task",
                description=description, total=total,
            )

    @classmethod
    def for_download_and_hashcheck(cls, title: str) -> "Progress":
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
                "time_elapsed": r_progress.TimeElapsedColumn(),
                "status": SpinnerColumn(
                    start_state_key="start",
                    finished_state_key="finished",
                    states={
                        "start": SpinnerType.dots,
                        "finished": EMOJI["white_heavy_check_mark"],
                        "already_finished": EMOJI["heavy_check_mark"],
                        "failed": EMOJI["cross_mark"],
                    }
                ),
            },
        )

        return _progress


@dataclasses.dataclass
class StatusPanel(Widget, abc.ABC):
    """
    A simple status indicator ... which we want make like panel
    todo: see
      + toolcraft/examples/richy/dynamic_progress.py
      + toolcraft/examples/richy/live_progress.py

    todo: explore adding time elapsed or add progress bar
      + see toolcraft/examples/richy/live_progress.py

    todo: explore clubbing multiple Status in one panel ... so that status spinner and
      it's log's stays in panel ...

    todo: add more compability for `util.HookUp` when used
      with `HashableCLass.hook_up_methods`

    todo: more complex Status panel

    + prints title with toolcraft.logger
    + then show simple spinner
    + can also log with time stamp (but not sent to logger module)
    """
    title: t.Optional[r_console.RenderableType] = None
    tc_log: logger.CustomLogger = None

    def __enter__(self) -> "StatusPanel":
        if self.tc_log is not None:
            self.tc_log.info(msg=self.title + " started ...")
            self._start_time = datetime.datetime.now()
        # noinspection PyTypeChecker
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        if self.tc_log is not None:
            _secs = (datetime.datetime.now() - self._start_time).total_seconds()
            self.tc_log.info(msg=self.title + f" finished in {_secs} seconds ...")


@dataclasses.dataclass
class ProgressStatusPanel(StatusPanel):
    """
    We have table with one row for Progress and second for Status

    todo: Add one more row that dumps logs using Text so that it stays inside Panel
      This will help us have some information while Panel is still live
      May de have method `self.log(...)` for this SimpleStatusPanel
    """

    @property
    @util.CacheResult
    def progress(self) -> Progress:
        return Progress.simple_progress(
            title=None, console=self.console,
            refresh_per_second=self.refresh_per_second)

    @property
    @util.CacheResult
    def status(self) -> Status:
        return Status(
            title=None,
            console=self.console, refresh_per_second=self.refresh_per_second
        )

    @property
    def renderable(self) -> r_console.RenderableType:
        _progress = self.progress.renderable
        _status = r_panel.Panel(self.status.renderable, box=r_box.HORIZONTALS)
        _group = r_console.Group(
            _progress, _status
        )
        if self.title is None:
            return _group
        else:
            return r_panel.Panel(
                _group,
                title=self.title,
                border_style="green",
                # padding=(2, 2),
                expand=True,
                box=r_box.ASCII,
            )
