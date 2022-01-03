import dataclasses
import typing as t

from .. import error as e
from .. import gui
from .. import marshalling as m
from .. import util
from . import callback, table, widget
from .__base__ import Form


@dataclasses.dataclass
class HashableMethodsRunnerForm(Form):

    hashable: m.HashableClass
    title: str
    # a single receiver will be used for all methods so we share it with `group_tag`
    group_tag: str
    # todo: add icons for this
    close_button: bool
    # todo: add icons for this
    info_button: bool
    callable_names: t.Dict[str, str]
    use_collapsing_header: bool = True

    @property
    @util.CacheResult
    def form_fields_container(
            self) -> t.Union[widget.Group, widget.CollapsingHeader]:
        if self.use_collapsing_header:
            _ret = widget.CollapsingHeader(label=self.title, default_open=True)
            _gp = widget.Group()
            _ret(_gp)
        else:
            _ret = widget.Group()
            _gp = _ret
            _gp(widget=widget.Text(default_value=self.title))
        _gp(widget=self.button_bar)
        _gp(widget=self.receiver)
        return _ret

    @property
    @util.CacheResult
    def button_bar(self) -> widget.Group:
        return widget.Group(horizontal=True)

    @property
    @util.CacheResult
    def receiver(self) -> widget.Group:
        return widget.Group()

    def init(self):
        # call super
        super().init()

        # get some vars
        _buttons_bar = self.button_bar
        _callable_names = self.callable_names
        _receiver = self.receiver

        # add close button
        if self.close_button:
            _buttons_bar(widget=callback.CloseWidgetCallback.get_button_widget(
                widget_to_delete=self), )

        # add info button
        if self.info_button:
            _callable_names["Info"] = "info_widget"

        # make buttons for callable names
        for _button_label, _callable_name in _callable_names.items():
            _b = self.hashable.get_gui_button(
                group_tag=self.group_tag,
                button_label=_button_label,
                callable_name=_callable_name,
                receiver=_receiver,
                allow_refresh=True,
            )
            _buttons_bar(widget=_b)


@dataclasses.dataclass
class HashablesMethodRunnerForm(Form):

    title: str
    callable_name: str
    allow_refresh: bool

    @property
    @util.CacheResult
    def _table(self) -> table.Table:
        # create table
        _table = table.Table.table_from_literals(
            rows=1,
            cols=2,
        )
        _table.header_row = False
        _table.resizable = True
        # _table.policy = gui.En
        _table.borders_innerH = True
        _table.borders_outerH = True
        _table.borders_innerV = True
        _table.borders_outerV = True

        # return
        return _table

    @property
    @util.CacheResult
    def form_fields_container(self) -> widget.Group:
        _grp = widget.Group(horizontal=False)
        _grp(widget=widget.Text(default_value=self.title))
        _grp(widget=self._table)
        return _grp

    @property
    @util.CacheResult
    def button_panel(self) -> widget.Group:
        _grp = widget.Group(horizontal=False)
        self._table[0, 0](_grp)
        return _grp

    @property
    @util.CacheResult
    def receiver_panel(self) -> widget.Group:
        _grp = widget.Group(horizontal=False)
        self._table[0, 1](_grp)
        return _grp

    def add(self, hashable: m.HashableClass, label: str = None):

        # ----------------------------------------------------- 01
        # create button widget
        if label is None:
            label = f"{hashable.__class__.__name__}.{hashable.hex_hash[:-6]}"
        _button = hashable.get_gui_button(
            button_label=label,
            callable_name=self.callable_name,
            receiver=self.receiver_panel,
            allow_refresh=self.allow_refresh,
            # we can maintain this as we will be using single `callable_name` and hence
            # no use for this kwarg
            group_tag=None,
        )

        # ----------------------------------------------------- 02
        # add button widget
        self.button_panel(widget=_button)
