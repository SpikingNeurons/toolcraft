import dataclasses
import typing as t

from .. import util
from .. import error as e
from .. import marshalling as m
from .__base__ import Form
from .. import gui
from . import widget
from . import table


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

        # add to form_fields_container
        self.form_fields_container(widget=_table)

        # return
        return _table

    @property
    @util.CacheResult
    def form_fields_container(self) -> widget.Group:
        _grp = widget.Group(horizontal=False)
        _grp(widget=widget.Text(default_value=self.title))
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
            button_label=label, callable_name=self.callable_name,
            receiver=self.receiver_panel,
            allow_refresh=self.allow_refresh,
            # as we want to stack the result widget from multiple buttons
            group_tag=None,
        )

        # ----------------------------------------------------- 02
        # add button widget
        self.button_panel(widget=_button)
