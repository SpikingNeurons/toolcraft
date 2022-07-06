import dataclasses
import abc
import asyncio
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .. import marshalling as m
from .. import util
from .. import dapr
from .. import logger
from .. import error as e
from . import window
from . import asset
from . import widget
from . import callback
from . import form
from .__base__ import Dashboard


_LOGGER = logger.get_logger()


@dataclasses.dataclass
@m.RuleChecker(
    things_to_be_cached=['primary_window'],
)
class BasicDashboard(Dashboard):
    """
    A dashboard with one primary window ... and can layout all fields inside it
    """

    @property
    @util.CacheResult
    def primary_window(self) -> "window.Window":
        from .window import Window
        return Window(
            label=self.title, width=self.width, height=self.height,
        )

    def setup(self):
        self.primary_window.setup(dash_board=self)

    def layout(self):
        _primary_window = self.primary_window
        for _fn in self.dataclass_field_names:
            _fv = getattr(self, _fn)
            if isinstance(_fv, widget.MovableWidget):
                _primary_window(widget=_fv)

    def build(self):
        self.primary_window.build()
        # primary window dpg_id
        _primary_window_dpg_id = self.primary_window.dpg_id
        # set the things for primary window
        dpg.set_primary_window(window=_primary_window_dpg_id, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_dpg_id=_ret, size=16)
        dpg.bind_item_theme(item=_primary_window_dpg_id, theme=asset.Theme.DARK.get())


@dataclasses.dataclass
@m.RuleChecker(
    things_to_be_cached=['split_form', 'console_form'],
)
class DaprClientDashboard(Dashboard):

    subtitle: str = None
    callable_name: str = None

    @property
    @util.CacheResult
    def primary_window(self) -> "window.Window":
        from .window import Window
        return Window(
            label=self.title, width=self.width, height=self.height,
        )

    @property
    @util.CacheResult
    def split_form(self) -> form.DoubleSplitForm:
        return form.DoubleSplitForm(
            title=f"...",
            callable_name=self.callable_name,
            allow_refresh=False,
            collapsing_header_open=False,
        )

    @property
    @util.CacheResult
    def console_form(self) -> widget.CollapsingHeader:

        _console_ch = widget.CollapsingHeader(default_open=False, label="Console")
        _receiver = widget.Text(default_value="...")
        # note only available for `dapr.DaprMode.client`
        _server = dapr.DAPR.server

        @dataclasses.dataclass(frozen=True)
        class __Callback(callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: widget.Widget):
                # noinspection PyTypeChecker
                _dapr_mode: str = sender.get_user_data()['dapr_mode']
                _receiver.default_value = _server.read_logs(
                    num_bytes=2048, dapr_mode=_dapr_mode)

        _button_bar = widget.Group(horizontal=True)
        _button_bar(
            widget=widget.Button(
                label="Launch Log",
                callback=__Callback(),
                user_data={"dapr_mode": dapr.DaprMode.launch.name},
            )
        )
        _button_bar(
            widget=widget.Button(
                label="Server Log",
                callback=__Callback(),
                user_data={"dapr_mode": dapr.DaprMode.server.name},
            )
        )

        _console_ch(widget=_button_bar)
        _console_ch(widget=_receiver)

        return _console_ch

    def setup(self):
        self.primary_window.setup(dash_board=self)

    def layout(self):
        # get _primary_window
        _primary_window = self.primary_window

        # add theme selector
        _primary_window(
            widget=callback.SetThemeCallback.get_combo_widget()
        )

        # add subtitle
        _primary_window(
            widget=widget.Text(default_value=self.subtitle,)
        )

        # add split form
        _primary_window(widget=self.split_form)

        # make console
        _primary_window(widget=self.console_form)

    def build(self):
        self.primary_window.build()
        # primary window dpg_id
        _primary_window_dpg_id = self.primary_window.dpg_id
        # set the things for primary window
        dpg.set_primary_window(window=_primary_window_dpg_id, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_dpg_id=_ret, size=16)
        dpg.bind_item_theme(item=_primary_window_dpg_id, theme=asset.Theme.DARK.get())

    def add_hashable(self, hashable: m.HashableClass, group_key: str = None,):
        self.split_form.add(
            hashable=hashable, group_key=group_key,
        )


