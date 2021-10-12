import enum
import pathlib
import dearpygui.dearpygui as dpg
from dearpygui import themes

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


class Theme(enum.Enum):
    DEFAULT = 0
    DARK = themes.create_theme_imgui_dark()
    LIGHT = themes.create_theme_imgui_light()



