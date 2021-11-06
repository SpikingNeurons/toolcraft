import dataclasses
import dearpygui.dearpygui as dpg
import typing as t

from .. import util
from .. import marshalling as m
from .. import error as e
from . import widget, asset
from .__base__ import Callback, Tag


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
        sender: widget.Widget,
        app_data: t.Any,
        user_data: t.Union[widget.Widget, t.List[widget.Widget]],
    ):
        _theme_str = dpg.get_value(item=sender.dpg_id)
        if _theme_str == "Dark":
            _theme = asset.Theme.DARK
        elif _theme_str == "Light":
            _theme = asset.Theme.LIGHT
        else:
            e.code.CodingError(
                msgs=[
                    f"unknown theme {_theme_str}"
                ]
            )
            raise
        # we change theme of parent to which this Combo widget is child
        sender.parent.bind_theme(theme=_theme)


@dataclasses.dataclass(frozen=True)
class CloseWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent
    """

    widget_to_delete: widget.Widget

    @classmethod
    def get_button_widget(
        cls, widget_to_delete: widget.Widget
    ) -> widget.Button:
        return widget.Button(
            label="Close [X]",
            callback=cls(widget_to_delete)
        )

    def fn(
        self,
        sender: widget.Widget,
        app_data: t.Any,
        user_data: t.Union[widget.Widget, t.List[widget.Widget]],
    ):
        # sender.parent.delete()
        self.widget_to_delete.delete()


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
        sender: widget.Widget,
        app_data: t.Any,
        user_data: t.Union[widget.Widget, t.List[widget.Widget]],
    ):
        sender.parent.delete()
        self.refresh_callback.fn(
            sender=sender, app_data=app_data, user_data=user_data)


@dataclasses.dataclass(frozen=True)
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.

    If group_tag is None then we make unique guid for all callable_name
    else we reuse group_tag across different callables this will just
    mimic the TabGroup behaviour where one receiver widget will be updated.

    Note that this will mean that allow_refresh will be True when
    tab_group_name is not None.
    """
    hashable: m.HashableClass
    callable_name: str
    receiver: widget.ContainerWidget
    allow_refresh: bool
    group_tag: str = None

    def init_validate(self):
        # call super
        super().init_validate()

        # if tab_group_name is supplied that means you are sharing receiver
        # object across multiple Callbacks with same tab_group_name
        # So ensure that the allow_refresh is True
        if self.group_tag is not None:
            if not self.allow_refresh:
                e.code.NotAllowed(
                    msgs=[
                        f"looks like you are using group_tag. So please "
                        f"ensure that allow_refresh is set to True"
                    ]
                )

    def fn(
        self,
        sender: widget.Widget,
        app_data: t.Any,
        user_data: t.Union[widget.Widget, t.List[widget.Widget]],
    ):
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        if self.group_tag is None:
            _tag = f"{_hashable.__class__.__name__}:" \
                   f"{_hashable.hex_hash[-10:]}.{self.callable_name}"
        else:
            # this make sure that same guid is shared across multiple
            # callbacks that use same tab_group_name.
            # Note this applies if _hashable and receiver are same
            _tag = f"{_hashable.__class__.__name__}:" \
                   f"{_hashable.hex_hash[-10:]}.{self.group_tag}"

        # get widget for given tag if present
        # noinspection PyTypeChecker
        _widget = Tag.get_widget(tag=_tag)

        # if allow refresh then delete widget and set it to None so that it
        # can be created again
        if self.allow_refresh and _widget is not None:
            # this will delete itself
            # this will also remove itself from `parent.children`
            # this will also untag itself if tagged
            _widget.delete()
            # set back to None so that it can be recreated
            # noinspection PyTypeChecker
            _widget = None

        # if widget is not present create it
        if _widget is None:
            # get actual result widget we are interested to display ... and make
            # it child to receiver
            _widget = util.rgetattr(
                _hashable, self.callable_name)()  # type: widget.MovableWidget

            # tag it as it was newly created
            _widget.tag_it(tag=_tag)

            # add to receiver children
            _receiver(_widget)


@dataclasses.dataclass(frozen=True)
class HashableMethodsRunnerCallback(Callback):
    """
    Special class just to create a button bar if you do not want to have a
    special method that generates button bar
    """
    group_tag: str
    hashable: m.HashableClass
    title: str
    close_button: bool
    info_button: bool
    callable_names: t.List[str]
    callable_labels: t.List[str]
    receiver: widget.ContainerWidget
    allow_refresh: bool

    def fn(
        self,
        sender: widget.Widget,
        app_data: t.Any,
        user_data: t.Union[widget.Widget, t.List[widget.Widget]]
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
        _unique_guid = f"{_hashable.hex_hash[-6:]}_{self.group_tag}"

        # if present in children
        if _unique_guid in self.temp_store.keys():
            # if allow refresh delete so that it can be added later
            if self.allow_refresh:
                # deletes from dpg and the children list of parent
                self.temp_store[_unique_guid].delete()
                # del from temp storage
                del self.temp_store[_unique_guid]
            # else return as nothing to do
            else:
                return

        # get actual result widget we are interested to display ... and make
        # it child to receiver
        _result_widget = helper.button_bar_from_hashable_callables(
            group_tag=self.group_tag,
            hashable=self.hashable,
            title=self.title,
            close_button=self.close_button,
            info_button=self.info_button,
            callable_names={
                k: v for k, v in zip(self.callable_labels, self.callable_names)
            },
        )

        # add to temp storage
        self.temp_store[_unique_guid] = _result_widget

        # add to receiver children
        _receiver(_result_widget)



