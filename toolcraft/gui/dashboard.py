import dataclasses
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from . import window
from . import widget
from .__base__ import Dashboard


@dataclasses.dataclass
class BasicDashboard(Dashboard):
    """
    A dashboard with one primary window ... and can lay out all fields inside it
    """

    def layout(self) -> "window.Window":
        from .window import Window
        _primary_window = Window(
            label=self.title, width=self.width, height=self.height,
        )
        for _fn in self.dataclass_field_names:
            _fv = getattr(self, _fn)
            if isinstance(_fv, widget.MovableWidget):
                _primary_window(widget=_fv)
        return _primary_window
