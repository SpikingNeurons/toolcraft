import dataclasses
import typing as t

from .. import error as e
from .. import util
from . import __base__, _auto, dashboard


class WindowInternal(__base__.DpgInternal):
    dash_board: dashboard.Dashboard

    def test_if_others_set(self):
        if not self.has("dash_board"):
            e.code.CodingError(msgs=[
                f"Window {self.__class__} has no dash_board",
                f"Make sure you have called `Window.setup(dash_board)` "
                f"before building window",
            ])


class _DowngradeContainerWidget:
    @property
    @util.CacheResult
    def internal(self) -> WindowInternal:
        # noinspection PyTypeChecker
        return WindowInternal(owner=self)

    @property
    def parent(self) -> None:
        e.code.CodingError(msgs=[
            "Use of `parent` for `Window` is not allowed.",
            "Please use `dash_board` instead.",
        ])
        raise

    @property
    def dash_board(self) -> dashboard.Dashboard:
        return self.internal.dash_board

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.window.{cls.__name__}"

    def setup(self, dash_board: dashboard.Dashboard):
        self.internal.dash_board = dash_board


@dataclasses.dataclass
class Window(_DowngradeContainerWidget, _auto.Window):
    @property
    def root(self) -> "Window":
        return self


@dataclasses.dataclass
class FileDialog(_DowngradeContainerWidget, _auto.FileDialog):
    @property
    def root(self) -> "FileDialog":
        return self
