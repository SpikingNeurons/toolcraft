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

    def fn(self, sender: widget.Widget):
        _theme_str = sender.get_value()
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
    This callback will be added to a Button that will delete the widget supplied
    """

    @classmethod
    def get_button_widget(
        cls, widget_to_delete: widget.Widget, label="Close [X]",
    ) -> widget.Button:
        return widget.Button(
            label=label,
            callback=cls(),
            user_data={'widget_to_delete': widget_to_delete},
        )

    def fn(self, sender: widget.Widget):
        try:
            sender.get_user_data()['widget_to_delete'].delete()
        except KeyError:
            e.code.CodingError(
                msgs=[
                    f"Was expecting you to supply dict item `widget_to_delete` in "
                    f"`user_data` of sender {sender.__class__}"
                ]
            )



