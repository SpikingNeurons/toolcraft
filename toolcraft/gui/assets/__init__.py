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
    Default = enum.auto()
    Dark = enum.auto()
    Light = enum.auto()

    @property
    @util.CacheResult
    def dpg_id(self) -> int:
        if self is self.Default:
            return 0
        elif self is self.Dark:
            return themes.create_theme_imgui_dark()
        elif self is self.Light:
            return themes.create_theme_imgui_light()
        else:
            e.code.ShouldNeverHappen(
                msgs=[
                    f"Unsupported theme {self}"
                ]
            )
            raise



