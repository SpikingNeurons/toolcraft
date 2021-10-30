import typing as t
import dataclasses

from .. import error as e
from .. import util
from . import dashboard
from . import __base__
from . import _auto


class WindowInternal(__base__.DpgInternal):
    dash_board: dashboard.Dashboard

    def test_if_others_set(self):
        if not self.internal.has("dash_board"):
            e.code.CodingError(
                msgs=[
                    f"Window {self.__class__} has no dash_board",
                    f"Make sure you have called `Window.setup(dash_board)` "
                    f"before building window",
                ]
            )


@dataclasses.dataclass
class Window(_auto.Window):

    @property
    @util.CacheResult
    def internal(self) -> WindowInternal:
        return WindowInternal(owner=self)

    @property
    def parent(self) -> None:
        e.code.CodingError(
            msgs=[
                "Use of `parent` for `Window` is not allowed.",
                "Please use `dash_board` instead.",
            ]
        )
        raise

    @property
    def root(self) -> None:
        e.code.CodingError(
            msgs=[
                "Use of `root` for `Window` is not allowed.",
                "Please use `dash_board` instead.",
            ]
        )
        raise

    @property
    def dash_board(self) -> dashboard.Dashboard:
        return self.internal.dash_board

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.window.{cls.__name__}"

    def setup(self, dash_board: dashboard.Dashboard):
        self.internal.dash_board = dash_board
