import dataclasses
import pathlib
from dearpygui import core as dpg
import abc
import typing as t

from .. import util
from .. import marshalling as m
from .. import storage as s
from .. import gui
from .. import error as e
from . import Widget, Callback, widget


@dataclasses.dataclass(frozen=True)
class SetThemeCallback(Callback):

    @staticmethod
    def themes() -> t.List[str]:
        return [
            "Dark", "Light", "Classic", "Dark 2", "Grey",
            "Dark Grey", "Cherry", "Purple", "Gold", "Red"
        ]

    @staticmethod
    def default_theme() -> str:
        return "Dark Grey"

    @classmethod
    def get_combo_widget(cls) -> widget.Combo:
        dpg.set_theme(theme=cls.default_theme())
        return widget.Combo(
            items=cls.themes(),
            default_value=cls.default_theme(),
            callback=cls()
        )

    def fn(self):
        _theme = dpg.get_value(name=self.sender.name)
        dpg.set_theme(theme=_theme)


@dataclasses.dataclass(frozen=True)
class CloseWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent
    """

    @classmethod
    def get_button_widget(cls) -> widget.Button:
        return widget.Button(
            label="Close [X]",
            callback=cls()
        )

    def fn(self):
        self.sender.parent.delete()


@dataclasses.dataclass(frozen=True)
class RefreshWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent and
    then call the refresh function that must ideally add the deleted widget back
    """

    refresh_callback: Callback

    @classmethod
    def get_button_widget(
        cls, refresh_callback: Callback
    ) -> widget.Button:
        return widget.Button(
            label="Refresh [R]",
            callback=cls(refresh_callback=refresh_callback)
        )

    def fn(self):
        self.sender.parent.delete()
        self.refresh_callback.fn()


@dataclasses.dataclass(frozen=True)
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.

    If tab_group_name is None then we make unique guid for all callable_name
    else we reuse tab_group_name across different callables this will just
    mimic the TabGroup behaviour where one receiver widget will be updated.

    Note that this will mean that allow_refresh will be True when
    tab_group_name is not None.
    """
    hashable: m.HashableClass
    callable_name: str
    receiver: Widget
    allow_refresh: bool
    tab_group_name: str = None

    def init_validate(self):
        # call super
        super().init_validate()

        # check if receiver can accept child
        if not self.receiver.is_container:
            e.validation.NotAllowed(
                msgs=[
                    f"We expect a receiver that can accept children..."
                ]
            )

        # if tab_group_name is supplied that means you are sharing receiver
        # object across multiple Callbacks with same tab_group_name
        # So ensure that the allow_refresh is True
        if self.tab_group_name is not None:
            if not self.allow_refresh:
                e.code.NotAllowed(
                    msgs=[
                        f"looks like you are using tab_group_name. So please "
                        f"ensure that allow_refresh is set to True"
                    ]
                )

    def fn(self):
        # get some vars
        _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        if self.tab_group_name is None:
            _unique_guid = f"{_hashable.hex_hash}_{self.callable_name}"
        else:
            # this make sure that same guid is shared across multiple
            # callbacks that use same tab_group_name.
            # Note this applies if _hashable and receiver are same
            _unique_guid = f"{_hashable.hex_hash}_{self.tab_group_name}"

        # if present in children
        if _unique_guid in _receiver.children.keys():
            # if allow refresh delete so that it can be deleted later
            if self.allow_refresh:
                _receiver.children[_unique_guid].delete()
            # else return as nothing to do
            else:
                return

        # get actual result widget we are interested to display ... and make
        # it child to receiver
        _result_widget = util.rgetattr(
            _hashable, self.callable_name
        )()
        _receiver.add_child(
            guid=_unique_guid,
            widget=_result_widget
        )



