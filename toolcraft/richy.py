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
import time
from collections.abc import Sized
import dataclasses
import typing as t
import enum
import datetime
import abc

import rich.jupyter
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
from rich import layout as r_layout
from rich import progress as r_progress
from rich import status as r_status
from rich import panel as r_panel
from rich import box as r_box
from rich import markdown as r_markdown
from rich import prompt as r_prompt
_now = datetime.datetime.now

from . import logger
from . import util
from . import error as e
from . import marshalling as m

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from . import marshalling as m

T = t.TypeVar('T', bound="Widget")

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
@m.RuleChecker(
    things_not_to_be_cached=['get_renderable'],
    things_to_be_cached=['layout'],
)
class Widget(m.Checker, abc.ABC):

    title: t.Optional[r_console.RenderableType] = ""
    sub_title: t.Optional[
        t.Union[
            t.List[r_console.RenderableType], m.HashableClass,
        ]
    ] = None
    console: r_console.Console = dataclasses.field(default_factory=lambda: r_console.Console(record=True))
    tc_log: logger.CustomLogger = None
    border_style: r_style.StyleType = "green"
    box_type: r_box.Box = r_box.ASCII

    @property
    @abc.abstractmethod
    def layout(self) -> t.Union[t.Dict[str, t.Union["Widget", rich.jupyter.JupyterMixin]], r_layout.Layout]:
        """
        Returns t.Dict if simple widget and Layout if complex application
        """
        ...

    def __post_init__(self):
        # temp mandatory
        if self.tc_log is None:
            raise e.validation.NotAllowed(
                msgs=["For now we want to keep tc_log field mandatory ..."]
            )

        # modify sub_title
        _h = self.sub_title
        if isinstance(self.sub_title, m.HashableClass):
            self.sub_title = [
                f"{_h.__module__}.{_h.__class__.__name__}", f"{_h.group_by}", f"{_h.name}"
            ]

        # some vars
        # noinspection PyTypeChecker
        self._live = None  # type: r_live.Live
        self.is_in_with_context = False

    def __enter__(self: T) -> T:

        if self.tc_log is not None:
            self.tc_log.info(msg=f"[{self.title}] started ...", msgs=self.sub_title)

        self._live = r_live.Live(
            self.get_renderable(),
            console=self.console,
            refresh_per_second=4.,
        )

        self._live.start()

        self._start_time = _now()

        if self.is_in_with_context:
            raise e.code.CodingError(
                msgs=["We do not expect this to be set already ..."]
            )
        self.is_in_with_context = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.is_in_with_context = False

        _elapsed_seconds = (_now() - self._start_time).total_seconds()

        self.refresh(update_renderable=True)

        self._live.stop()

        # todo: remove this only needed for pycharm terminal as new line is not added when printing on console
        #    but works fine on terminal
        self.console.print("")

        if self.tc_log is not None:
            # todo: use `self.console.extract_*` methods to get console frame and log it
            #   via self.tc_log .... need to do this because the RichHandler is not able
            #   to write things to file like FileHandler ... explore later
            # _ct = self.console.export_text()
            self.tc_log.info(
                msg=f"[{self.title}] finished in {_elapsed_seconds} seconds ...", msgs=self.sub_title,
                # + _ct
            )

    @classmethod
    def class_init(cls):
        # as of nothing to do at class level ... like rule checking etc.
        ...

    def log(
        self,
        objects: t.List,
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
        self.console.log(
            *objects, sep=sep, end=end, style=style,
            justify=justify, emoji=emoji, markup=markup,
            highlight=highlight, log_locals=log_locals,
            _stack_offset=_stack_offset,
        )

        # todo: improve this to use self.tc_log so that terminal based
        #   richy loging plays well with file logging of toolcraft
        if self.tc_log is not None:
            self.tc_log.info(msg=f"[{self.title}] log ...", msgs=objects)

    def get_renderable(self) -> r_console.RenderableType:
        # ------------------------------------------------------------- 01
        # grp layout
        _layout = self.layout
        # return quickly when `r_layout.Layout`
        if isinstance(_layout, r_layout.Layout):
            # todo: still need to handle title and sub_title for rich.layout.Layout
            raise e.code.NotSupported(
                msgs=["still need to handle title and sub_title for rich.layout.Layout"]
            )
            # return _layout

        # ------------------------------------------------------------- 02
        # make container for renderables
        if self.sub_title is None:
            _grp = []
        else:
            # noinspection PyTypeChecker
            _grp = [
                r_text.Text(_, justify='center') for _ in self.sub_title
            ] + [r_markdown.Markdown("---")]
        for _k, _v in _layout.items():
            if _v is None:
                continue
            if isinstance(_v, Widget):
                _v = _v.get_renderable()
            _grp.append(_v)

        # ------------------------------------------------------------- 03
        # make actual group
        _grp = r_console.Group(*_grp)

        # ------------------------------------------------------------- 04
        # add title
        if self.title == "":
            return _grp
        else:
            return r_panel.Panel(
                _grp, title=self.title,
                border_style=self.border_style,
                # padding=(2, 2),
                expand=True,
                box=self.box_type,
            )

    def refresh(self, update_renderable: bool = False):
        """
        Args:
            update_renderable: In case you want to update any renderable components on the fly
        """
        if self._live is None:
            raise e.code.CodingError(
                msgs=["Did you miss to call from with context ..."]
            )
        if update_renderable:
            self._live.update(renderable=self.get_renderable(), refresh=True)
        else:
            self._live.refresh()


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
        completed: float = None,
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
            advance=advance, total=total, completed=completed,
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

    @property
    @util.CacheResult
    def layout(self) -> t.Dict:
        return {
            'progress': r_progress.Progress(
                *list(self.columns.values()),
                console=self.console,
                expand=True,
            )
        }

    def __post_init__(self):
        # ------------------------------------------------------------ 01
        # make rich progress
        if self.columns is None:
            raise e.validation.NotAllowed(
                msgs=["Please supply mandatory columns field"]
            )

        # ------------------------------------------------------------ 02
        # empty container for added tasks
        # noinspection PyTypeChecker
        self.tasks = dict()  # type: t.Dict[str, ProgressTask]

        # ------------------------------------------------------------ 03
        super().__post_init__()

    def add_task(
        self, task_name: str, total: t.Optional[float], description: str = None, **fields
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
        _p = self.layout['progress']
        _tid = _p.add_task(
            description=description or task_name, total=total, **fields,
        )
        for _rt in _p.tasks:
            if _rt.id == _tid:
                self.tasks[task_name] = ProgressTask(rich_progress=_p, rich_task=_rt, total=total)
                break

        # log
        if self.tc_log is not None:
            self.tc_log.info(msg=f"[{self.title}] add task {task_name!r}")

        # return
        return self.tasks[task_name]

    def update(
        self,
        task_name: str = None, advance: float = None,
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
        **fields,
    ) -> t.Generator[r_progress.ProgressType, None, None]:
        """
        This can be better shortcut for add_task ...
        Specifically to be used directly on iterables ...

        You can add_task and also track it ... but only benefit here is you
        need not write code to handle task instance ... also this one yields, so it can be fast

        Current task added by this method can eb accessed via self.current_task

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
        for value in sequence:
            yield value
            _task.update(advance=1)

        # ------------------------------------------------------------ xx
        # check r_progress.Progress.track
        # todo: explore --- self.rich_progress.live.auto_refresh
        # if _p.live.auto_refresh:
        #     # noinspection PyProtectedMember
        #     with r_progress._TrackThread(
        #             _p, task_id, update_period) as track_thread:
        #         for value in sequence:
        #             print("xxxxx", task_id, task_name, value)
        #             yield value
        #             track_thread.completed += 1
        # else:
        #     advance = _p.advance
        #     refresh = _p.refresh
        #     for value in sequence:
        #         print("xxxxx", task_id, task_name, value)
        #         yield value
        #         advance(task_id, 1)
        #         refresh()

    @staticmethod
    def simple_progress(
        console: t.Optional[r_console.Console],
        title: t.Optional[str] = "",
        tc_log: logger.CustomLogger = None,
        box_type: r_box.Box = r_box.ASCII,
        border_style: r_style.Style = "green",
        show_time_elapsed: bool = True,
        show_time_remaining: bool = False,
        use_msg_field: bool = False,
    ) -> "Progress":
        if console is None:
            console = r_console.Console(record=True)
        _cols = {
            "text": r_progress.TextColumn(
                "[progress.description]{task.description}"),
            "progress": r_progress.BarColumn(),
            "percentage": r_progress.TextColumn(
                "[progress.percentage]{task.percentage:>3.0f}%"),
        }
        if use_msg_field:
            _cols['msg'] = r_progress.TextColumn("{task.fields[msg]}")
        if show_time_elapsed:
            _cols['time_elapsed'] = r_progress.TimeElapsedColumn()
        if show_time_remaining:
            _cols['time_remaining'] = r_progress.TimeRemainingColumn()
        _cols['status'] = SpinnerColumn()
        return Progress(
            title=title,  # setting this to str will add panel
            columns=_cols,
            console=console,
            tc_log=tc_log,
            box_type=box_type,
            border_style=border_style,
        )

    @classmethod
    def simple_track(
        cls,
        sequence: t.Union[
            t.Sequence[r_progress.ProgressType],
            t.Iterable[r_progress.ProgressType]
        ],
        console: t.Optional[r_console.Console],
        title: t.Optional[str] = "",
        description: str = "Working...",
        total: float = None,
        tc_log: logger.CustomLogger = None,
        box_type: r_box.Box = r_box.ASCII,
        border_style: r_style.Style = "green",
        show_time_elapsed: bool = True,
        show_time_remaining: bool = False,
        use_msg_field: bool = False,
    ) -> t.Generator[r_progress.ProgressType, None, None]:
        """
        Simple progress bar for single task which iterates over sequence
        """
        if console is None:
            console = r_console.Console(record=True)
        with cls.simple_progress(
            title=title, tc_log=tc_log, box_type=box_type,
            console=console,
            border_style=border_style,
            show_time_elapsed=show_time_elapsed,
            show_time_remaining=show_time_remaining,
            use_msg_field=use_msg_field,
        ) as _progress:
            yield from _progress.track(
                sequence=sequence, task_name="single_task",
                description=description, total=total,
            )

    @classmethod
    def for_download_and_hashcheck(
        cls, title: str,
        tc_log: logger.CustomLogger,
        console: t.Optional[r_console.Console],
        box_type: r_box.Box = r_box.ASCII,
        border_style: r_style.Style = "green",
    ) -> "Progress":
        """
        todo: ass hashcheck progress panel ... currently only download shown .... similar to FitProgressPanel
        """
        if console is None:
            console = r_console.Console(record=True)
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
            box_type=box_type,
            border_style=border_style,
            console=console,
        )

        return _progress


@dataclasses.dataclass
@m.RuleChecker(
    things_to_be_cached=['generic_progress', 'summary', 'iter_next_start_callbacks', 'iter_next_end_callbacks']
)
class StatusPanel(Widget):
    """
    todo: we have now full support for s.FileGroup and s.Folder
      so add counters on status panel for that ... so that `on_enter` can call them and they will update
      via `self.richy_panel`
      We will have some thing like (FG-FileGroup, Fo-Folder, C-created, A-accessed, D-deleted)
      + FG C:02 A:67 D:04
      + Fo C:12 A:03 D:43
    """
    stages: t.Optional[
        t.Union[t.Sequence[t.Any], t.Iterable[t.Any]]
    ] = None

    @property
    @util.CacheResult
    def generic_progress(self) -> Progress:
        if 'generic_progress' not in self.layout.keys():
            self['generic_progress'] = Progress.simple_progress(
                title="tasks",
                console=self.console,
                box_type=r_box.HORIZONTALS,
                border_style=r_style.Style(color="cyan"),
                tc_log=self.tc_log,
                use_msg_field=True,
            )
        # noinspection PyTypeChecker
        return self['generic_progress']

    @property
    @util.CacheResult
    def summary(self) -> t.List[str]:
        return []

    @property
    @util.CacheResult
    def iter_next_start_callbacks(self) -> t.List[t.Callable]:
        return []

    @property
    @util.CacheResult
    def iter_next_end_callbacks(self) -> t.List[t.Callable]:
        return []

    @property
    @util.CacheResult
    def layout(self) -> t.Dict:
        """
        refer
        >>> from rich import layout
        Also check example `toolcraft/examples/layout.py`
        """
        _ret = dict()
        if self.stages is None:
            _ret['stages_progress'] = None
        else:
            _ret['stages_progress'] = self._make_stages_progress()
        _ret['spinner'] = SpinnerType.dots.get_spinner(text="Waiting ...")
        return _ret

    def __post_init__(self):
        # noinspection PyTypeChecker
        self.current_stage = None  # type: str
        super().__post_init__()

    def __setitem__(self, key: str, value: t.Union[rich.jupyter.JupyterMixin, Widget, r_console.Group]):
        """
        This will add renderable items except for reserved items
          (as they will be added by this class based on usage)
        Note that for now reserved items are at end ...
        """
        if isinstance(value, Widget):
            if self.console != value.console:
                raise e.code.CodingError(
                    msgs=["Please make sure that you share the console of the widget "
                          "you want to add to this StatusPanel"]
                )
        _reserved_keys = ['final_message', 'stages_progress', 'spinner']
        e.validation.ShouldNotBeOneOf(
            value=key, values=_reserved_keys,
            msgs=["Cannot add items with reserved names ..."]
        ).raise_if_failed()
        e.validation.ShouldNotBeOneOf(
            value=key, values=list(self.layout.keys()),
            msgs=["There already exists a item with that name"]
        ).raise_if_failed()
        _new_dict = dict()
        _reserved_dict = dict()
        for _k in self.layout.keys():
            if _k in _reserved_keys:
                _reserved_dict[_k] = self.layout[_k]
            else:
                _new_dict[_k] = self.layout[_k]
        _new_dict[key] = value
        self.layout.clear()
        self.layout.update(**_new_dict, **_reserved_dict)
        self.refresh(update_renderable=True)

    def __getitem__(self, item: str) -> t.Union[rich.jupyter.JupyterMixin, Widget, r_console.Group]:
        e.validation.ShouldBeOneOf(
            value=item, values=list(self.layout.keys()), msgs=["There is no item with that name"]
        ).raise_if_failed()
        return self.layout[item]

    def __delitem__(self, key: str):
        if key not in self.layout.keys():
            return
        del self.layout[key]
        self.refresh(update_renderable=True)

    def __enter__(self) -> "StatusPanel":
        if self.current_stage is not None:
            raise e.code.CodingError(
                msgs=["Looks like the previous with context did not exit properly",
                      f"We expect this to be None, but found {self.current_stage}"]
            )
        self.layout['spinner'] = SpinnerType.dots.get_spinner(text="Waiting ...")
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _elapsed_seconds = (_now() - self._start_time).total_seconds()
        # noinspection PyTypedDict
        self.layout['spinner'] = r_text.Text.from_markup(
                f"{EMOJI['white_heavy_check_mark']} "
                f"Finished in {_elapsed_seconds} seconds ...")
        self.current_stage = None
        super().__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        if self.stages is None:
            raise e.code.CodingError(
                msgs=["Could not iterate over this panel as stages are not provided ..."]
            )
        _len = len(self.stages)
        _str_len = len(str(_len))
        if self.is_in_with_context:
            _i = 0
            for _stage in self.layout['stages_progress'].track(
                sequence=self.stages, task_name="progress", msg="..."
            ):
                self.on_iter_next_start(current_stage=_stage)
                _i += 1
                yield _stage
                self.on_iter_next_end(current_stage=_stage)
        else:
            with self:
                _i = 0
                for _stage in self.layout['stages_progress'].track(
                    sequence=self.stages, task_name="progress", msg="..."
                ):
                    self.on_iter_next_start(current_stage=_stage)
                    _i += 1
                    yield _stage
                    self.on_iter_next_end(current_stage=_stage)

    def _make_stages_progress(self) -> Progress:
        return Progress.simple_progress(
            title="***",
            console=self.console,
            box_type=r_box.HORIZONTALS,
            border_style=r_style.Style(color="cyan"),
            tc_log=self.tc_log,
            show_time_elapsed=True,
            show_time_remaining=True,
            use_msg_field=True,
        )

    def on_iter_next_start(self, current_stage: t.Any):
        # noinspection PyAttributeOutsideInit
        self.current_stage = current_stage
        self.update(status=f"executing stage `{current_stage}` ...")
        for _fn in self.iter_next_start_callbacks:
            _fn(current_stage=current_stage)

    def on_iter_next_end(self, current_stage: t.Any):
        # noinspection PyAttributeOutsideInit
        self.current_stage = None
        for _fn in self.iter_next_end_callbacks:
            _fn(current_stage=current_stage)

    def add_task(
        self, task_name: str, total: float, msg: str = "", prefix_current_stage: bool = False,
    ) -> ProgressTask:
        """
        Uses reserved generic_progress_bar
        """
        if prefix_current_stage:
            if self.current_stage is None:
                raise e.code.CodingError(
                    msgs=["To prefix current_stage must be using `stages` field and you "
                          "must be iterating on this instance."]
                )
            task_name = f"{self.current_stage}:{task_name}"
        return self.generic_progress.add_task(
            task_name=task_name, total=float(total), msg=msg,
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
        msg: str = "",
        prefix_current_stage: bool = False,
    ) -> t.Generator[r_progress.ProgressType, None, None]:
        """
        Uses reserved generic_progress_bar
        """
        if prefix_current_stage:
            if self.current_stage is None:
                raise e.code.CodingError(
                    msgs=["To prefix current_stage must be using `stages` field and you "
                          "must be iterating on the `StatusPanel` richy instance."]
                )
            task_name = f"{self.current_stage}:{task_name}"
        return self.generic_progress.track(
            sequence=sequence, task_name=task_name, total=total,
            description=description, msg=msg,
        )

    def append_to_summary(self, line: str, highlight_line: int = None):

        # add to summary
        self.summary.append(line)

        # some vars
        _summary = self.summary
        _len = len(_summary)
        _text_lines = []

        # this will show maximum 16 lines and minimum 8 lines
        for _i in range(_len):
            _text_str = _summary[_i]
            if highlight_line == _i:
                _text_str = f"[white]>>> {_text_str} [white]<<<"
            if (_i == 0) or (_i == (_len - 1)) or (highlight_line == _i) or ((_i % ((_len//8) + 1)) == 0):
                _text_lines.append(r_text.Text.from_markup(_text_str, justify='center'))

        # add for rendering
        del self['summary']
        # _msg = f"# Fitting summary \n" + "\n".join(self.summary)
        self['summary'] = r_console.Group(*_text_lines)
        if self.tc_log is not None:
            self.tc_log.info(msg="Summary: ", msgs=[line])

    def set_final_message(self, msg: str):
        self.layout['final_message'] = r_markdown.Markdown(msg)
        self.refresh(update_renderable=True)
        if self.tc_log is not None:
            self.tc_log.info(msg="Final message: ", msgs=[msg])

    def update(
        self,
        status: t.Optional[r_console.RenderableType] = None,
        spinner: t.Optional[SpinnerType] = None,
        # spinner_style: Optional[StyleType] = None
        spinner_speed: t.Optional[float] = None,
    ):
        if spinner is None:
            self.layout['spinner'].update(text=status, speed=spinner_speed)
            self.refresh(update_renderable=False)
        else:
            # todo:
            #   figure this out currently only text update is happening
            #   dont know how spinner can be changed with our API ....
            #   Works with `python -m rich.status` example ...
            #   Note that console which is not widget might be key to solve this
            self.layout['spinner'] = spinner.get_spinner(text=status, speed=spinner_speed)
            self.refresh(update_renderable=True)

        # only log is status is supplied ...
        if status is not None and self.tc_log is not None:
            self.tc_log.info(msg=f"[{self.title}] status changed ...", msgs=[status])

    def convert_to_fit_status_panel(
        self, epochs: int,
    ) -> t.Tuple[t.Callable, t.Callable]:

        # set stages_progress
        if self.layout['stages_progress'] is None:
            self.layout['stages_progress'] = self._make_stages_progress()
        else:
            raise e.code.CodingError(
                msgs=["Was expecting `self.layout['stages_progress']` to be None"]
            )

        # set stages
        if self.stages is None:
            self.stages = [f"epoch {_:0{len(str(epochs))}d}" for _ in range(epochs)]
        else:
            raise e.code.CodingError(
                msgs=["Was expecting `self.stages` this to be None"]
            )

        # refresh renderable
        self.refresh(update_renderable=True)

        # add iter next start callback
        def _iter_next_start(current_stage: str):
            self.update(status=f"Fitting for `{current_stage}` ...")
            _fit_progress = Progress.simple_progress(
                title=f"Train & Validate: {current_stage}",
                box_type=r_box.HORIZONTALS,
                border_style=r_style.Style(color="cyan"),
                use_msg_field=True, console=self.console, tc_log=self.tc_log,
            )
            _fit_progress.add_task(task_name="train", total=None, msg="...")
            _fit_progress.add_task(task_name="validate", total=None, msg="...")
            self['fit_progress'] = _fit_progress
        self.iter_next_start_callbacks.append(_iter_next_start)

        # add iter next start callback
        def _iter_next_end(current_stage: str):
            del self['fit_progress']
        self.iter_next_end_callbacks.append(_iter_next_end)

        # make tran and validate task fetchers
        def _train_task_fetcher() -> ProgressTask:
            return self['fit_progress'].tasks["train"]

        def _validate_task_fetcher() -> ProgressTask:
            return self['fit_progress'].tasks["validate"]

        # return fetchers
        return _train_task_fetcher, _validate_task_fetcher


