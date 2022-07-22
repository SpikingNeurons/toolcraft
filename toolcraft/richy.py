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
from rich import markdown as r_markdown
from rich import prompt as r_prompt

from . import logger
from . import util
from . import error as e

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from . import marshalling as m


# noinspection PyArgumentList
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
        start_state: t.Union[str, r_text.Text, r_spinner.Spinner, SpinnerType] = SpinnerType.dots,
        finished_state: t.Union[str, r_text.Text] = EMOJI["white_heavy_check_mark"],
        table_column: t.Optional[r_table.Column] = None,
    ):
        # set states
        self.start_state = \
            start_state.get_spinner() \
            if isinstance(start_state, SpinnerType) \
            else start_state  # type: t.Union[str, r_text.Text, r_spinner.Spinner]
        self.finished_state = finished_state

        # call super __init__ while skipping the immediate parent
        # note that we will not need spinner property
        super(r_progress.SpinnerColumn, self).__init__(table_column=table_column)

    def render(self, task: r_progress.Task) -> r_console.RenderableType:
        # if task finished return
        if task.finished:
            return self.finished_state

        # if state is provided in task then use it
        _spinner_state = task.fields.get("spinner_state", None)

        # if state was not provided then infer from start state
        if _spinner_state is None:
            _spinner_state = self.start_state

        # now return thing to render
        return _spinner_state.render(task.get_time()) \
            if isinstance(_spinner_state, r_spinner.Spinner) else _spinner_state


@dataclasses.dataclass
class Widget(abc.ABC):
    title: t.Optional[r_console.RenderableType] = None
    tc_log: logger.CustomLogger = None
    refresh_per_second: int = 10
    console: r_console.Console = None

    @property
    @abc.abstractmethod
    def renderable(self) -> r_console.RenderableType:
        ...

    def __post_init__(self):
        if self.console is None:
            self.console = r_console.Console(record=True)
        self._live = r_live.Live(
            self.renderable,
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            transient=True,
        )

    def __enter__(self) -> "Widget":

        self._start_time = datetime.datetime.now()

        if self.tc_log is not None:
            _title = (self.title + ' ') if bool(self.title) else ''
            self.tc_log.info(msg=_title + "started ...")

        self._live = r_live.Live(
            self.renderable, refresh_per_second=self.refresh_per_second,
            console=self.console
        )

        self._live.start(refresh=False)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._live.stop()

        self.console.print("")

        if self.tc_log is not None:
            # todo: use `self.console.extract_*` methods to get console frame and log it
            #   via self.tc_log .... need to do this because the RichHandler is not able
            #   to write things to file like FileHandler ... explore later
            _secs = (datetime.datetime.now() - self._start_time).total_seconds()
            _title = (self.title + ' ') if bool(self.title) else ''
            _ct = self.console.export_text()
            self.tc_log.info(
                msg=_title + f"finished in {_secs} seconds ..."
                # + _ct
            )

    def log(
        self,
        *objects: t.Any,
        sep: str = " ",
        end: str = "\n",
        style: t.Optional[t.Union[str, r_style.Style]] = None,
        justify: t.Optional[r_console.JustifyMethod] = None,
        emoji: t.Optional[bool] = None,
        markup: t.Optional[bool] = None,
        highlight: t.Optional[bool] = None,
        log_locals: bool = False,
        _stack_offset: int = 1,
    ):
        """
        todo: improve this to use toolcraft.logger so that terminal based
          richy loging plays well with file logging of toolcraft
        Args:
            *objects:
            sep:
            end:
            style:
            justify:
            emoji:
            markup:
            highlight:
            log_locals:
            _stack_offset:

        Returns:

        """
        self.console.log(
            *objects, sep=sep, end=end, style=style,
            justify=justify, emoji=emoji, markup=markup,
            highlight=highlight, log_locals=log_locals,
            _stack_offset=_stack_offset,
        )

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
    overall_progress_iterable: t.Union[
        t.Sequence[r_progress.ProgressType],
        t.Iterable[r_progress.ProgressType]
    ] = None

    @property
    def renderable(self) -> r_console.RenderableType:
        # grp container
        _grp = []

        # overall progress
        if self.overall_progress_iterable is not None:
            _grp.append(self._overall_progress.renderable)

        # get spinner
        _grp.append(self._spinner)

        # if message there
        if self._final_message is not None:
            _grp.append(self._final_message)

        # make actual group
        _grp = r_console.Group(*_grp)

        # add title
        if self.title is None:
            return _grp
        else:
            return r_panel.Panel(
                _grp, title=self.title,
                border_style="green",
                # padding=(2, 2),
                expand=True,
                box=self.box_type,
            )

    def __post_init__(self):
        # make spinner
        self._spinner = self.spinner.get_spinner(
            text=self.status, speed=self.spinner_speed
        )

        # make message
        self._final_message = None

        # make overall progress
        if self.overall_progress_iterable is not None:
            self._overall_progress = Progress(
                tc_log=self.tc_log,
                columns={
                    "text": r_progress.TextColumn(
                        "[progress.description]{task.description}"),
                    "progress": r_progress.BarColumn(),
                    "percentage": r_progress.TextColumn(
                        "[progress.percentage]{task.percentage:>3.0f}%"),
                    "time_elapsed": r_progress.TimeElapsedColumn(),
                    "time_remaining": r_progress.TimeRemainingColumn(),
                    "status": SpinnerColumn(
                        start_state=SpinnerType.dots,
                        finished_state=EMOJI["white_heavy_check_mark"],
                    ),
                },
                console=self.console,
                refresh_per_second=self.refresh_per_second,
            )

        # call super
        super().__post_init__()

    def __enter__(self) -> "Status":
        super().__enter__()
        self._spinner = SpinnerType.dots.get_spinner(text="Started ...")
        self.refresh(update_renderable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _elapsed_secs = (datetime.datetime.now() - self._start_time).total_seconds()
        self._spinner = r_text.Text.from_markup(
            f"{EMOJI['white_heavy_check_mark']} "
            f"Finished in {_elapsed_secs} seconds ...")
        self.refresh(update_renderable=True)
        super().__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self) -> t.Generator[r_progress.ProgressType, None, None]:
        if self.overall_progress_iterable is not None:
            return self._overall_progress.track(
                self.overall_progress_iterable, task_name="overall progress",
                update_period=1./self.refresh_per_second,
            )
        else:
            raise e.code.CodingError(
                msgs=[
                    f"To iterate please set field `overall_progress_iterable`"
                ]
            )

    def set_final_message(self, msg: str):
        # noinspection PyAttributeOutsideInit
        self._final_message = r_markdown.Markdown("\n---\n" + msg)
        self.refresh(update_renderable=True)
        if self.tc_log is not None:
            self.tc_log.info(msg=msg)

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
class ProgressTask:
    rich_progress: r_progress.Progress
    rich_task: r_progress.Task
    total: float

    def __post_init__(self):
        self._failed = False
        self._already_finished = False

    def update(
        self,
        advance: float = None,
        total: float = None, description: str = None, **fields,
    ):
        """
        When you pass special `**fields`
        + `spinner_state` it will be consumed by ProgressColumn
        >>> SpinnerColumn
        """
        if self._failed:
            raise e.code.CodingError(
                msgs=["Cannot update anything as the task has failed ..."]
            )
        if self._already_finished:
            raise e.code.CodingError(
                msgs=["The task is already finished ... so there should be no call for update ..."]
            )
        self.rich_progress.update(
            task_id=self.rich_task.id,
            advance=advance, total=total,
            description=description, **fields,
        )

    def failed(self):
        # update
        self.update(spinner_state=EMOJI["cross_mark"])
        # set as failed so that update is unusable ...
        # noinspection PyAttributeOutsideInit
        self._failed = True

    def already_finished(self):
        # update ... note we set full length so that any progress bar is fully filled
        self.update(
            advance=self.total,
            spinner_state=EMOJI["heavy_check_mark"],
        )
        # set as already_finished so that update is unusable ...
        # noinspection PyAttributeOutsideInit
        self._already_finished = True


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
        # empty container for added tasks
        self.tasks = {}  # type: t.Dict[str, ProgressTask]

        # ------------------------------------------------------------ 03
        super().__post_init__()

    def add_task(
        self, task_name: str, total: float, description: str = None, **fields
    ) -> ProgressTask:
        # process task_name
        if task_name in self.tasks.keys():
            raise e.validation.NotAllowed(
                msgs=[
                    f"There already exists a task named {task_name!r}",
                    "Try giving new task name while iterating or else add '#' token at end to make name reusable.",
                ]
            )
        # if # at end task name then add counter
        # note adding # will make task name reusable by adding counter
        if task_name.endswith("#"):
            task_name += str(len([k for k in self.tasks.keys() if k.startswith(task_name)]))

        # test if fields are defined in columns for progress bar
        for _k in fields.keys():
            e.validation.ShouldBeOneOf(
                value=_k, values=list(self.columns.keys()),
                msgs=[f"You have not specified how to render extra field {_k} in `Progress.columns`"]
            ).raise_if_failed()

        # add task
        _tid = self._progress.add_task(
            description=description or task_name, total=total, **fields,
        )
        for _rt in self._progress.tasks:
            if _rt.id == _tid:
                self.tasks[task_name] = ProgressTask(rich_progress=self._progress, rich_task=_rt, total=total)
                break

        # return
        return self.tasks[task_name]

    def update(
        self,
        task_name: str = None,
        advance: float = None,
        total: float = None, description: str = None, **fields,
    ):
        """
        This is just for convenience.
        It will just look for last added task and update it.
        """
        if bool(self.tasks):
            if task_name is None:
                task_name = next(reversed(self.tasks.keys()))
            else:
                if task_name not in self.tasks.keys():
                    raise e.code.CodingError(
                        msgs=[f"There is no task with name {task_name} available ..."]
                    )
            self.tasks[task_name].update(
                advance=advance, total=total, description=description, **fields
            )
        else:
            raise e.code.CodingError(
                msgs=[
                    f"There are no tasks added yet ... so nothing to update"
                ]
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
        **fields,
    ) -> t.Generator[r_progress.ProgressType, None, None]:
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
        # add task
        _task = self.add_task(
            task_name=task_name, total=task_total,
            description=description, **fields)

        # ------------------------------------------------------------ 03
        # yield and hence auto track
        # todo: explore --- self.rich_progress.live.auto_refresh
        task_id = _task.rich_task.id
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
        console: r_console.Console = r_console.Console(record=True),
        tc_log: logger.CustomLogger = None,
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
                "status": SpinnerColumn(),
            },
            console=console,
            refresh_per_second=refresh_per_second,
            tc_log=tc_log,
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
        tc_log: logger.CustomLogger = None,
    ) -> t.Generator[r_progress.ProgressType, None, None]:
        """
        Simple progress bar for single task which iterates over sequence

        """
        with cls.simple_progress(title="", tc_log=tc_log) as _progress:
            yield from _progress.track(
                sequence=sequence, task_name="single_task",
                description=description, total=total,
            )

    @classmethod
    def for_download_and_hashcheck(
        cls, title: str,
        tc_log: logger.CustomLogger = None,
    ) -> "Progress":
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
                "status": SpinnerColumn(),
            },
            tc_log=tc_log,
        )

        return _progress


@dataclasses.dataclass
class ProgressStatusPanel(Widget):
    """

    todo: Add one more row that dumps logs using Text so that it stays inside Panel
      This will help us have some information while Panel is still live
      May de have method `self.log(...)` for this SimpleStatusPanel
    """

    stages: t.Optional[t.List[str]] = None

    @property
    def renderable(self) -> r_console.RenderableType:
        _progress = self._progress.renderable
        _status = r_panel.Panel(self._status.renderable, box=r_box.HORIZONTALS)
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

    def __post_init__(self):
        self.current_stage = None
        self._progress = self._make_richy_progress()
        self._status = Status(
            tc_log=self.tc_log,
            title=None,
            console=self.console, refresh_per_second=self.refresh_per_second,
            overall_progress_iterable=self.stages,
        )
        super().__post_init__()

    def __enter__(self) -> "ProgressStatusPanel":
        super().__enter__()
        self._status._spinner = SpinnerType.dots.get_spinner(text="Started ...")
        self.refresh(update_renderable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _elapsed_secs = (datetime.datetime.now() - self._start_time).total_seconds()
        self._status._spinner = r_text.Text.from_markup(
            f"{EMOJI['white_heavy_check_mark']} "
            f"Finished in {_elapsed_secs} seconds ...")
        self.refresh(update_renderable=True)
        super().__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        if self.stages is None:
            raise e.code.CodingError(
                msgs=["Could not iterate over this panel as stages are not provided ..."]
            )
        with self:
            for _stage in self._status:
                self.update(status=f"Executing stage {_stage!r} ...")
                self.current_stage = _stage
                yield _stage

    def _make_richy_progress(self) -> Progress:
        return Progress(
            columns={
                "text": r_progress.TextColumn(
                    "[progress.description]{task.description}"),
                "progress": r_progress.BarColumn(),
                "percentage": r_progress.TextColumn(
                    "[progress.percentage]{task.percentage:>3.0f}%"),
                # "time_remaining": r_progress.TimeRemainingColumn(),
                # "acc": r_progress.TextColumn("[green]{task.fields[acc]:.4f}"),
                # "loss": r_progress.TextColumn("[yellow]{task.fields[loss]:.4f}"),
                "msg": r_progress.TextColumn("{task.fields[msg]}"),
                "status": SpinnerColumn(),
            },
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            tc_log=self.tc_log,
            title=None,
        )

    def update(
        self,
        status: t.Optional[r_console.RenderableType] = None,
        spinner: SpinnerType = None,
        # spinner_style: Optional[StyleType] = None
        spinner_speed: t.Optional[float] = None,
    ):
        self._status.update(status=status, spinner=spinner, spinner_speed=spinner_speed)

    def add_task(
        self, task_name: str, total: float, msg: str,
        prefix_current_stage: bool = True,
    ) -> ProgressTask:
        if prefix_current_stage:
            if self.current_stage is None:
                raise e.code.CodingError(
                    msgs=["You are not using `stages` field or you are not iterating on `ProgressStatusPanel`",
                          "Please iterate over this instance to loop on stages ..."]
                )
            task_name = f"{self.current_stage}:{task_name}"
        return self._progress.add_task(
            task_name=task_name, total=float(total), msg=msg,
        )

    def track(self):
        ...

    def set_final_message(self, msg: str):
        self._status.set_final_message(msg=msg)


@dataclasses.dataclass
class FitProgressStatusPanel(Widget):

    epochs: int = None

    @property
    def renderable(self) -> r_console.RenderableType:
        _train_progress = self._train_progress.renderable
        _validate_progress = self._validate_progress.renderable
        _status_renderable = self._status.renderable
        _table = r_table.Table.grid(expand=True)
        _table.add_row(
            r_panel.Panel(
                _train_progress,
                title="Train", box=r_box.HORIZONTALS, expand=True),
            r_panel.Panel(
                _validate_progress,
                title="Validate", box=r_box.HORIZONTALS, expand=True),
        )
        _status = r_panel.Panel(self._status.renderable, box=r_box.HORIZONTALS)
        _group = r_console.Group(
            _table, _status
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

    def __post_init__(self):
        if self.epochs is None:
            raise e.validation.NotAllowed(msgs=["Please specify epochs ... it is mandatory"])
        self._train_progress = self._make_richy_progress()
        self._validate_progress = self._make_richy_progress()
        self._status = Status(
            tc_log=self.tc_log,
            title=None,
            console=self.console, refresh_per_second=self.refresh_per_second,
            overall_progress_iterable=range(1, self.epochs + 1),
        )
        super().__post_init__()

    def __enter__(self) -> "FitProgressStatusPanel":
        super().__enter__()
        self._status._spinner = SpinnerType.dots.get_spinner(text="Started ...")
        self.refresh(update_renderable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _elapsed_secs = (datetime.datetime.now() - self._start_time).total_seconds()
        self._status._spinner = r_text.Text.from_markup(
            f"{EMOJI['white_heavy_check_mark']} "
            f"Finished in {_elapsed_secs} seconds ...")
        self.refresh(update_renderable=True)
        super().__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        with self:
            for _epoch in self._status:
                self.update(status=f"Fitting epoch {_epoch} ...")
                self._task_name = f"ep {_epoch:03d}"
                yield _epoch

    def _make_richy_progress(self) -> Progress:
        return Progress(
            columns={
                "text": r_progress.TextColumn(
                    "[progress.description]{task.description}"),
                "progress": r_progress.BarColumn(),
                "percentage": r_progress.TextColumn(
                    "[progress.percentage]{task.percentage:>3.0f}%"),
                # "time_remaining": r_progress.TimeRemainingColumn(),
                # "acc": r_progress.TextColumn("[green]{task.fields[acc]:.4f}"),
                # "loss": r_progress.TextColumn("[yellow]{task.fields[loss]:.4f}"),
                "msg": r_progress.TextColumn("{task.fields[msg]}"),
                "status": SpinnerColumn(),
            },
            console=self.console,
            refresh_per_second=self.refresh_per_second,
            tc_log=self.tc_log,
            title=None,
        )

    def update(
        self,
        status: t.Optional[r_console.RenderableType] = None,
        spinner: SpinnerType = None,
        # spinner_style: Optional[StyleType] = None
        spinner_speed: t.Optional[float] = None,
    ):
        self._status.update(status=status, spinner=spinner, spinner_speed=spinner_speed)

    def add_train_task(
        self, total: float, msg: str,
    ) -> ProgressTask:
        return self._train_progress.add_task(
            task_name=self._task_name, total=float(total), msg=msg,
        )

    def add_validate_task(
        self, total: float, msg: str,
    ) -> ProgressTask:
        return self._validate_progress.add_task(
            task_name=self._task_name, total=float(total), msg=msg,
        )

    def set_final_message(self, msg: str):
        self._status.set_final_message(msg=msg)

