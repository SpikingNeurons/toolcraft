import dataclasses
import dearpygui.dearpygui as dpg
import typing as t

from .. import util
from .. import marshalling as m
from .. import error as e
from . import Widget, Callback, Binder
from . import widget
from . import assets


@dataclasses.dataclass(frozen=True)
class SetThemeCallback(Callback):
    """
    todo: we will get rid of this callback in favour of assets module ...
      once we understand theme, icon, font, background, color etc styling
      related things
    """

    @staticmethod
    def themes() -> t.List[str]:
        return [
            "Dark", "Light",
            # "Classic",
            # "Dark 2", "Grey", "Purple",
            # "Dark Grey", "Cherry", "Gold", "Red"
        ]

    @staticmethod
    def default_theme() -> str:
        return "Dark"

    @classmethod
    def get_combo_widget(cls) -> widget.Combo:
        return widget.Combo(
            items=cls.themes(),
            default_value=cls.default_theme(),
            callback=cls(),
            label="Select Theme"
        )

    def fn(
        self,
        sender: Widget,
        app_data: t.Any,
        user_data: t.Union[Widget, t.List[Widget]]
    ):
        _theme_str = dpg.get_value(item=sender.dpg_id)
        if _theme_str == "Dark":
            _theme = assets.Theme.Dark
        elif _theme_str == "Light":
            _theme = assets.Theme.Light
        else:
            e.code.CodingError(
                msgs=[
                    f"unknown theme {_theme_str}"
                ]
            )
            raise
        # we change theme of parent to which this Combo widget is child
        sender.parent.set_theme(theme=_theme)


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

    def fn(
        self,
        sender: Widget,
        app_data: t.Any,
        user_data: t.Union[Widget, t.List[Widget]]
    ):
        sender.parent.delete()


@dataclasses.dataclass(frozen=True)
class RefreshWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent and
    then call the refresh function that must ideally add the deleted widget back
    """

    refresh_callback: Callback

    @classmethod
    def get_button_widget(
        cls, refresh_callback: Callback, label: str = "Refresh [R]"
    ) -> widget.Button:
        return widget.Button(
            label=label,
            callback=cls(refresh_callback=refresh_callback)
        )

    def fn(
        self,
        sender: Widget,
        app_data: t.Any,
        user_data: t.Union[Widget, t.List[Widget]]
    ):
        sender.parent.delete()
        self.refresh_callback.fn(
            sender=sender, app_data=app_data, user_data=user_data)


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

    def fn(
        self,
        sender: Widget,
        app_data: t.Any,
        user_data: t.Union[Widget, t.List[Widget]]
    ):
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        if self.tab_group_name is None:
            _unique_guid = f"{_hashable.hex_hash[-6:]}_{self.callable_name}"
        else:
            # this make sure that same guid is shared across multiple
            # callbacks that use same tab_group_name.
            # Note this applies if _hashable and receiver are same
            _unique_guid = f"{_hashable.hex_hash[-6:]}_{self.tab_group_name}"

        # if present in children
        if _unique_guid in _receiver.children.keys():
            # if allow refresh delete so that it can be added later
            if self.allow_refresh:
                _receiver.children[_unique_guid].delete()
            # else return as nothing to do
            else:
                return

        # get actual result widget we are interested to display ... and make
        # it child to receiver
        util.rgetattr(
            _hashable, self.callable_name
        )(
            binder=Binder(
                guid=_unique_guid, parent=_receiver,
                # before=None
            )
        )


@dataclasses.dataclass(frozen=True)
class HashableMethodsRunnerCallback(Callback):
    """
    Special class just to create a button bar if you do not want to have a
    special method that generates button bar
    """
    tab_group_name: str
    hashable: m.HashableClass
    title: str
    close_button: bool
    callable_names: t.List[str]
    callable_labels: t.List[str]
    receiver: Widget
    allow_refresh: bool

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

        # length must be same
        if len(self.callable_names) != len(self.callable_labels):
            e.validation.NotAllowed(
                msgs=[
                    f"We expect fields `callable_names` and `callable_labels` "
                    f"to have same length"
                ]
            )

    def fn(
        self,
        sender: Widget,
        app_data: t.Any,
        user_data: t.Union[Widget, t.List[Widget]]
    ):
        # import
        from . import helper

        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        # this make sure that same guid is shared across multiple
        # callbacks that use same tab_group_name.
        # Note this applies if _hashable and receiver are same
        _unique_guid = f"{_hashable.hex_hash[-6:]}_{self.tab_group_name}"

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
        _result_widget = helper.button_bar_from_hashable_callables(
            tab_group_name=self.tab_group_name,
            hashable=self.hashable,
            title=self.title,
            close_button=self.close_button,
            callable_names={
                k: v for k, v in zip(self.callable_labels, self.callable_names)
            },
        )
        _receiver.add_child(
            guid=_unique_guid,
            widget=_result_widget
        )



