"""
Refer:
https://github.com/Textualize/rich/blob/master/examples/dynamic_progress.py
https://github.com/Textualize/rich/blob/master/examples/live_progress.py
"""

import dataclasses
import typing as t
from rich.emoji import EMOJI
from rich.spinner import SPINNERS
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
                if _v in SPINNERS.keys():
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

    @classmethod
    def for_download(cls, title: str) -> "Progress":
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
                        "finished": EMOJI["heavy_check_mark"],
                        "failed": EMOJI["heavy_multiplication_x"],
                    }
                ),
            },
        )

        return _progress
