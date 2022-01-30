import enum
import pathlib
import typing as t

import dearpygui.dearpygui as dpg
from dearpygui_ext import themes

from ... import util
from ... import error as e

_ASSET_FOLDER = pathlib.Path(__file__).parent.resolve()


class Font(enum.Enum):
    RobotoRegular = enum.auto()

    @property
    def file(self) -> pathlib.Path:
        return _ASSET_FOLDER / "fonts" / f"{self.name}.ttf"

    def set(self, item_dpg_id: int, size: int = 13):
        _dpg_font_id = dpg.font(file=self.file.as_posix(), size=size)
        dpg.set_item_font(item_dpg_id, _dpg_font_id)


_THEMES_CACHE = {}


class Theme(enum.Enum):
    DARK = enum.auto()
    LIGHT = enum.auto()

    def get(self) -> t.Union[int, str]:
        if self in _THEMES_CACHE.keys():
            return _THEMES_CACHE[self]
        if self is self.DARK:
            _THEMES_CACHE[self] = themes.create_theme_imgui_dark()
        elif self is self.LIGHT:
            _THEMES_CACHE[self] = themes.create_theme_imgui_light()
        else:
            raise e.code.NotSupported(
                msgs=[
                    f"Theme {self} is not supported"
                ]
            )
        return _THEMES_CACHE[self]



