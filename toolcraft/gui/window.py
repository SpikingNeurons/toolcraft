import dataclasses
import dearpygui.dearpygui as dpg

from . import dashboard
from . import _auto


@dataclasses.dataclass
class Window(_auto.Window):

    @property
    def parent(self) -> None:
        raise Exception(
            "Use of `parent` for `Window` is not allowed.",
            "Please use `dash_board` instead.",
        )

    @parent.setter
    def parent(self, value):
        raise Exception(
            f"Property parent should not be set for Window ..."
        )

    @property
    def dash_board(self) -> "dashboard.Dashboard":
        if self._dash_board is None:
            raise Exception(f"The dash_board property was never set so cannot retrieve it ...")
        return self._dash_board

    @dash_board.setter
    def dash_board(self, value: "dashboard.Dashboard"):
        if self._dash_board is not None:
            raise Exception(f"The property dash_board is already set so cannot set it again")
        self._dash_board = value

    @property
    def root(self) -> "Window":
        return self


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
    # def build(self) -> int:
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

    def setup(self, dash_board: dashboard.Dashboard):
        self.internal.dash_board = dash_board
