import dataclasses
import abc
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .. import marshalling as m
from .. import util
from .. import error as e
from . import window
from . import asset


class DashboardInternal(m.Internal):
    is_run_called: bool


@dataclasses.dataclass
class Dashboard(m.YamlRepr, abc.ABC):
    """
    Dashboard is not a Widget.
    As of now we think of having only items that do not have parent; like
    + Window
    + Registry
    + theme

    The `primary_window` property holds primary Window which will occupy entire screen

    Figure out having more windows that can be popped inside or can be added
    dynamically.

    Here we will take care of things like
    + screen resolution
    + theme
    + closing even handlers
    + favicon
    + login mechanism

    Note that we make this as primary window when we start GUI

    todo: add less important fields to config and save it to disk ... on
      config field change trigger ui update ... plus also update ui when
      config loaded from disk ... this will indirectly help save ui state :)
      Or maybe have only one config for Dashboard alone and make key value
      pairs ... may be introduce new State file for that
      Also maybe add field save_state for Widget so that we know that only
      these widgets state needs to be saved
    """
    title: str
    width: int = 1370
    height: int = 1200

    @property
    @util.CacheResult
    def internal(self) -> DashboardInternal:
        return DashboardInternal(owner=self)

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.dashboard.{cls.__name__}"

    @staticmethod
    def is_dearpygui_running() -> bool:
        return internal_dpg.is_dearpygui_running()

    @staticmethod
    def is_key_down(key: int) -> bool:
        return internal_dpg.is_key_down(key)

    @staticmethod
    def is_key_pressed(key: int) -> bool:
        return internal_dpg.is_key_pressed(key)

    @staticmethod
    def is_key_released(key: int) -> bool:
        return internal_dpg.is_key_released(key)

    @staticmethod
    def is_mouse_button_clicked(button: int) -> bool:
        return internal_dpg.is_mouse_button_clicked(button)

    @staticmethod
    def is_mouse_button_double_clicked(button: int) -> bool:
        return internal_dpg.is_mouse_button_double_clicked(button)

    @staticmethod
    def is_mouse_button_down(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def is_mouse_button_dragging(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def is_mouse_button_released(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def get_active_window(**kwargs) -> int:
        """
        Refer:
        >>> dpg.get_active_window

        todo: we will return Window widget later ... once we can track Window's in
          Dashboard
        """
        # noinspection PyArgumentList
        return internal_dpg.get_active_window(**kwargs)

    @staticmethod
    def get_windows(**kwargs) -> t.List[int]:
        """
        Refer:
        >>> dpg.get_windows

        todo: we will return Window widgets later ... once we can track Window's in
          Dashboard
        """
        # noinspection PyArgumentList
        return internal_dpg.get_windows(**kwargs)

    @staticmethod
    def get_app_configuration(**kwargs) -> t.Dict:
        """
        Refer:
        >>> dpg.get_app_configuration
        """
        # noinspection PyArgumentList
        return internal_dpg.get_app_configuration(**kwargs)

    @staticmethod
    def get_delta_time(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_delta_time
        """
        # noinspection PyArgumentList
        return internal_dpg.get_delta_time(**kwargs)

    @staticmethod
    def get_drawing_mouse_pos(**kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_drawing_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_drawing_mouse_pos(**kwargs))

    @staticmethod
    def get_frame_count(**kwargs) -> int:
        """
        Refer:
        >>> dpg.get_frame_count
        """
        # noinspection PyArgumentList
        return internal_dpg.get_frame_count(**kwargs)

    @staticmethod
    def get_frame_rate(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_frame_rate
        """
        # noinspection PyArgumentList
        return internal_dpg.get_frame_rate(**kwargs)

    @staticmethod
    def get_global_font_scale(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_global_font_scale
        """
        # noinspection PyArgumentList
        return internal_dpg.get_global_font_scale(**kwargs)

    @staticmethod
    def get_item_types(**kwargs) -> t.Dict:
        """
        Refer:
        >>> dpg.get_item_types
        """
        # noinspection PyArgumentList
        return internal_dpg.get_item_types(**kwargs)

    @staticmethod
    def get_mouse_drag_delta(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_mouse_drag_delta
        """
        # noinspection PyArgumentList
        return internal_dpg.get_mouse_drag_delta(**kwargs)

    @staticmethod
    def get_mouse_pos(local: bool = True, **kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_mouse_pos(local=local, **kwargs))

    @staticmethod
    def get_plot_mouse_pos(**kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_plot_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_plot_mouse_pos(**kwargs))

    @staticmethod
    def get_total_time(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_total_time
        """
        # noinspection PyArgumentList
        return internal_dpg.get_total_time(**kwargs)

    @abc.abstractmethod
    def setup(self):
        ...

    @abc.abstractmethod
    def layout(self):
        ...

    @abc.abstractmethod
    def build(self):
        ...

    def run(self):
        # -------------------------------------------------- 01
        # make sure if was already called
        if self.internal.has("is_run_called"):
            e.code.NotAllowed(
                msgs=[
                    f"You can run only once ..."
                ]
            )
        # -------------------------------------------------- 02
        # setup dpg
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

        # -------------------------------------------------- 03
        # layout and build
        self.setup()
        self.layout()

        # -------------------------------------------------- 04
        # call build and indicate build is done
        self.build()
        self.internal.is_run_called = True

        # -------------------------------------------------- 05
        # dpg related
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


@dataclasses.dataclass
class BasicDashboard(Dashboard):

    @property
    @util.CacheResult
    def primary_window(self) -> "window.Window":
        from .window import Window
        return Window(
            label=self.title, width=self.width, height=self.height,
        )

    def setup(self):
        self.primary_window.setup(dash_board=self)

    def layout(self):
        ...

    def build(self):
        self.primary_window.build()
        # primary window dpg_id
        _primary_window_dpg_id = self.primary_window.dpg_id
        # set the things for primary window
        dpg.set_primary_window(window=_primary_window_dpg_id, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_dpg_id=_ret, size=16)
        dpg.bind_item_theme(item=_primary_window_dpg_id, theme=asset.Theme.DARK.get())
