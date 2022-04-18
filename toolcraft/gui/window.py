import typing as t
import dataclasses
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import dearpygui.dearpygui as dpg

from .. import error as e
from .. import util
from . import dashboard
from . import __base__
from . import _auto
from . import widget
from . import EnMouseButton


class WindowInternal(__base__.WidgetInternal):
    dash_board: dashboard.Dashboard

    def test_if_others_set(self):
        if not self.has("dash_board"):
            raise e.code.CodingError(
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
        # noinspection PyTypeChecker
        return WindowInternal(owner=self)

    @property
    def parent(self) -> None:
        raise e.code.CodingError(
            msgs=[
                "Use of `parent` for `Window` is not allowed.",
                "Please use `dash_board` instead.",
            ]
        )

    @property
    def dash_board(self) -> dashboard.Dashboard:
        return self.internal.dash_board

    @property
    def root(self) -> "Window":
        return self

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.window.{cls.__name__}"

    def setup(self, dash_board: dashboard.Dashboard):
        self.internal.dash_board = dash_board


@dataclasses.dataclass
class PopUp(Window):
    """
    PopUp is special Window ...
    Note that `dpg.popup` is made with thin wrapper over Window ...
    so we replicate it here as we do not have respective `add_popup` method

    todo: implement this with our wrraper for handler_registry

    Refer:
    >>> dpg.popup
    """
    # hover_over: widget.Widget = None
    # mousebutton: EnMouseButton = EnMouseButton.Right
    # min_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
    #     dataclasses.field(default_factory=lambda: [100, 100])
    # max_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
    #     dataclasses.field(default_factory=lambda: [30000, 30000])
    # no_move: bool = False
    # no_background: bool = False
    #
    # def build(self) -> t.Union[int, str]:
    #     _internal_popup_id = internal_dpg.generate_uuid()
    #     _handler_reg_id = internal_dpg.add_item_handler_registry()
    #     internal_dpg.add_item_clicked_handler(
    #         self.mousebutton.value,
    #         parent=internal_dpg.last_item(),
    #         callback=lambda: internal_dpg.configure_item(
    #             _internal_popup_id, show=True))
    #     internal_dpg.bind_item_handler_registry(
    #         self.hover_over.dpg_id, _handler_reg_id)
    #
    #     _ret = super().build()
    #
    #     return _ret


@dataclasses.dataclass
class FileDialog(_auto.FileDialog):

    @property
    @util.CacheResult
    def internal(self) -> WindowInternal:
        # noinspection PyTypeChecker
        return WindowInternal(owner=self)

    @property
    def parent(self) -> None:
        raise e.code.CodingError(
            msgs=[
                "Use of `parent` for `Window` is not allowed.",
                "Please use `dash_board` instead.",
            ]
        )

    @property
    def dash_board(self) -> dashboard.Dashboard:
        return self.internal.dash_board

    @property
    def root(self) -> "FileDialog":
        return self

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.window.{cls.__name__}"

    def setup(self, dash_board: dashboard.Dashboard):
        self.internal.dash_board = dash_board
