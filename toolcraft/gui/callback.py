import dataclasses
import typing as t

import dearpygui.dearpygui as dpg

from .. import error as e
from .. import marshalling as m
from .. import util
from . import asset, widget
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
            "Dark",
            "Light",
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
            label="Select Theme",
        )

    def fn(self, sender: widget.Widget):
        _theme_str = sender.get_value()
        if _theme_str == "Dark":
            _theme = asset.Theme.DARK
        elif _theme_str == "Light":
            _theme = asset.Theme.LIGHT
        else:
            raise e.code.CodingError(msgs=[f"unknown theme {_theme_str}"])
        # we change theme of parent to which this Combo widget is child
        sender.parent.bind_theme(theme=_theme)


@dataclasses.dataclass(frozen=True)
class CloseWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete the widget supplied
    """

    @classmethod
    def get_button_widget(
        cls,
        widget_to_delete: widget.Widget,
        label="Close [X]",
    ) -> widget.Button:
        return widget.Button(
            label=label,
            callback=cls(),
            user_data={"widget_to_delete": widget_to_delete},
        )

    def fn(self, sender: widget.Widget):
        try:
            sender.get_user_data()["widget_to_delete"].delete()
        except KeyError:
            raise e.code.CodingError(msgs=[
                f"Was expecting you to supply dict item `widget_to_delete` in "
                f"`user_data` of sender {sender.__class__}"
            ])


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
                raise e.code.NotAllowed(msgs=[
                    f"looks like you are using group_tag. So please "
                    f"ensure that allow_refresh is set to True"
                ])

    def fn(self, sender: widget.Widget):
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        if self.group_tag is None:
            _tag = (f"{_hashable.__class__.__name__}:"
                    f"{_hashable.hex_hash[-10:]}.{self.callable_name}")
        else:
            # this make sure that same guid is shared across multiple
            # callbacks that use same tab_group_name.
            # Note this applies if _hashable and receiver are same
            _tag = (f"{_hashable.__class__.__name__}:"
                    f"{_hashable.hex_hash[-10:]}.{self.group_tag}")

        # get widget for given tag if present
        if Tag.exists(tag_or_widget=_tag):
            _widget = Tag.get_widget(tag=_tag)
        else:
            _widget = None
        _before_widget = None

        # if allow refresh then delete widget and set it to None so that it
        # can be created again
        if self.allow_refresh:
            # if widget is available i.e. it is tagged then delete it
            if _widget is not None:
                # fetch _before_widget
                # we are assuming this will be MovableWidget ... Note that we want to
                # keep this way and if possible modify other code ... this is possible
                # for container widgets and we do not see that this callback will be
                # used non movable Widgets
                try:
                    _before_widget = _widget.parent.children[
                        _widget.index_in_parent_children + 1]
                except IndexError:
                    ...
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
            _new_widget = util.rgetattr(
                _hashable, self.callable_name)()  # type: widget.MovableWidget

            # tag it as it was newly created
            _new_widget.tag_it(tag=_tag)

            # add to receiver children
            _receiver(_new_widget)

            # move widget
            if _before_widget is not None:
                _new_widget.move(before=_before_widget)
