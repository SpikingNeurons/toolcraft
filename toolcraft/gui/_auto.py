"""
********************************************************************************
This code is auto-generated:
>> Script: toolcraft/gui/_scripts/dpg_generator.py
>> DearPyGui: 1.10.1
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import dataclasses
import enum
import abc
import typing as t

from .__base__ import Widget
from .__base__ import MovableWidget
from .__base__ import ContainerWidget
from .__base__ import MovableContainerWidget
from .__base__ import Callback
from .__base__ import Registry
from .__base__ import RegistryItem
from .__base__ import PlotSeries
from .__base__ import PlotItem
from .__base__ import PLOT_DATA_TYPE
from .__base__ import COLOR_TYPE
from .__base__ import USER_DATA


class EnDir(enum.Enum):

    Left = internal_dpg.mvDir_Left  # 0
    Up = internal_dpg.mvDir_Up  # 2
    Down = internal_dpg.mvDir_Down  # 3
    Right = internal_dpg.mvDir_Right  # 1
    NONE = internal_dpg.mvDir_None  # -1


class EnTimeUnit(enum.Enum):

    Day = internal_dpg.mvTimeUnit_Day  # 5
    Hr = internal_dpg.mvTimeUnit_Hr  # 4
    Min = internal_dpg.mvTimeUnit_Min  # 3
    Mo = internal_dpg.mvTimeUnit_Mo  # 6
    Ms = internal_dpg.mvTimeUnit_Ms  # 1
    S = internal_dpg.mvTimeUnit_S  # 2
    Us = internal_dpg.mvTimeUnit_Us  # 0
    Yr = internal_dpg.mvTimeUnit_Yr  # 7


class EnPlotColormap(enum.Enum):

    BrBG = internal_dpg.mvPlotColormap_BrBG  # 12
    Cool = internal_dpg.mvPlotColormap_Cool  # 7
    Dark = internal_dpg.mvPlotColormap_Dark  # 1
    Deep = internal_dpg.mvPlotColormap_Deep  # 0
    Default = internal_dpg.mvPlotColormap_Default  # 0
    Greys = internal_dpg.mvPlotColormap_Greys  # 15
    Hot = internal_dpg.mvPlotColormap_Hot  # 6
    Jet = internal_dpg.mvPlotColormap_Jet  # 9
    Paired = internal_dpg.mvPlotColormap_Paired  # 3
    Pastel = internal_dpg.mvPlotColormap_Pastel  # 2
    PiYG = internal_dpg.mvPlotColormap_PiYG  # 13
    Pink = internal_dpg.mvPlotColormap_Pink  # 8
    Plasma = internal_dpg.mvPlotColormap_Plasma  # 5
    RdBu = internal_dpg.mvPlotColormap_RdBu  # 11
    Spectral = internal_dpg.mvPlotColormap_Spectral  # 14
    Twilight = internal_dpg.mvPlotColormap_Twilight  # 10
    Viridis = internal_dpg.mvPlotColormap_Viridis  # 4


class EnComboHeight(enum.Enum):

    Small = internal_dpg.mvComboHeight_Small  # 0
    Regular = internal_dpg.mvComboHeight_Regular  # 1
    Large = internal_dpg.mvComboHeight_Large  # 2
    Largest = internal_dpg.mvComboHeight_Largest  # 3


class EnDatePickerLevel(enum.Enum):

    Day = internal_dpg.mvDatePickerLevel_Day  # 0
    Month = internal_dpg.mvDatePickerLevel_Month  # 1
    Year = internal_dpg.mvDatePickerLevel_Year  # 2


class EnPlotLocation(enum.Enum):

    Center = internal_dpg.mvPlot_Location_Center  # 0
    East = internal_dpg.mvPlot_Location_East  # 8
    North = internal_dpg.mvPlot_Location_North  # 1
    NorthEast = internal_dpg.mvPlot_Location_NorthEast  # 9
    NorthWest = internal_dpg.mvPlot_Location_NorthWest  # 5
    South = internal_dpg.mvPlot_Location_South  # 2
    SouthEast = internal_dpg.mvPlot_Location_SouthEast  # 10
    SouthWest = internal_dpg.mvPlot_Location_SouthWest  # 6
    West = internal_dpg.mvPlot_Location_West  # 4


class EnThemeCat(enum.Enum):

    Core = internal_dpg.mvThemeCat_Core  # 0
    Plots = internal_dpg.mvThemeCat_Plots  # 1
    Nodes = internal_dpg.mvThemeCat_Nodes  # 2


class EnCullMode(enum.Enum):

    Back = internal_dpg.mvCullMode_Back  # 1
    Front = internal_dpg.mvCullMode_Front  # 2
    NONE = internal_dpg.mvCullMode_None  # 0


class EnNodeAttr(enum.Enum):

    Input = internal_dpg.mvNode_Attr_Input  # 0
    Output = internal_dpg.mvNode_Attr_Output  # 1
    Static = internal_dpg.mvNode_Attr_Static  # 2


class EnMouseButton(enum.Enum):

    Left = internal_dpg.mvMouseButton_Left  # 0
    Middle = internal_dpg.mvMouseButton_Middle  # 2
    Right = internal_dpg.mvMouseButton_Right  # 1
    X1 = internal_dpg.mvMouseButton_X1  # 3
    X2 = internal_dpg.mvMouseButton_X2  # 4
    Any = -1


class EnPlatform(enum.Enum):

    Apple = internal_dpg.mvPlatform_Apple  # 1
    Linux = internal_dpg.mvPlatform_Linux  # 2
    Windows = internal_dpg.mvPlatform_Windows  # 0


class EnKey(enum.Enum):

    Num0 = internal_dpg.mvKey_0  # 48
    Num1 = internal_dpg.mvKey_1  # 49
    Num2 = internal_dpg.mvKey_2  # 50
    Num3 = internal_dpg.mvKey_3  # 51
    Num4 = internal_dpg.mvKey_4  # 52
    Num5 = internal_dpg.mvKey_5  # 53
    Num6 = internal_dpg.mvKey_6  # 54
    Num7 = internal_dpg.mvKey_7  # 55
    Num8 = internal_dpg.mvKey_8  # 56
    Num9 = internal_dpg.mvKey_9  # 57
    A = internal_dpg.mvKey_A  # 65
    Add = internal_dpg.mvKey_Add  # 107
    Alt = internal_dpg.mvKey_Alt  # 18
    Apps = internal_dpg.mvKey_Apps  # 93
    B = internal_dpg.mvKey_B  # 66
    Back = internal_dpg.mvKey_Back  # 8
    Backslash = internal_dpg.mvKey_Backslash  # 220
    Browser_Back = internal_dpg.mvKey_Browser_Back  # 166
    Browser_Favorites = internal_dpg.mvKey_Browser_Favorites  # 171
    Browser_Forward = internal_dpg.mvKey_Browser_Forward  # 167
    Browser_Home = internal_dpg.mvKey_Browser_Home  # 172
    Browser_Refresh = internal_dpg.mvKey_Browser_Refresh  # 168
    Browser_Search = internal_dpg.mvKey_Browser_Search  # 170
    Browser_Stop = internal_dpg.mvKey_Browser_Stop  # 169
    C = internal_dpg.mvKey_C  # 67
    Capital = internal_dpg.mvKey_Capital  # 20
    Clear = internal_dpg.mvKey_Clear  # 12
    Close_Brace = internal_dpg.mvKey_Close_Brace  # 221
    Colon = internal_dpg.mvKey_Colon  # 186
    Comma = internal_dpg.mvKey_Comma  # 188
    Control = internal_dpg.mvKey_Control  # 17
    D = internal_dpg.mvKey_D  # 68
    Decimal = internal_dpg.mvKey_Decimal  # 110
    Delete = internal_dpg.mvKey_Delete  # 46
    Divide = internal_dpg.mvKey_Divide  # 111
    Down = internal_dpg.mvKey_Down  # 40
    E = internal_dpg.mvKey_E  # 69
    End = internal_dpg.mvKey_End  # 35
    Escape = internal_dpg.mvKey_Escape  # 27
    Execute = internal_dpg.mvKey_Execute  # 43
    F = internal_dpg.mvKey_F  # 70
    F1 = internal_dpg.mvKey_F1  # 112
    F10 = internal_dpg.mvKey_F10  # 121
    F11 = internal_dpg.mvKey_F11  # 122
    F12 = internal_dpg.mvKey_F12  # 123
    F13 = internal_dpg.mvKey_F13  # 124
    F14 = internal_dpg.mvKey_F14  # 125
    F15 = internal_dpg.mvKey_F15  # 126
    F16 = internal_dpg.mvKey_F16  # 127
    F17 = internal_dpg.mvKey_F17  # 128
    F18 = internal_dpg.mvKey_F18  # 129
    F19 = internal_dpg.mvKey_F19  # 130
    F2 = internal_dpg.mvKey_F2  # 113
    F20 = internal_dpg.mvKey_F20  # 131
    F21 = internal_dpg.mvKey_F21  # 132
    F22 = internal_dpg.mvKey_F22  # 133
    F23 = internal_dpg.mvKey_F23  # 134
    F24 = internal_dpg.mvKey_F24  # 135
    F25 = internal_dpg.mvKey_F25  # 136
    F3 = internal_dpg.mvKey_F3  # 114
    F4 = internal_dpg.mvKey_F4  # 115
    F5 = internal_dpg.mvKey_F5  # 116
    F6 = internal_dpg.mvKey_F6  # 117
    F7 = internal_dpg.mvKey_F7  # 118
    F8 = internal_dpg.mvKey_F8  # 119
    F9 = internal_dpg.mvKey_F9  # 120
    G = internal_dpg.mvKey_G  # 71
    H = internal_dpg.mvKey_H  # 72
    Help = internal_dpg.mvKey_Help  # 47
    Home = internal_dpg.mvKey_Home  # 36
    I = internal_dpg.mvKey_I  # 73
    Insert = internal_dpg.mvKey_Insert  # 45
    J = internal_dpg.mvKey_J  # 74
    K = internal_dpg.mvKey_K  # 75
    L = internal_dpg.mvKey_L  # 76
    LControl = internal_dpg.mvKey_LControl  # 162
    LMenu = internal_dpg.mvKey_LMenu  # 164
    LShift = internal_dpg.mvKey_LShift  # 160
    LWin = internal_dpg.mvKey_LWin  # 91
    Launch_App1 = internal_dpg.mvKey_Launch_App1  # 182
    Launch_App2 = internal_dpg.mvKey_Launch_App2  # 183
    Launch_Mail = internal_dpg.mvKey_Launch_Mail  # 180
    Launch_Media_Select = internal_dpg.mvKey_Launch_Media_Select  # 181
    Left = internal_dpg.mvKey_Left  # 37
    M = internal_dpg.mvKey_M  # 77
    Media_Next_Track = internal_dpg.mvKey_Media_Next_Track  # 176
    Media_Play_Pause = internal_dpg.mvKey_Media_Play_Pause  # 179
    Media_Prev_Track = internal_dpg.mvKey_Media_Prev_Track  # 177
    Media_Stop = internal_dpg.mvKey_Media_Stop  # 178
    Minus = internal_dpg.mvKey_Minus  # 189
    Multiply = internal_dpg.mvKey_Multiply  # 106
    N = internal_dpg.mvKey_N  # 78
    Next = internal_dpg.mvKey_Next  # 34
    NumLock = internal_dpg.mvKey_NumLock  # 144
    NumPad0 = internal_dpg.mvKey_NumPad0  # 96
    NumPad1 = internal_dpg.mvKey_NumPad1  # 97
    NumPad2 = internal_dpg.mvKey_NumPad2  # 98
    NumPad3 = internal_dpg.mvKey_NumPad3  # 99
    NumPad4 = internal_dpg.mvKey_NumPad4  # 100
    NumPad5 = internal_dpg.mvKey_NumPad5  # 101
    NumPad6 = internal_dpg.mvKey_NumPad6  # 102
    NumPad7 = internal_dpg.mvKey_NumPad7  # 103
    NumPad8 = internal_dpg.mvKey_NumPad8  # 104
    NumPad9 = internal_dpg.mvKey_NumPad9  # 105
    O = internal_dpg.mvKey_O  # 79
    Open_Brace = internal_dpg.mvKey_Open_Brace  # 219
    P = internal_dpg.mvKey_P  # 80
    Pause = internal_dpg.mvKey_Pause  # 19
    Period = internal_dpg.mvKey_Period  # 190
    Plus = internal_dpg.mvKey_Plus  # 187
    Print = internal_dpg.mvKey_Print  # 42
    PrintScreen = internal_dpg.mvKey_PrintScreen  # 44
    Prior = internal_dpg.mvKey_Prior  # 33
    Q = internal_dpg.mvKey_Q  # 81
    Quote = internal_dpg.mvKey_Quote  # 222
    R = internal_dpg.mvKey_R  # 82
    RControl = internal_dpg.mvKey_RControl  # 163
    RMenu = internal_dpg.mvKey_RMenu  # 165
    RShift = internal_dpg.mvKey_RShift  # 161
    RWin = internal_dpg.mvKey_RWin  # 92
    Return = internal_dpg.mvKey_Return  # 13
    Right = internal_dpg.mvKey_Right  # 39
    S = internal_dpg.mvKey_S  # 83
    ScrollLock = internal_dpg.mvKey_ScrollLock  # 145
    Select = internal_dpg.mvKey_Select  # 41
    Separator = internal_dpg.mvKey_Separator  # 108
    Shift = internal_dpg.mvKey_Shift  # 16
    Slash = internal_dpg.mvKey_Slash  # 191
    Sleep = internal_dpg.mvKey_Sleep  # 95
    Spacebar = internal_dpg.mvKey_Spacebar  # 32
    Subtract = internal_dpg.mvKey_Subtract  # 109
    T = internal_dpg.mvKey_T  # 84
    Tab = internal_dpg.mvKey_Tab  # 9
    Tilde = internal_dpg.mvKey_Tilde  # 192
    U = internal_dpg.mvKey_U  # 85
    Up = internal_dpg.mvKey_Up  # 38
    V = internal_dpg.mvKey_V  # 86
    Volume_Down = internal_dpg.mvKey_Volume_Down  # 174
    Volume_Mute = internal_dpg.mvKey_Volume_Mute  # 173
    Volume_Up = internal_dpg.mvKey_Volume_Up  # 175
    W = internal_dpg.mvKey_W  # 87
    X = internal_dpg.mvKey_X  # 88
    Y = internal_dpg.mvKey_Y  # 89
    Z = internal_dpg.mvKey_Z  # 90
    Any = -1


class GlobalHandler(RegistryItem, abc.ABC):

    @property
    def restrict_parents_to(self) -> t.Tuple[t.Type["GlobalHandlerRegistry"]]:
        return GlobalHandlerRegistry, 


class WidgetHandler(RegistryItem, abc.ABC):

    @property
    def restrict_parents_to(self) -> t.Tuple[t.Type["WidgetHandlerRegistry"]]:
        return WidgetHandlerRegistry, 


@dataclasses.dataclass(repr=False)
class HistogramSeries2D(PlotSeries):
    """
    Refer:
    >>> dpg.add_2d_histogram_series

     Adds a 2d histogram series.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # xbins (int, optional): ...
    xbins: int = -1

    # ybins (int, optional): ...
    ybins: int = -1

    # xmin_range (float, optional): ...
    xmin_range: float = 0.0

    # xmax_range (float, optional): ...
    xmax_range: float = 1.0

    # ymin_range (float, optional): ...
    ymin_range: float = 0.0

    # ymax_range (float, optional): ...
    ymax_range: float = 1.0

    # density (bool, optional): ...
    density: bool = False

    # outliers (bool, optional): ...
    outliers: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_2d_histogram_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            xbins=self.xbins,
            ybins=self.ybins,
            xmin_range=self.xmin_range,
            xmax_range=self.xmax_range,
            ymin_range=self.ymin_range,
            ymax_range=self.ymax_range,
            density=self.density,
            outliers=self.outliers,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Slider3D(MovableWidget):
    """
    Refer:
    >>> dpg.add_3d_slider

     Adds a 3D box slider.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    # max_x (float, optional): Applies upper limit to slider.
    max_x: float = 100.0

    # max_y (float, optional): Applies upper limit to slider.
    max_y: float = 100.0

    # max_z (float, optional): Applies upper limit to slider.
    max_z: float = 100.0

    # min_x (float, optional): Applies lower limit to slider.
    min_x: float = 0.0

    # min_y (float, optional): Applies lower limit to slider.
    min_y: float = 0.0

    # min_z (float, optional): Applies lower limit to slider.
    min_z: float = 0.0

    # scale (float, optional): Size of the widget.
    scale: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_3d_slider(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            max_x=self.max_x,
            max_y=self.max_y,
            max_z=self.max_z,
            min_x=self.min_x,
            min_y=self.min_y,
            min_z=self.min_z,
            scale=self.scale,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class AreaSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_area_series

     Adds an area series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # contribute_to_bounds (bool, optional): ...
    contribute_to_bounds: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_area_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            fill=self.fill,
            contribute_to_bounds=self.contribute_to_bounds,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class BarSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_bar_series

     Adds a bar series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # weight (float, optional): ...
    weight: float = 1.0

    # horizontal (bool, optional): ...
    horizontal: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_bar_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            weight=self.weight,
            horizontal=self.horizontal,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class BoolValue(Widget):
    """
    Refer:
    >>> dpg.add_bool_value

     Adds a bool value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (bool, optional): ...
    default_value: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_bool_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Button(MovableWidget):
    """
    Refer:
    >>> dpg.add_button

     Adds a button.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # small (bool, optional): Shrinks the size of the button to the text of the label it contains. Useful for embedding in text.
    small: bool = False

    # arrow (bool, optional): Displays an arrow in place of the text string. This requires the direction keyword.
    arrow: bool = False

    # direction (int, optional): Sets the cardinal direction for the arrow by using constants mvDir_Left, mvDir_Up, mvDir_Down, mvDir_Right, mvDir_None. Arrow keyword must be set to True.
    direction: EnDir = EnDir.Left

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_button(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            small=self.small,
            arrow=self.arrow,
            direction=self.direction.value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class CandleSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_candle_series

     Adds a candle series to a plot.

    """

    # dates (Any): ...
    dates: PLOT_DATA_TYPE

    # opens (Any): ...
    opens: PLOT_DATA_TYPE

    # closes (Any): ...
    closes: PLOT_DATA_TYPE

    # lows (Any): ...
    lows: PLOT_DATA_TYPE

    # highs (Any): ...
    highs: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # bull_color (Union[List[int], Tuple[int, ...]], optional): ...
    bull_color: COLOR_TYPE = (0, 255, 113, 255)

    # bear_color (Union[List[int], Tuple[int, ...]], optional): ...
    bear_color: COLOR_TYPE = (218, 13, 79, 255)

    # weight (float, optional): ...
    weight: float = 0.25

    # tooltip (bool, optional): ...
    tooltip: bool = True

    # time_unit (int, optional): mvTimeUnit_* constants. Default mvTimeUnit_Day.
    time_unit: EnTimeUnit = EnTimeUnit.Day

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_candle_series(
            self.dates,
            self.opens,
            self.closes,
            self.lows,
            self.highs,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            bull_color=self.bull_color,
            bear_color=self.bear_color,
            weight=self.weight,
            tooltip=self.tooltip,
            time_unit=self.time_unit.value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class CheckBox(MovableWidget):
    """
    Refer:
    >>> dpg.add_checkbox

     Adds a checkbox.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (bool, optional): Sets the default value of the checkmark
    default_value: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_checkbox(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ColorButton(MovableWidget):
    """
    Refer:
    >>> dpg.add_color_button

     Adds a color button.

    """

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 255)

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # no_alpha (bool, optional): Removes the displayed slider that can change alpha channel.
    no_alpha: bool = False

    # no_border (bool, optional): Disable border around the image.
    no_border: bool = False

    # no_drag_drop (bool, optional): Disable ability to drag and drop small preview (color square) to apply colors to other items.
    no_drag_drop: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_color_button(
            tag=self.guid,
            parent=_parent_guid,
            default_value=self.default_value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            no_alpha=self.no_alpha,
            no_border=self.no_border,
            no_drag_drop=self.no_drag_drop,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ColorValue(Widget):
    """
    Refer:
    >>> dpg.add_color_value

     Adds a color value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_color_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Colormap(Widget):
    """
    Refer:
    >>> dpg.add_colormap

     Adds a legend that pairs colors with normalized value 0.0->1.0. Each color will be  This is typically used with a heat series. (ex. [[0, 0, 0, 255], [255, 255, 255, 255]] will be mapped to a soft transition from 0.0-1.0)

    """

    # colors (Any): colors that will be mapped to the normalized value 0.0->1.0
    colors: t.List[COLOR_TYPE]

    # qualitative (bool): Qualitative will create hard transitions for color boundries across the value range when enabled.
    qualitative: bool

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_colormap(
            self.colors,
            self.qualitative,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ColormapButton(MovableWidget):
    """
    Refer:
    >>> dpg.add_colormap_button

     Adds a button that a color map can be bound to.

    """

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 255)

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_colormap_button(
            tag=self.guid,
            parent=_parent_guid,
            default_value=self.default_value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ColormapScale(MovableWidget):
    """
    Refer:
    >>> dpg.add_colormap_scale

     Adds a legend that pairs values with colors. This is typically used with a heat series. 

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # colormap (Union[int, str], optional): mvPlotColormap_* constants or mvColorMap uuid from a color map registry
    colormap: EnPlotColormap = EnPlotColormap.Default

    # min_scale (float, optional): Sets the min number of the color scale. Typically is the same as the min scale from the heat series.
    min_scale: float = 0.0

    # max_scale (float, optional): Sets the max number of the color scale. Typically is the same as the max scale from the heat series.
    max_scale: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_colormap_scale(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            colormap=self.colormap.value,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ColormapSlider(MovableWidget):
    """
    Refer:
    >>> dpg.add_colormap_slider

     Adds a color slider that a color map can be bound to.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_colormap_slider(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Combo(MovableWidget):
    """
    Refer:
    >>> dpg.add_combo

     Adds a combo dropdown that allows a user to select a single option from a drop down window. All items will be shown as selectables on the dropdown.

    """

    # items (Union[List[str], Tuple[str, ...]], optional): A tuple of items to be shown in the drop down window. Can consist of any combination of types but will convert all items to strings to be shown.
    items: t.Union[t.List[str], t.Tuple[str, ...]] = ()

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (str, optional): Sets a selected item from the drop down by specifying the string value.
    default_value: str = ''

    # popup_align_left (bool, optional): Align the contents on the popup toward the left.
    popup_align_left: bool = False

    # no_arrow_button (bool, optional): Display the preview box without the square arrow button indicating dropdown activity.
    no_arrow_button: bool = False

    # no_preview (bool, optional): Display only the square arrow button and not the selected value.
    no_preview: bool = False

    # height_mode (int, optional): Controlls the number of items shown in the dropdown by the constants mvComboHeight_Small, mvComboHeight_Regular, mvComboHeight_Large, mvComboHeight_Largest
    height_mode: EnComboHeight = EnComboHeight.Regular

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_combo(
            tag=self.guid,
            parent=_parent_guid,
            items=self.items,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            popup_align_left=self.popup_align_left,
            no_arrow_button=self.no_arrow_button,
            no_preview=self.no_preview,
            height_mode=self.height_mode.value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DatePicker(MovableWidget):
    """
    Refer:
    >>> dpg.add_date_picker

     Adds a data picker.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (dict, optional): ...
    default_value: dict = dataclasses.field(default_factory=lambda: {'month_day': 14, 'year': 20, 'month': 5})

    # level (int, optional): Use avaliable constants. mvDatePickerLevel_Day, mvDatePickerLevel_Month, mvDatePickerLevel_Year
    level: EnDatePickerLevel = EnDatePickerLevel.Day

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_date_picker(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            level=self.level.value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Double4Value(Widget):
    """
    Refer:
    >>> dpg.add_double4_value

     Adds a double value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0, 0.0, 0.0)

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_double4_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DoubleValue(Widget):
    """
    Refer:
    >>> dpg.add_double_value

     Adds a double value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (float, optional): ...
    default_value: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_double_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DragDouble(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_double

     Adds drag for a single double value. Useful when drag float is not accurate enough. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%0.3f'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (float, optional): Applies a limit only to draging entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to draging entry only.
    max_value: float = 100.0

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_double(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DragDoublex(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_doublex

     Adds drag input for a set of double values up to 4. Useful when drag float is not accurate enough. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0, 0.0, 0.0)

    # size (int, optional): Number of doubles to be displayed.
    size: int = 4

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%0.3f'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (float, optional): Applies a limit only to draging entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to draging entry only.
    max_value: float = 100.0

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_doublex(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DragFloat(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_float

     Adds drag for a single float value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%0.3f'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (float, optional): Applies a limit only to draging entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to draging entry only.
    max_value: float = 100.0

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_float(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DragFloatX(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_floatx

     Adds drag input for a set of float values up to 4. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    # size (int, optional): Number of floats to be displayed.
    size: int = 4

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%0.3f'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (float, optional): Applies a limit only to draging entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to draging entry only.
    max_value: float = 100.0

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_floatx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DragInt(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_int

     Adds drag for a single int value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (int, optional): ...
    default_value: int = 0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%d'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (int, optional): Applies a limit only to draging entry only.
    min_value: int = 0

    # max_value (int, optional): Applies a limit only to draging entry only.
    max_value: int = 100

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_int(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class DragIntX(MovableWidget):
    """
    Refer:
    >>> dpg.add_drag_intx

     Adds drag input for a set of int values up to 4. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the drag. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    # size (int, optional): Number of ints to be displayed.
    size: int = 4

    # format (str, optional): Determines the format the int will be displayed as use python string formatting.
    format: str = '%d'

    # speed (float, optional): Sets the sensitivity the float will be modified while dragging.
    speed: float = 1.0

    # min_value (int, optional): Applies a limit only to draging entry only.
    min_value: int = 0

    # max_value (int, optional): Applies a limit only to draging entry only.
    max_value: int = 100

    # no_input (bool, optional): Disable direct entry methods or Enter key allowing to input text directly into the widget.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_intx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            format=self.format,
            speed=self.speed,
            min_value=self.min_value,
            max_value=self.max_value,
            no_input=self.no_input,
            clamped=self.clamped,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class PlotDragLine(PlotItem):
    """
    Refer:
    >>> dpg.add_drag_line

     Adds a drag line to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_value (Any, optional): ...
    default_value: t.Any = 0.0

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # show_label (bool, optional): ...
    show_label: bool = True

    # vertical (bool, optional): ...
    vertical: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_line(
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color,
            thickness=self.thickness,
            show_label=self.show_label,
            vertical=self.vertical,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class PlotDragPoint(PlotItem):
    """
    Refer:
    >>> dpg.add_drag_point

     Adds a drag point to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0)

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # show_label (bool, optional): ...
    show_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_drag_point(
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color,
            thickness=self.thickness,
            show_label=self.show_label,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class DynamicTexture(Widget):
    """
    Refer:
    >>> dpg.add_dynamic_texture

     Adds a dynamic texture.

    """

    # width (int): ...
    width: int

    # height (int): ...
    height: int

    # default_value (Union[List[float], Tuple[float, ...]]): ...
    default_value: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_dynamic_texture(
            self.width,
            self.height,
            self.default_value,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ErrorSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_error_series

     Adds an error series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # negative (Any): ...
    negative: PLOT_DATA_TYPE

    # positive (Any): ...
    positive: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # contribute_to_bounds (bool, optional): ...
    contribute_to_bounds: bool = True

    # horizontal (bool, optional): ...
    horizontal: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_error_series(
            self.x,
            self.y,
            self.negative,
            self.positive,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            contribute_to_bounds=self.contribute_to_bounds,
            horizontal=self.horizontal,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FileExtension(MovableWidget):
    """
    Refer:
    >>> dpg.add_file_extension

     Creates a file extension filter option in the file dialog.

    """

    # extension (str): Extension that will show as an when the parent is a file dialog.
    extension: str

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # custom_text (str, optional): Replaces the displayed text in the drop down for this extension.
    custom_text: str = ''

    # color (Union[List[int], Tuple[int, ...]], optional): Color for the text that will be shown with specified extensions.
    color: COLOR_TYPE = (-255, 0, 0, 255)

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_file_extension(
            self.extension,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            custom_text=self.custom_text,
            color=self.color,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Float4Value(Widget):
    """
    Refer:
    >>> dpg.add_float4_value

     Adds a float4 value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_float4_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FloatValue(Widget):
    """
    Refer:
    >>> dpg.add_float_value

     Adds a float value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (float, optional): ...
    default_value: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_float_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FloatVectValue(Widget):
    """
    Refer:
    >>> dpg.add_float_vect_value

     Adds a float vect value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = ()

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_float_vect_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FontChars(Widget):
    """
    Refer:
    >>> dpg.add_font_chars

     Adds specific font characters to a font.

    """

    # chars (Union[List[int], Tuple[int, ...]]): ...
    chars: t.Union[t.List[int], t.Tuple[int, ...]]

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_font_chars(
            self.chars,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FontRange(Widget):
    """
    Refer:
    >>> dpg.add_font_range

     Adds a range of font characters to a font.

    """

    # first_char (int): ...
    first_char: int

    # last_char (int): ...
    last_char: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_font_range(
            self.first_char,
            self.last_char,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FontRangeHint(Widget):
    """
    Refer:
    >>> dpg.add_font_range_hint

     Adds a range of font characters (mvFontRangeHint_ constants).

    """

    # hint (int): ...
    hint: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_font_range_hint(
            self.hint,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class HeatSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_heat_series

     Adds a heat series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # rows (int): ...
    rows: int

    # cols (int): ...
    cols: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # scale_min (float, optional): Sets the color scale min. Typically paired with the color scale widget scale_min.
    scale_min: float = 0.0

    # scale_max (float, optional): Sets the color scale max. Typically paired with the color scale widget scale_max.
    scale_max: float = 1.0

    # bounds_min (Any, optional): ...
    bounds_min: t.Any = (0.0, 0.0)

    # bounds_max (Any, optional): ...
    bounds_max: t.Any = (1.0, 1.0)

    # format (str, optional): ...
    format: str = '%0.1f'

    # contribute_to_bounds (bool, optional): ...
    contribute_to_bounds: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_heat_series(
            self.x,
            self.rows,
            self.cols,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            scale_min=self.scale_min,
            scale_max=self.scale_max,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            format=self.format,
            contribute_to_bounds=self.contribute_to_bounds,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class HistogramSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_histogram_series

     Adds a histogram series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # bins (int, optional): ...
    bins: int = -1

    # bar_scale (float, optional): ...
    bar_scale: float = 1.0

    # min_range (float, optional): ...
    min_range: float = 0.0

    # max_range (float, optional): ...
    max_range: float = 1.0

    # cumlative (bool, optional): ...
    cumlative: bool = False

    # density (bool, optional): ...
    density: bool = False

    # outliers (bool, optional): ...
    outliers: bool = True

    # contribute_to_bounds (bool, optional): ...
    contribute_to_bounds: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_histogram_series(
            self.x,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            bins=self.bins,
            bar_scale=self.bar_scale,
            min_range=self.min_range,
            max_range=self.max_range,
            cumlative=self.cumlative,
            density=self.density,
            outliers=self.outliers,
            contribute_to_bounds=self.contribute_to_bounds,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class HLineSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_hline_series

     Adds an infinite horizontal line series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_hline_series(
            self.x,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class InputDouble(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_double

     Adds input for an double. Useful when input float is not accurate enough. +/- buttons can be activated by setting the value of step.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    # min_value (float, optional): Value for lower limit of input. By default this limits the step buttons. Use min_clamped to limit manual input.
    min_value: float = 0.0

    # max_value (float, optional): Value for upper limit of input. By default this limits the step buttons. Use max_clamped to limit manual input.
    max_value: float = 100.0

    # step (float, optional): Increment to change value by when the step buttons are pressed. Setting this and step_fast to a value of 0 or less will turn off step buttons.
    step: float = 0.1

    # step_fast (float, optional): Increment to change value by when ctrl + step buttons are pressed. Setting this and step to a value of 0 or less will turn off step buttons.
    step_fast: float = 1.0

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_double(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            min_value=self.min_value,
            max_value=self.max_value,
            step=self.step,
            step_fast=self.step_fast,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputDoublex(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_doublex

     Adds multi double input for up to 4 double values. Useful when input float mulit is not accurate enough.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0, 0.0, 0.0)

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    # min_value (float, optional): Value for lower limit of input for each cell. Use min_clamped to turn on.
    min_value: float = 0.0

    # max_value (float, optional): Value for upper limit of input for each cell. Use max_clamped to turn on.
    max_value: float = 100.0

    # size (int, optional): Number of components displayed for input.
    size: int = 4

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_doublex(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            min_value=self.min_value,
            max_value=self.max_value,
            size=self.size,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputFloat(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_float

     Adds input for an float. +/- buttons can be activated by setting the value of step.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    # min_value (float, optional): Value for lower limit of input. By default this limits the step buttons. Use min_clamped to limit manual input.
    min_value: float = 0.0

    # max_value (float, optional): Value for upper limit of input. By default this limits the step buttons. Use max_clamped to limit manual input.
    max_value: float = 100.0

    # step (float, optional): Increment to change value by when the step buttons are pressed. Setting this and step_fast to a value of 0 or less will turn off step buttons.
    step: float = 0.1

    # step_fast (float, optional): Increment to change value by when ctrl + step buttons are pressed. Setting this and step to a value of 0 or less will turn off step buttons.
    step_fast: float = 1.0

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_float(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            min_value=self.min_value,
            max_value=self.max_value,
            step=self.step,
            step_fast=self.step_fast,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputFloatX(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_floatx

     Adds multi float input for up to 4 float values.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    # min_value (float, optional): Value for lower limit of input for each cell. Use min_clamped to turn on.
    min_value: float = 0.0

    # max_value (float, optional): Value for upper limit of input for each cell. Use max_clamped to turn on.
    max_value: float = 100.0

    # size (int, optional): Number of components displayed for input.
    size: int = 4

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_floatx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            format=self.format,
            min_value=self.min_value,
            max_value=self.max_value,
            size=self.size,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputInt(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_int

     Adds input for an int. +/- buttons can be activated by setting the value of step.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (int, optional): ...
    default_value: int = 0

    # min_value (int, optional): Value for lower limit of input. By default this limits the step buttons. Use min_clamped to limit manual input.
    min_value: int = 0

    # max_value (int, optional): Value for upper limit of input. By default this limits the step buttons. Use max_clamped to limit manual input.
    max_value: int = 100

    # step (int, optional): Increment to change value by when the step buttons are pressed. Setting this and step_fast to a value of 0 or less will turn off step buttons.
    step: int = 1

    # step_fast (int, optional): Increment to change value by when ctrl + step buttons are pressed. Setting this and step to a value of 0 or less will turn off step buttons.
    step_fast: int = 100

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_int(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            min_value=self.min_value,
            max_value=self.max_value,
            step=self.step,
            step_fast=self.step_fast,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputIntX(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_intx

     Adds multi int input for up to 4 integer values.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    # min_value (int, optional): Value for lower limit of input for each cell. Use min_clamped to turn on.
    min_value: int = 0

    # max_value (int, optional): Value for upper limit of input for each cell. Use max_clamped to turn on.
    max_value: int = 100

    # size (int, optional): Number of components displayed for input.
    size: int = 4

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_intx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            min_value=self.min_value,
            max_value=self.max_value,
            size=self.size,
            min_clamped=self.min_clamped,
            max_clamped=self.max_clamped,
            on_enter=self.if_entered,
            readonly=self.readonly,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class InputText(MovableWidget):
    """
    Refer:
    >>> dpg.add_input_text

     Adds input for text.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (str, optional): ...
    default_value: str = ''

    # hint (str, optional): Displayed only when value is an empty string. Will reappear if input value is set to empty string. Will not show if default value is anything other than default empty string.
    hint: str = ''

    # multiline (bool, optional): Allows for multiline text input.
    multiline: bool = False

    # no_spaces (bool, optional): Filter out spaces and tabs.
    no_spaces: bool = False

    # uppercase (bool, optional): Automatically make all inputs uppercase.
    uppercase: bool = False

    # tab_input (bool, optional): Allows tabs to be input into the string value instead of changing item focus.
    tab_input: bool = False

    # decimal (bool, optional): Only allow characters 0123456789.+-*/
    decimal: bool = False

    # hexadecimal (bool, optional): Only allow characters 0123456789ABCDEFabcdef
    hexadecimal: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    # password (bool, optional): Display all input characters as '*'.
    password: bool = False

    # scientific (bool, optional): Only allow characters 0123456789.+-*/eE (Scientific notation input)
    scientific: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_input_text(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            hint=self.hint,
            multiline=self.multiline,
            no_spaces=self.no_spaces,
            uppercase=self.uppercase,
            tab_input=self.tab_input,
            decimal=self.decimal,
            hexadecimal=self.hexadecimal,
            readonly=self.readonly,
            password=self.password,
            scientific=self.scientific,
            on_enter=self.if_entered,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Int4Value(Widget):
    """
    Refer:
    >>> dpg.add_int4_value

     Adds a int4 value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_int4_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class IntValue(Widget):
    """
    Refer:
    >>> dpg.add_int_value

     Adds a int value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (int, optional): ...
    default_value: int = 0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_int_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class WidgetActivatedHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_activated_handler

     Adds a activated handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_activated_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetActiveHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_active_handler

     Adds a active handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_active_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetClickedHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_clicked_handler

     Adds a clicked handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_clicked_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetDeactivatedAfterEditHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_deactivated_after_edit_handler

     Adds a deactivated after edit handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_deactivated_after_edit_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetDeactivatedHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_deactivated_handler

     Adds a deactivated handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_deactivated_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetDoubleClickedHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_double_clicked_handler

     Adds a double click handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_double_clicked_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetEditedHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_edited_handler

     Adds an edited handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_edited_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetFocusHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_focus_handler

     Adds a focus handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_focus_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetHoverHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_hover_handler

     Adds a hover handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_hover_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetResizeHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_resize_handler

     Adds a resize handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_resize_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetToggledOpenHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_toggled_open_handler

     Adds a togged open handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_toggled_open_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class WidgetVisibleHandler(WidgetHandler):
    """
    Refer:
    >>> dpg.add_item_visible_handler

     Adds a visible handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_item_visible_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class KeyDownHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_key_down_handler

     Adds a key down handler.

    """

    # key (int, optional): Submits callback for all keys
    key: EnKey = EnKey.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_key_down_handler(
            tag=self.guid,
            parent=_parent_guid,
            key=self.key.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class KeyPressHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_key_press_handler

     Adds a key press handler.

    """

    # key (int, optional): Submits callback for all keys
    key: EnKey = EnKey.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_key_press_handler(
            tag=self.guid,
            parent=_parent_guid,
            key=self.key.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class KeyReleaseHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_key_release_handler

     Adds a key release handler.

    """

    # key (int, optional): Submits callback for all keys
    key: EnKey = EnKey.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_key_release_handler(
            tag=self.guid,
            parent=_parent_guid,
            key=self.key.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class KnobFloat(MovableWidget):
    """
    Refer:
    >>> dpg.add_knob_float

     Adds a knob that rotates based on change in x mouse position.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # min_value (float, optional): Applies lower limit to value.
    min_value: float = 0.0

    # max_value (float, optional): Applies upper limit to value.
    max_value: float = 100.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_knob_float(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            min_value=self.min_value,
            max_value=self.max_value,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class LineSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_line_series

     Adds a line series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_line_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Listbox(MovableWidget):
    """
    Refer:
    >>> dpg.add_listbox

     Adds a listbox. If height is not large enough to show all items a scroll bar will appear.

    """

    # items (Union[List[str], Tuple[str, ...]], optional): A tuple of items to be shown in the listbox. Can consist of any combination of types. All items will be displayed as strings.
    items: t.Union[t.List[str], t.Tuple[str, ...]] = ()

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (str, optional): String value of the item that will be selected by default.
    default_value: str = ''

    # num_items (int, optional): Expands the height of the listbox to show specified number of items.
    num_items: int = 3

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_listbox(
            tag=self.guid,
            parent=_parent_guid,
            items=self.items,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            num_items=self.num_items,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class LoadingIndicator(MovableWidget):
    """
    Refer:
    >>> dpg.add_loading_indicator

     Adds a rotating animated loading symbol.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # style (int, optional): 0 is rotating dots style, 1 is rotating bar style.
    style: int = 0

    # circle_count (int, optional): Number of dots show if dots or size of circle if circle.
    circle_count: int = 8

    # speed (float, optional): Speed the anamation will rotate.
    speed: float = 1.0

    # radius (float, optional): Radius size of the loading indicator.
    radius: float = 3.0

    # thickness (float, optional): Thickness of the circles or line.
    thickness: float = 1.0

    # color (Union[List[int], Tuple[int, ...]], optional): Color of the growing center circle.
    color: COLOR_TYPE = (51, 51, 55, 255)

    # secondary_color (Union[List[int], Tuple[int, ...]], optional): Background of the dots in dot mode.
    secondary_color: COLOR_TYPE = (29, 151, 236, 103)

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_loading_indicator(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            style=self.style,
            circle_count=self.circle_count,
            speed=self.speed,
            radius=self.radius,
            thickness=self.thickness,
            color=self.color,
            secondary_color=self.secondary_color,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class MenuItem(MovableWidget):
    """
    Refer:
    >>> dpg.add_menu_item

     Adds a menu item to an existing menu. Menu items act similar to selectables and has a bool value. When placed in a menu the checkmark will reflect its value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (bool, optional): This value also controls the checkmark when shown.
    default_value: bool = False

    # shortcut (str, optional): Displays text on the menu item. Typically used to show a shortcut key command.
    shortcut: str = ''

    # check (bool, optional): Displays a checkmark on the menu item when it is selected and placed in a menu.
    check: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_menu_item(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            shortcut=self.shortcut,
            check=self.check,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class MouseClickHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_click_handler

     Adds a mouse click handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_click_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseDoubleClickHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_double_click_handler

     Adds a mouse double click handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_double_click_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseDownHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_down_handler

     Adds a mouse down handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_down_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseDragHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_drag_handler

     Adds a mouse drag handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # threshold (float, optional): The threshold the mouse must be dragged before the callback is ran
    threshold: float = 10.0

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_drag_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            threshold=self.threshold,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseMoveHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_move_handler

     Adds a mouse move handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_move_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseReleaseHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_release_handler

     Adds a mouse release handler.

    """

    # button (int, optional): Submits callback for all mouse buttons
    button: EnMouseButton = EnMouseButton.Any

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_release_handler(
            tag=self.guid,
            parent=_parent_guid,
            button=self.button.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class MouseWheelHandler(GlobalHandler):
    """
    Refer:
    >>> dpg.add_mouse_wheel_handler

     Adds a mouse wheel handler.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_mouse_wheel_handler(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class PieSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_pie_series

     Adds an pie series to a plot.

    """

    # x (float): ...
    x: float

    # y (float): ...
    y: float

    # radius (float): ...
    radius: float

    # values (Any): ...
    values: PLOT_DATA_TYPE

    # labels (Union[List[str], Tuple[str, ...]]): ...
    labels: t.Union[t.List[str], t.Tuple[str, ...]]

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # format (str, optional): ...
    format: str = '%0.2f'

    # angle (float, optional): ...
    angle: float = 90.0

    # normalize (bool, optional): ...
    normalize: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_pie_series(
            self.x,
            self.y,
            self.radius,
            self.values,
            self.labels,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            format=self.format,
            angle=self.angle,
            normalize=self.normalize,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class PlotAnnotation(PlotItem):
    """
    Refer:
    >>> dpg.add_plot_annotation

     Adds an annotation to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0)

    # offset (Union[List[float], Tuple[float, ...]], optional): ...
    offset: PLOT_DATA_TYPE = (0.0, 0.0)

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (0, 0, 0, -255)

    # clamped (bool, optional): ...
    clamped: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_plot_annotation(
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            default_value=self.default_value,
            offset=self.offset,
            color=self.color,
            clamped=self.clamped,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class PlotLegend(Widget):
    """
    Refer:
    >>> dpg.add_plot_legend

     Adds a plot legend to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # location (int, optional): location, mvPlot_Location_*
    location: EnPlotLocation = EnPlotLocation.NorthWest

    # horizontal (bool, optional): ...
    horizontal: bool = False

    # outside (bool, optional): ...
    outside: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_plot_legend(
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            location=self.location.value,
            horizontal=self.horizontal,
            outside=self.outside,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ProgressBar(MovableWidget):
    """
    Refer:
    >>> dpg.add_progress_bar

     Adds a progress bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # overlay (str, optional): Overlayed text onto the bar that typically used to display the value of the progress.
    overlay: str = ''

    # default_value (float, optional): Normalized value to fill the bar from 0.0 to 1.0.
    default_value: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_progress_bar(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            overlay=self.overlay,
            default_value=self.default_value,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class RadioButton(MovableWidget):
    """
    Refer:
    >>> dpg.add_radio_button

     Adds a set of radio buttons. If items keyword is empty, nothing will be shown.

    """

    # items (Union[List[str], Tuple[str, ...]], optional): A tuple of items to be shown as radio options. Can consist of any combination of types. All types will be shown as strings.
    items: t.Union[t.List[str], t.Tuple[str, ...]] = ()

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (str, optional): Default selected radio option. Set by using the string value of the item.
    default_value: str = ''

    # horizontal (bool, optional): Displays the radio options horizontally.
    horizontal: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_radio_button(
            tag=self.guid,
            parent=_parent_guid,
            items=self.items,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            horizontal=self.horizontal,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class RawTexture(Widget):
    """
    Refer:
    >>> dpg.add_raw_texture

     Adds a raw texture.

    """

    # width (int): ...
    width: int

    # height (int): ...
    height: int

    # default_value (Union[List[float], Tuple[float, ...]]): ...
    default_value: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # format (int, optional): Data format.
    format: int = 0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_raw_texture(
            self.width,
            self.height,
            self.default_value,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            format=self.format,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ScatterSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_scatter_series

     Adds a scatter series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_scatter_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Selectable(MovableWidget):
    """
    Refer:
    >>> dpg.add_selectable

     Adds a selectable. Similar to a button but can indicate its selected state.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (bool, optional): ...
    default_value: bool = False

    # span_columns (bool, optional): Forces the selectable to span the width of all columns if placed in a table.
    span_columns: bool = False

    # disable_popup_close (bool, optional): Disable closing a modal or popup window.
    disable_popup_close: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_selectable(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            span_columns=self.span_columns,
            disable_popup_close=self.disable_popup_close,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Separator(MovableWidget):
    """
    Refer:
    >>> dpg.add_separator

     Adds a horizontal line separator.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_separator(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class SeriesValue(Widget):
    """
    Refer:
    >>> dpg.add_series_value

     Adds a plot series value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (Any, optional): ...
    default_value: t.Any = ()

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_series_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ShadeSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_shade_series

     Adds a shade series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y1 (Any): ...
    y1: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # y2 (Any, optional): ...
    y2: t.Any = dataclasses.field(default_factory=lambda: [])

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_shade_series(
            self.x,
            self.y1,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
            y2=self.y2,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class SimplePlot(MovableWidget):
    """
    Refer:
    >>> dpg.add_simple_plot

     Adds a simple plot for visualization of a 1 dimensional set of values.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = ()

    # overlay (str, optional): overlays text (similar to a plot title)
    overlay: str = ''

    # histogram (bool, optional): ...
    histogram: bool = False

    # autosize (bool, optional): ...
    autosize: bool = True

    # min_scale (float, optional): ...
    min_scale: float = 0.0

    # max_scale (float, optional): ...
    max_scale: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_simple_plot(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            overlay=self.overlay,
            histogram=self.histogram,
            autosize=self.autosize,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderDouble(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_double

     Adds slider for a single double value. Useful when slider float is not accurate enough. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # vertical (bool, optional): Sets orientation of the slidebar and slider to vertical.
    vertical: bool = False

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (float, optional): Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_double(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            vertical=self.vertical,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderDoublex(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_doublex

     Adds multi slider for up to 4 double values. Usueful for when multi slide float is not accurate enough. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0, 0.0, 0.0)

    # size (int, optional): Number of doubles to be displayed.
    size: int = 4

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (float, optional): Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # format (str, optional): Determines the format the int will be displayed as use python string formatting.
    format: str = '%.3f'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_doublex(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderFloat(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_float

     Adds slider for a single float value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (float, optional): ...
    default_value: float = 0.0

    # vertical (bool, optional): Sets orientation of the slidebar and slider to vertical.
    vertical: bool = False

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (float, optional): Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # format (str, optional): Determines the format the float will be displayed as use python string formatting.
    format: str = '%.3f'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_float(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            vertical=self.vertical,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderFloatX(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_floatx

     Adds multi slider for up to 4 float values. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: PLOT_DATA_TYPE = (0.0, 0.0, 0.0, 0.0)

    # size (int, optional): Number of floats to be displayed.
    size: int = 4

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (float, optional): Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # max_value (float, optional): Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # format (str, optional): Determines the format the int will be displayed as use python string formatting.
    format: str = '%.3f'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_floatx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderInt(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_int

     Adds slider for a single int value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (int, optional): ...
    default_value: int = 0

    # vertical (bool, optional): Sets orientation of the slidebar and slider to vertical.
    vertical: bool = False

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (int, optional): Applies a limit only to sliding entry only.
    min_value: int = 0

    # max_value (int, optional): Applies a limit only to sliding entry only.
    max_value: int = 100

    # format (str, optional): Determines the format the int will be displayed as use python string formatting.
    format: str = '%d'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_int(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            vertical=self.vertical,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SliderIntX(MovableWidget):
    """
    Refer:
    >>> dpg.add_slider_intx

     Adds multi slider for up to 4 int values. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[int], Tuple[int, ...]], optional): ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    # size (int, optional): Number of ints to be displayed.
    size: int = 4

    # no_input (bool, optional): Disable direct entry methods double-click or ctrl+click or Enter key allowing to input text directly into the item.
    no_input: bool = False

    # clamped (bool, optional): Applies the min and max limits to direct entry methods also such as double click and CTRL+Click.
    clamped: bool = False

    # min_value (int, optional): Applies a limit only to sliding entry only.
    min_value: int = 0

    # max_value (int, optional): Applies a limit only to sliding entry only.
    max_value: int = 100

    # format (str, optional): Determines the format the int will be displayed as use python string formatting.
    format: str = '%d'

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_slider_intx(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            size=self.size,
            no_input=self.no_input,
            clamped=self.clamped,
            min_value=self.min_value,
            max_value=self.max_value,
            format=self.format,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Spacer(MovableWidget):
    """
    Refer:
    >>> dpg.add_spacer

     Adds a spacer item that can be used to help with layouts or can be used as a placeholder item.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_spacer(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class StairSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_stair_series

     Adds a stair series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_stair_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class StaticTexture(Widget):
    """
    Refer:
    >>> dpg.add_static_texture

     Adds a static texture.

    """

    # width (int): ...
    width: int

    # height (int): ...
    height: int

    # default_value (Union[List[float], Tuple[float, ...]]): ...
    default_value: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_static_texture(
            self.width,
            self.height,
            self.default_value,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class StemSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_stem_series

     Adds a stem series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_stem_series(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            indent=self.indent,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class StringValue(Widget):
    """
    Refer:
    >>> dpg.add_string_value

     Adds a string value.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # default_value (str, optional): ...
    default_value: str = ''

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_string_value(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            default_value=self.default_value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TabButton(MovableWidget):
    """
    Refer:
    >>> dpg.add_tab_button

     Adds a tab button to a tab bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # no_reorder (bool, optional): Disable reordering this tab or having another tab cross over this tab. Fixes the position of this tab in relation to the order of neighboring tabs at start.
    no_reorder: bool = False

    # leading (bool, optional): Enforce the tab position to the left of the tab bar (after the tab list popup button).
    leading: bool = False

    # trailing (bool, optional): Enforce the tab position to the right of the tab bar (before the scrolling buttons).
    trailing: bool = False

    # no_tooltip (bool, optional): Disable tooltip for the given tab.
    no_tooltip: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_tab_button(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            no_reorder=self.no_reorder,
            leading=self.leading,
            trailing=self.trailing,
            no_tooltip=self.no_tooltip,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class TableColumn(MovableWidget):
    """
    Refer:
    >>> dpg.add_table_column

     Adds a table column.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # init_width_or_weight (float, optional): ...
    init_width_or_weight: float = 0.0

    # default_hide (bool, optional): Default as a hidden/disabled column.
    default_hide: bool = False

    # default_sort (bool, optional): Default as a sorting column.
    default_sort: bool = False

    # width_stretch (bool, optional): Column will stretch. Preferable with horizontal scrolling disabled (default if table sizing policy is _SizingStretchSame or _SizingStretchProp).
    width_stretch: bool = False

    # width_fixed (bool, optional): Column will not stretch. Preferable with horizontal scrolling enabled (default if table sizing policy is _SizingFixedFit and table is resizable).
    width_fixed: bool = False

    # no_resize (bool, optional): Disable manual resizing.
    no_resize: bool = False

    # no_reorder (bool, optional): Disable manual reordering this column, this will also prevent other columns from crossing over this column.
    no_reorder: bool = False

    # no_hide (bool, optional): Disable ability to hide/disable this column.
    no_hide: bool = False

    # no_clip (bool, optional): Disable clipping for this column (all NoClip columns will render in a same draw command).
    no_clip: bool = False

    # no_sort (bool, optional): Disable ability to sort on this field (even if ImGuiTableFlags_Sortable is set on the table).
    no_sort: bool = False

    # no_sort_ascending (bool, optional): Disable ability to sort in the ascending direction.
    no_sort_ascending: bool = False

    # no_sort_descending (bool, optional): Disable ability to sort in the descending direction.
    no_sort_descending: bool = False

    # no_header_width (bool, optional): Disable header text width contribution to automatic column width.
    no_header_width: bool = False

    # prefer_sort_ascending (bool, optional): Make the initial sort direction Ascending when first sorting on this column (default).
    prefer_sort_ascending: bool = True

    # prefer_sort_descending (bool, optional): Make the initial sort direction Descending when first sorting on this column.
    prefer_sort_descending: bool = False

    # indent_enable (bool, optional): Use current Indent value when entering cell (default for column 0).
    indent_enable: bool = False

    # indent_disable (bool, optional): Ignore current Indent value when entering cell (default for columns > 0). Indentation changes _within_ the cell will still be honored.
    indent_disable: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_table_column(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            show=self.show,
            enabled=self.enabled,
            init_width_or_weight=self.init_width_or_weight,
            default_hide=self.default_hide,
            default_sort=self.default_sort,
            width_stretch=self.width_stretch,
            width_fixed=self.width_fixed,
            no_resize=self.no_resize,
            no_reorder=self.no_reorder,
            no_hide=self.no_hide,
            no_clip=self.no_clip,
            no_sort=self.no_sort,
            no_sort_ascending=self.no_sort_ascending,
            no_sort_descending=self.no_sort_descending,
            no_header_width=self.no_header_width,
            prefer_sort_ascending=self.prefer_sort_ascending,
            prefer_sort_descending=self.prefer_sort_descending,
            indent_enable=self.indent_enable,
            indent_disable=self.indent_disable,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Text(MovableWidget):
    """
    Refer:
    >>> dpg.add_text

     Adds text. Text can have an optional label that will display to the right of the text.

    """

    # default_value (str, optional): ...
    default_value: str = ''

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # wrap (int, optional): Number of pixels from the start of the item until wrapping starts.
    wrap: int = -1

    # bullet (bool, optional): Places a bullet to the left of the text.
    bullet: bool = False

    # color (Union[List[int], Tuple[int, ...]], optional): Color of the text (rgba).
    color: COLOR_TYPE = (-255, 0, 0, 255)

    # show_label (bool, optional): Displays the label to the right of the text.
    show_label: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_text(
            tag=self.guid,
            parent=_parent_guid,
            default_value=self.default_value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            source=_source_guid,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            wrap=self.wrap,
            bullet=self.bullet,
            color=self.color,
            show_label=self.show_label,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class TextPoint(MovableWidget):
    """
    Refer:
    >>> dpg.add_text_point

     Adds a label series to a plot.

    """

    # x (float): ...
    x: float

    # y (float): ...
    y: float

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # x_offset (int, optional): ...
    x_offset: int = Ellipsis

    # y_offset (int, optional): ...
    y_offset: int = Ellipsis

    # vertical (bool, optional): ...
    vertical: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_text_point(
            self.x,
            self.y,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            show=self.show,
            x_offset=self.x_offset,
            y_offset=self.y_offset,
            vertical=self.vertical,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ThemeColor(Widget):
    """
    Refer:
    >>> dpg.add_theme_color

     Adds a theme color.

    """

    # target (int, optional): ...
    target: int = 0

    # value (Union[List[int], Tuple[int, ...]], optional): ...
    value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 255)

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # category (int, optional): Options include mvThemeCat_Core, mvThemeCat_Plots, mvThemeCat_Nodes.
    category: EnThemeCat = EnThemeCat.Core

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_theme_color(
            tag=self.guid,
            parent=_parent_guid,
            target=self.target,
            value=self.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            category=self.category.value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ThemeStyle(Widget):
    """
    Refer:
    >>> dpg.add_theme_style

     Adds a theme style.

    """

    # target (int, optional): ...
    target: int = 0

    # x (float, optional): ...
    x: float = 1.0

    # y (float, optional): ...
    y: float = -1.0

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # category (int, optional): Options include mvThemeCat_Core, mvThemeCat_Plots, mvThemeCat_Nodes.
    category: EnThemeCat = EnThemeCat.Core

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_theme_style(
            tag=self.guid,
            parent=_parent_guid,
            target=self.target,
            x=self.x,
            y=self.y,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            category=self.category.value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TimePicker(MovableWidget):
    """
    Refer:
    >>> dpg.add_time_picker

     Adds a time picker.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (dict, optional): ...
    default_value: dict = dataclasses.field(default_factory=lambda: {'hour': 14, 'min': 32, 'sec': 23})

    # hour24 (bool, optional): Show 24 hour clock instead of 12 hour.
    hour24: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_time_picker(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_value=self.default_value,
            hour24=self.hour24,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class VLineSeries(PlotSeries):
    """
    Refer:
    >>> dpg.add_vline_series

     Adds an infinite vertical line series to a plot.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_vline_series(
            self.x,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            source=_source_guid,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ChildWindow(MovableContainerWidget):
    """
    Refer:
    >>> dpg.child_window

     Adds an embedded child window. Will show scrollbars when items do not fit.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # border (bool, optional): Shows/Hides the border around the sides.
    border: bool = True

    # autosize_x (bool, optional): Autosize the window to its parents size in x.
    autosize_x: bool = False

    # autosize_y (bool, optional): Autosize the window to its parents size in y.
    autosize_y: bool = False

    # no_scrollbar (bool, optional): Disable scrollbars (window can still scroll with mouse or programmatically).
    no_scrollbar: bool = False

    # horizontal_scrollbar (bool, optional): Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    # menubar (bool, optional): Shows/Hides the menubar at the top.
    menubar: bool = False

    # no_scroll_with_mouse (bool, optional): Disable user vertically scrolling with mouse wheel.
    no_scroll_with_mouse: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_child_window(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            border=self.border,
            autosize_x=self.autosize_x,
            autosize_y=self.autosize_y,
            no_scrollbar=self.no_scrollbar,
            horizontal_scrollbar=self.horizontal_scrollbar,
            menubar=self.menubar,
            no_scroll_with_mouse=self.no_scroll_with_mouse,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class Clipper(MovableContainerWidget):
    """
    Refer:
    >>> dpg.clipper

     Helper to manually clip large list of items. Increases performance by not searching or drawing widgets outside of the clipped region.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_clipper(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            show=self.show,
            delay_search=self.delay_search,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class CollapsingHeader(MovableContainerWidget):
    """
    Refer:
    >>> dpg.collapsing_header

     Adds a collapsing header to add items to. Must be closed with the end command.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # closable (bool, optional): Adds the ability to hide this widget by pressing the (x) in the top right of widget.
    closable: bool = False

    # default_open (bool, optional): Sets the collapseable header open by default.
    default_open: bool = False

    # open_on_double_click (bool, optional): Need double-click to open node.
    open_on_double_click: bool = False

    # open_on_arrow (bool, optional): Only open when clicking on the arrow part.
    open_on_arrow: bool = False

    # leaf (bool, optional): No collapsing, no arrow (use as a convenience for leaf nodes).
    leaf: bool = False

    # bullet (bool, optional): Display a bullet instead of arrow.
    bullet: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_collapsing_header(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            closable=self.closable,
            default_open=self.default_open,
            open_on_double_click=self.open_on_double_click,
            open_on_arrow=self.open_on_arrow,
            leaf=self.leaf,
            bullet=self.bullet,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ColormapRegistry(Registry):
    """
    Refer:
    >>> dpg.colormap_registry

     Adds a colormap registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = False

    def build(self) -> int:

        _ret = internal_dpg.add_colormap_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class CustomSeries(MovableContainerWidget):
    """
    Refer:
    >>> dpg.custom_series

     Adds a custom series to a plot. New in 1.6.

    """

    # x (Any): ...
    x: PLOT_DATA_TYPE

    # y (Any): ...
    y: PLOT_DATA_TYPE

    # channel_count (int): ...
    channel_count: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # y1 (Any, optional): ...
    y1: t.Any = dataclasses.field(default_factory=lambda: [])

    # y2 (Any, optional): ...
    y2: t.Any = dataclasses.field(default_factory=lambda: [])

    # y3 (Any, optional): ...
    y3: t.Any = dataclasses.field(default_factory=lambda: [])

    # tooltip (bool, optional): Show tooltip when plot is hovered.
    tooltip: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_custom_series(
            self.x,
            self.y,
            self.channel_count,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=_source_guid,
            callback=self.callback_fn,
            show=self.show,
            y1=self.y1,
            y2=self.y2,
            y3=self.y3,
            tooltip=self.tooltip,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class DragPayload(ContainerWidget):
    """
    Refer:
    >>> dpg.drag_payload

     User data payload for drag and drop operations.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # drag_data (Any, optional): Drag data
    drag_data: t.Any = None

    # drop_data (Any, optional): Drop data
    drop_data: t.Any = None

    # payload_type (str, optional): ...
    payload_type: str = '$$DPG_PAYLOAD'

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_drag_payload(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            drag_data=self.drag_data,
            drop_data=self.drop_data,
            payload_type=self.payload_type,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawArrow(MovableWidget):
    """
    Refer:
    >>> dpg.draw_arrow

     Adds an arrow.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): Arrow tip.
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): Arrow tail.
    p2: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # size (int, optional): ...
    size: int = 4

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_arrow(
            self.p1,
            self.p2,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            thickness=self.thickness,
            size=self.size,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawBezierCubic(MovableWidget):
    """
    Refer:
    >>> dpg.draw_bezier_cubic

     Adds a cubic bezier curve.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): First point in curve.
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): Second point in curve.
    p2: PLOT_DATA_TYPE

    # p3 (Union[List[float], Tuple[float, ...]]): Third point in curve.
    p3: PLOT_DATA_TYPE

    # p4 (Union[List[float], Tuple[float, ...]]): Fourth point in curve.
    p4: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # segments (int, optional): Number of segments to approximate bezier curve.
    segments: int = 0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_bezier_cubic(
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            thickness=self.thickness,
            segments=self.segments,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawBezierQuadratic(MovableWidget):
    """
    Refer:
    >>> dpg.draw_bezier_quadratic

     Adds a quadratic bezier curve.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): First point in curve.
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): Second point in curve.
    p2: PLOT_DATA_TYPE

    # p3 (Union[List[float], Tuple[float, ...]]): Third point in curve.
    p3: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # segments (int, optional): Number of segments to approximate bezier curve.
    segments: int = 0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_bezier_quadratic(
            self.p1,
            self.p2,
            self.p3,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            thickness=self.thickness,
            segments=self.segments,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawCircle(MovableWidget):
    """
    Refer:
    >>> dpg.draw_circle

     Adds a circle

    """

    # center (Union[List[float], Tuple[float, ...]]): ...
    center: PLOT_DATA_TYPE

    # radius (float): ...
    radius: float

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # segments (int, optional): Number of segments to approximate circle.
    segments: int = 0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_circle(
            self.center,
            self.radius,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            fill=self.fill,
            thickness=self.thickness,
            segments=self.segments,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawEllipse(MovableWidget):
    """
    Refer:
    >>> dpg.draw_ellipse

     Adds an ellipse.

    """

    # pmin (Union[List[float], Tuple[float, ...]]): Min point of bounding rectangle.
    pmin: PLOT_DATA_TYPE

    # pmax (Union[List[float], Tuple[float, ...]]): Max point of bounding rectangle.
    pmax: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # segments (int, optional): Number of segments to approximate bezier curve.
    segments: int = 32

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_ellipse(
            self.pmin,
            self.pmax,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            fill=self.fill,
            thickness=self.thickness,
            segments=self.segments,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawLayer(MovableContainerWidget):
    """
    Refer:
    >>> dpg.draw_layer

     New in 1.1. Creates a layer useful for grouping drawlist items.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # perspective_divide (bool, optional): New in 1.1. apply perspective divide
    perspective_divide: bool = False

    # depth_clipping (bool, optional): New in 1.1. apply depth clipping
    depth_clipping: bool = False

    # cull_mode (int, optional): New in 1.1. culling mode, mvCullMode_* constants. Only works with triangles currently.
    cull_mode: EnCullMode = EnCullMode.NONE

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_draw_layer(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            perspective_divide=self.perspective_divide,
            depth_clipping=self.depth_clipping,
            cull_mode=self.cull_mode.value,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawLine(MovableWidget):
    """
    Refer:
    >>> dpg.draw_line

     Adds a line.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): Start of line.
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): End of line.
    p2: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_line(
            self.p1,
            self.p2,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawNode(MovableContainerWidget):
    """
    Refer:
    >>> dpg.draw_node

     New in 1.1. Creates a drawing node to associate a transformation matrix. Child node matricies will concatenate.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_draw_node(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawPolygon(MovableWidget):
    """
    Refer:
    >>> dpg.draw_polygon

     Adds a polygon.

    """

    # points (List[List[float]]): ...
    points: t.List[t.List[float]]

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_polygon(
            self.points,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            fill=self.fill,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawPolyline(MovableWidget):
    """
    Refer:
    >>> dpg.draw_polyline

     Adds a polyline.

    """

    # points (List[List[float]]): ...
    points: t.List[t.List[float]]

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # closed (bool, optional): Will close the polyline by returning to the first point.
    closed: bool = False

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_polyline(
            self.points,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            closed=self.closed,
            color=self.color,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawQuad(MovableWidget):
    """
    Refer:
    >>> dpg.draw_quad

     Adds a quad.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): ...
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): ...
    p2: PLOT_DATA_TYPE

    # p3 (Union[List[float], Tuple[float, ...]]): ...
    p3: PLOT_DATA_TYPE

    # p4 (Union[List[float], Tuple[float, ...]]): ...
    p4: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_quad(
            self.p1,
            self.p2,
            self.p3,
            self.p4,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            fill=self.fill,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawRectangle(MovableWidget):
    """
    Refer:
    >>> dpg.draw_rectangle

     Adds a rectangle.

    """

    # pmin (Union[List[float], Tuple[float, ...]]): Min point of bounding rectangle.
    pmin: PLOT_DATA_TYPE

    # pmax (Union[List[float], Tuple[float, ...]]): Max point of bounding rectangle.
    pmax: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # color_upper_left (Union[List[int], Tuple[int, ...]], optional): 'multicolor' must be set to 'True'
    color_upper_left: COLOR_TYPE = (255, 255, 255, 255)

    # color_upper_right (Union[List[int], Tuple[int, ...]], optional): 'multicolor' must be set to 'True'
    color_upper_right: COLOR_TYPE = (255, 255, 255, 255)

    # color_bottom_right (Union[List[int], Tuple[int, ...]], optional): 'multicolor' must be set to 'True'
    color_bottom_right: COLOR_TYPE = (255, 255, 255, 255)

    # color_bottom_left (Union[List[int], Tuple[int, ...]], optional): 'multicolor' must be set to 'True'
    color_bottom_left: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # multicolor (bool, optional): ...
    multicolor: bool = False

    # rounding (float, optional): Number of pixels of the radius that will round the corners of the rectangle. Note
    rounding: float = 0.0

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_rectangle(
            self.pmin,
            self.pmax,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            color_upper_left=self.color_upper_left,
            color_upper_right=self.color_upper_right,
            color_bottom_right=self.color_bottom_right,
            color_bottom_left=self.color_bottom_left,
            fill=self.fill,
            multicolor=self.multicolor,
            rounding=self.rounding,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawText(MovableWidget):
    """
    Refer:
    >>> dpg.draw_text

     Adds text (drawlist).

    """

    # pos (Union[List[float], Tuple[float, ...]]): Top left point of bounding text rectangle.
    pos: PLOT_DATA_TYPE

    # text (str): Text to draw.
    text: str

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # size (float, optional): ...
    size: float = 10.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_text(
            self.pos,
            self.text,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            size=self.size,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawTriangle(MovableWidget):
    """
    Refer:
    >>> dpg.draw_triangle

     Adds a triangle.

    """

    # p1 (Union[List[float], Tuple[float, ...]]): ...
    p1: PLOT_DATA_TYPE

    # p2 (Union[List[float], Tuple[float, ...]]): ...
    p2: PLOT_DATA_TYPE

    # p3 (Union[List[float], Tuple[float, ...]]): ...
    p3: PLOT_DATA_TYPE

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: COLOR_TYPE = (255, 255, 255, 255)

    # fill (Union[List[int], Tuple[int, ...]], optional): ...
    fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.draw_triangle(
            self.p1,
            self.p2,
            self.p3,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            color=self.color,
            fill=self.fill,
            thickness=self.thickness,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class DrawList(MovableContainerWidget):
    """
    Refer:
    >>> dpg.drawlist

     Adds a drawing canvas.

    """

    # width (int): ...
    width: int

    # height (int): ...
    height: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_drawlist(
            self.width,
            self.height,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class FileDialog(ContainerWidget):
    """
    Refer:
    >>> dpg.file_dialog

     Displays a file or directory selector depending on keywords. Displays a file dialog by default. Callback will be ran when the file or directory picker is closed. The app_data arguemnt will be populated with information related to the file and directory as a dictionary.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_path (str, optional): Path that the file dialog will default to when opened.
    default_path: str = ''

    # default_filename (str, optional): Default name that will show in the file name input.
    default_filename: str = '.'

    # file_count (int, optional): Number of visible files in the dialog.
    file_count: int = 0

    # modal (bool, optional): Forces user interaction with the file selector.
    modal: bool = False

    # directory_selector (bool, optional): Shows only directory/paths as options. Allows selection of directory/paths only.
    directory_selector: bool = False

    # min_size (Union[List[int], Tuple[int, ...]], optional): Minimum window size.
    min_size: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [100, 100])

    # max_size (Union[List[int], Tuple[int, ...]], optional): Maximum window size.
    max_size: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [30000, 30000])

    # cancel_callback (Callable, optional): Callback called when cancel button is clicked.
    cancel_callback: t.Union[Callback, t.Callable] = None

    def build(self) -> int:

        _ret = internal_dpg.add_file_dialog(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            callback=self.callback_fn,
            show=self.show,
            default_path=self.default_path,
            default_filename=self.default_filename,
            file_count=self.file_count,
            modal=self.modal,
            directory_selector=self.directory_selector,
            min_size=self.min_size,
            max_size=self.max_size,
            cancel_callback=self.cancel_callback_fn,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def cancel_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.cancel_callback is None:
            return None
        elif isinstance(self.cancel_callback, Callback):
            return self.cancel_callback.fn(sender=self)
        else:
            return self.cancel_callback()


@dataclasses.dataclass(repr=False)
class FilterSet(MovableContainerWidget):
    """
    Refer:
    >>> dpg.filter_set

     Helper to parse and apply text filters (e.g. aaaaa[, bbbbb][, ccccc])

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_filter_set(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            show=self.show,
            delay_search=self.delay_search,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Font(ContainerWidget):
    """
    Refer:
    >>> dpg.font

     Adds font to a font registry.

    """

    # file (str): ...
    file: str

    # size (int): ...
    size: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # pixel_snapH (bool, optional): Align every glyph to pixel boundary. Useful e.g. if you are merging a non-pixel aligned font with the default font, or rendering text piece-by-piece (e.g. for coloring).
    pixel_snapH: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_font(
            self.file,
            self.size,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            pixel_snapH=self.pixel_snapH,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class FontRegistry(Registry):
    """
    Refer:
    >>> dpg.font_registry

     Adds a font registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    def build(self) -> int:

        _ret = internal_dpg.add_font_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Group(MovableContainerWidget):
    """
    Refer:
    >>> dpg.group

     Creates a group that other widgets can belong to. The group allows item commands to be issued for all of its members.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # horizontal (bool, optional): Forces child widgets to be added in a horizontal layout.
    horizontal: bool = False

    # horizontal_spacing (float, optional): Spacing for the horizontal layout.
    horizontal_spacing: float = -1

    # xoffset (float, optional): Offset from containing window x item location within group.
    xoffset: float = 0.0

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_group(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            horizontal=self.horizontal,
            horizontal_spacing=self.horizontal_spacing,
            xoffset=self.xoffset,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class GlobalHandlerRegistry(Registry):
    """
    Refer:
    >>> dpg.handler_registry

     Adds a handler registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type["GlobalHandler", ]]:
        return GlobalHandler, 

    def build(self) -> int:

        _ret = internal_dpg.add_handler_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class WidgetHandlerRegistry(Registry):
    """
    Refer:
    >>> dpg.item_handler_registry

     Adds an item handler registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type["WidgetHandler", ]]:
        return WidgetHandler, 

    def build(self) -> int:

        _ret = internal_dpg.add_item_handler_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Menu(MovableContainerWidget):
    """
    Refer:
    >>> dpg.menu

     Adds a menu to an existing menu bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_menu(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class MenuBar(ContainerWidget):
    """
    Refer:
    >>> dpg.menu_bar

     Adds a menu bar to a window.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_menu_bar(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            show=self.show,
            delay_search=self.delay_search,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Node(MovableContainerWidget):
    """
    Refer:
    >>> dpg.node

     Adds a node to a node editor.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # draggable (bool, optional): Allow node to be draggable.
    draggable: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_node(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            draggable=self.draggable,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class NodeAttribute(MovableContainerWidget):
    """
    Refer:
    >>> dpg.node_attribute

     Adds a node attribute to a node.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # attribute_type (int, optional): mvNode_Attr_Input, mvNode_Attr_Output, or mvNode_Attr_Static.
    attribute_type: EnNodeAttr = EnNodeAttr.Input

    # shape (int, optional): Pin shape.
    shape: int = 1

    # category (str, optional): Category
    category: str = 'general'

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_node_attribute(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            show=self.show,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            attribute_type=self.attribute_type.value,
            shape=self.shape,
            category=self.category,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Plot(MovableContainerWidget):
    """
    Refer:
    >>> dpg.plot

     Adds a plot which is used to hold series, and can be drawn to with draw commands.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # no_title (bool, optional): the plot title will not be displayed
    no_title: bool = False

    # no_menus (bool, optional): the user will not be able to open context menus with right-click
    no_menus: bool = False

    # no_box_select (bool, optional): the user will not be able to box-select with right-click drag
    no_box_select: bool = False

    # no_mouse_pos (bool, optional): the mouse position, in plot coordinates, will not be displayed inside of the plot
    no_mouse_pos: bool = False

    # no_highlight (bool, optional): plot items will not be highlighted when their legend entry is hovered
    no_highlight: bool = False

    # no_child (bool, optional): a child window region will not be used to capture mouse scroll (can boost performance for single ImGui window applications)
    no_child: bool = False

    # query (bool, optional): the user will be able to draw query rects with middle - mouse or CTRL + right - click drag
    query: bool = False

    # crosshairs (bool, optional): the default mouse cursor will be replaced with a crosshair when hovered
    crosshairs: bool = False

    # anti_aliased (bool, optional): plot lines will be software anti-aliased (not recommended for high density plots, prefer MSAA)
    anti_aliased: bool = False

    # equal_aspects (bool, optional): primary x and y axes will be constrained to have the same units/pixel (does not apply to auxiliary y-axes)
    equal_aspects: bool = False

    # use_local_time (bool, optional): axis labels will be formatted for your timezone when
    use_local_time: bool = False

    # use_ISO8601 (bool, optional): dates will be formatted according to ISO 8601 where applicable (e.g. YYYY-MM-DD, YYYY-MM, --MM-DD, etc.)
    use_ISO8601: bool = False

    # use_24hour_clock (bool, optional): times will be formatted using a 24 hour clock
    use_24hour_clock: bool = False

    # pan_button (int, optional): enables panning when held
    pan_button: int = 0

    # pan_mod (int, optional): optional modifier that must be held for panning
    pan_mod: int = -1

    # fit_button (int, optional): fits visible data when double clicked
    fit_button: int = 0

    # context_menu_button (int, optional): opens plot context menu (if enabled) when clicked
    context_menu_button: int = 1

    # box_select_button (int, optional): begins box selection when pressed and confirms selection when released
    box_select_button: int = 1

    # box_select_mod (int, optional): begins box selection when pressed and confirms selection when released
    box_select_mod: int = -1

    # box_select_cancel_button (int, optional): cancels active box selection when pressed
    box_select_cancel_button: int = 0

    # query_button (int, optional): begins query selection when pressed and end query selection when released
    query_button: int = 2

    # query_mod (int, optional): optional modifier that must be held for query selection
    query_mod: int = -1

    # query_toggle_mod (int, optional): when held, active box selections turn into queries
    query_toggle_mod: int = 17

    # horizontal_mod (int, optional): expands active box selection/query horizontally to plot edge when held
    horizontal_mod: int = 18

    # vertical_mod (int, optional): expands active box selection/query vertically to plot edge when held
    vertical_mod: int = 16

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_plot(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            no_title=self.no_title,
            no_menus=self.no_menus,
            no_box_select=self.no_box_select,
            no_mouse_pos=self.no_mouse_pos,
            no_highlight=self.no_highlight,
            no_child=self.no_child,
            query=self.query,
            crosshairs=self.crosshairs,
            anti_aliased=self.anti_aliased,
            equal_aspects=self.equal_aspects,
            use_local_time=self.use_local_time,
            use_ISO8601=self.use_ISO8601,
            use_24hour_clock=self.use_24hour_clock,
            pan_button=self.pan_button,
            pan_mod=self.pan_mod,
            fit_button=self.fit_button,
            context_menu_button=self.context_menu_button,
            box_select_button=self.box_select_button,
            box_select_mod=self.box_select_mod,
            box_select_cancel_button=self.box_select_cancel_button,
            query_button=self.query_button,
            query_mod=self.query_mod,
            query_toggle_mod=self.query_toggle_mod,
            horizontal_mod=self.horizontal_mod,
            vertical_mod=self.vertical_mod,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class PlotXAxis(Widget):
    """
    Refer:
    >>> dpg.plot_axis

     Adds an axis to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # no_gridlines (bool, optional): ...
    no_gridlines: bool = False

    # no_tick_marks (bool, optional): ...
    no_tick_marks: bool = False

    # no_tick_labels (bool, optional): ...
    no_tick_labels: bool = False

    # log_scale (bool, optional): ...
    log_scale: bool = False

    # invert (bool, optional): ...
    invert: bool = False

    # lock_min (bool, optional): ...
    lock_min: bool = False

    # lock_max (bool, optional): ...
    lock_max: bool = False

    # time (bool, optional): ...
    time: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_plot_axis(
            dpg.mvXAxis,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            no_gridlines=self.no_gridlines,
            no_tick_marks=self.no_tick_marks,
            no_tick_labels=self.no_tick_labels,
            log_scale=self.log_scale,
            invert=self.invert,
            lock_min=self.lock_min,
            lock_max=self.lock_max,
            time=self.time,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class PlotYAxis(ContainerWidget):
    """
    Refer:
    >>> dpg.plot_axis

     Adds an axis to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # no_gridlines (bool, optional): ...
    no_gridlines: bool = False

    # no_tick_marks (bool, optional): ...
    no_tick_marks: bool = False

    # no_tick_labels (bool, optional): ...
    no_tick_labels: bool = False

    # log_scale (bool, optional): ...
    log_scale: bool = False

    # invert (bool, optional): ...
    invert: bool = False

    # lock_min (bool, optional): ...
    lock_min: bool = False

    # lock_max (bool, optional): ...
    lock_max: bool = False

    # time (bool, optional): ...
    time: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_plot_axis(
            dpg.mvYAxis,
            tag=self.guid,
            parent=_parent_guid,
            use_internal_label=False,
            label=None if self.label is None else self.label.split('#')[0],
            user_data=self.user_data,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            no_gridlines=self.no_gridlines,
            no_tick_marks=self.no_tick_marks,
            no_tick_labels=self.no_tick_labels,
            log_scale=self.log_scale,
            invert=self.invert,
            lock_min=self.lock_min,
            lock_max=self.lock_max,
            time=self.time,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class SubPlots(MovableContainerWidget):
    """
    Refer:
    >>> dpg.subplots

     Adds a collection of plots.

    """

    # rows (int): ...
    rows: int

    # columns (int): ...
    columns: int

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # row_ratios (Union[List[float], Tuple[float, ...]], optional): ...
    row_ratios: PLOT_DATA_TYPE = dataclasses.field(default_factory=lambda: [])

    # column_ratios (Union[List[float], Tuple[float, ...]], optional): ...
    column_ratios: PLOT_DATA_TYPE = dataclasses.field(default_factory=lambda: [])

    # no_title (bool, optional): ...
    no_title: bool = False

    # no_menus (bool, optional): the user will not be able to open context menus with right-click
    no_menus: bool = False

    # no_resize (bool, optional): resize splitters between subplot cells will be not be provided
    no_resize: bool = False

    # no_align (bool, optional): subplot edges will not be aligned vertically or horizontally
    no_align: bool = False

    # link_rows (bool, optional): link the y-axis limits of all plots in each row (does not apply auxiliary y-axes)
    link_rows: bool = False

    # link_columns (bool, optional): link the x-axis limits of all plots in each column
    link_columns: bool = False

    # link_all_x (bool, optional): link the x-axis limits in every plot in the subplot
    link_all_x: bool = False

    # link_all_y (bool, optional): link the y-axis limits in every plot in the subplot (does not apply to auxiliary y-axes)
    link_all_y: bool = False

    # column_major (bool, optional): subplots are added in column major order instead of the default row major order
    column_major: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_subplots(
            self.rows,
            self.columns,
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            row_ratios=self.row_ratios,
            column_ratios=self.column_ratios,
            no_title=self.no_title,
            no_menus=self.no_menus,
            no_resize=self.no_resize,
            no_align=self.no_align,
            link_rows=self.link_rows,
            link_columns=self.link_columns,
            link_all_x=self.link_all_x,
            link_all_y=self.link_all_y,
            column_major=self.column_major,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class Tab(MovableContainerWidget):
    """
    Refer:
    >>> dpg.tab

     Adds a tab to a tab bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # closable (bool, optional): Creates a button on the tab that can hide the tab.
    closable: bool = False

    # no_tooltip (bool, optional): Disable tooltip for the given tab.
    no_tooltip: bool = False

    # order_mode (bool, optional): set using a constant
    order_mode: bool = 0

    @property
    def restrict_parents_to(self) -> t.Tuple[t.Type["TabBar", ]]:
        return TabBar, 

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_tab(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            closable=self.closable,
            no_tooltip=self.no_tooltip,
            order_mode=self.order_mode,
        )
        
        return _ret

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class TabBar(MovableContainerWidget):
    """
    Refer:
    >>> dpg.tab_bar

     Adds a tab bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # reorderable (bool, optional): Allows for the user to change the order of the tabs.
    reorderable: bool = False

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type["Tab", ]]:
        return Tab, 

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_tab_bar(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            reorderable=self.reorderable,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class Table(MovableContainerWidget):
    """
    Refer:
    >>> dpg.table

     Adds a table.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # header_row (bool, optional): show headers at the top of the columns
    header_row: bool = True

    # clipper (bool, optional): Use clipper (rows must be same height).
    clipper: bool = False

    # inner_width (int, optional): ...
    inner_width: int = 0

    # policy (int, optional): ...
    policy: int = 0

    # freeze_rows (int, optional): ...
    freeze_rows: int = 0

    # freeze_columns (int, optional): ...
    freeze_columns: int = 0

    # sort_multi (bool, optional): Hold shift when clicking headers to sort on multiple column.
    sort_multi: bool = False

    # sort_tristate (bool, optional): Allow no sorting, disable default sorting.
    sort_tristate: bool = False

    # resizable (bool, optional): Enable resizing columns
    resizable: bool = False

    # reorderable (bool, optional): Enable reordering columns in header row (need calling TableSetupColumn() + TableHeadersRow() to display headers)
    reorderable: bool = False

    # hideable (bool, optional): Enable hiding/disabling columns in context menu.
    hideable: bool = False

    # sortable (bool, optional): Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
    sortable: bool = False

    # context_menu_in_body (bool, optional): Right-click on columns body/contents will display table context menu. By default it is available in TableHeadersRow().
    context_menu_in_body: bool = False

    # row_background (bool, optional): Set each RowBg color with ImGuiCol_TableRowBg or ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with ImGuiTableBgFlags_RowBg0 on each row manually)
    row_background: bool = False

    # borders_innerH (bool, optional): Draw horizontal borders between rows.
    borders_innerH: bool = False

    # borders_outerH (bool, optional): Draw horizontal borders at the top and bottom.
    borders_outerH: bool = False

    # borders_innerV (bool, optional): Draw vertical borders between columns.
    borders_innerV: bool = False

    # borders_outerV (bool, optional): Draw vertical borders on the left and right sides.
    borders_outerV: bool = False

    # no_host_extendX (bool, optional): Make outer width auto-fit to columns, overriding outer_size.x value. Only available when ScrollX/ScrollY are disabled and Stretch columns are not used.
    no_host_extendX: bool = False

    # no_host_extendY (bool, optional): Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit). Only available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.
    no_host_extendY: bool = False

    # no_keep_columns_visible (bool, optional): Disable keeping column always minimally visible when ScrollX is off and table gets too small. Not recommended if columns are resizable.
    no_keep_columns_visible: bool = False

    # precise_widths (bool, optional): Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns
    precise_widths: bool = False

    # no_clip (bool, optional): Disable clipping rectangle for every individual columns.
    no_clip: bool = False

    # pad_outerX (bool, optional): Default if BordersOuterV is on. Enable outer-most padding. Generally desirable if you have headers.
    pad_outerX: bool = False

    # no_pad_outerX (bool, optional): Default if BordersOuterV is off. Disable outer-most padding.
    no_pad_outerX: bool = False

    # no_pad_innerX (bool, optional): Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off).
    no_pad_innerX: bool = False

    # scrollX (bool, optional): Enable horizontal scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size. Changes default sizing policy. Because this create a child window, ScrollY is currently generally recommended when using ScrollX.
    scrollX: bool = False

    # scrollY (bool, optional): Enable vertical scrolling.
    scrollY: bool = False

    # no_saved_settings (bool, optional): Never load/save settings in .ini file.
    no_saved_settings: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid
        _source_guid = getattr(self.source, 'guid', 0)

        _ret = internal_dpg.add_table(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=_source_guid,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            header_row=self.header_row,
            clipper=self.clipper,
            inner_width=self.inner_width,
            policy=self.policy,
            freeze_rows=self.freeze_rows,
            freeze_columns=self.freeze_columns,
            sort_multi=self.sort_multi,
            sort_tristate=self.sort_tristate,
            resizable=self.resizable,
            reorderable=self.reorderable,
            hideable=self.hideable,
            sortable=self.sortable,
            context_menu_in_body=self.context_menu_in_body,
            row_background=self.row_background,
            borders_innerH=self.borders_innerH,
            borders_outerH=self.borders_outerH,
            borders_innerV=self.borders_innerV,
            borders_outerV=self.borders_outerV,
            no_host_extendX=self.no_host_extendX,
            no_host_extendY=self.no_host_extendY,
            no_keep_columns_visible=self.no_keep_columns_visible,
            precise_widths=self.precise_widths,
            no_clip=self.no_clip,
            pad_outerX=self.pad_outerX,
            no_pad_outerX=self.no_pad_outerX,
            no_pad_innerX=self.no_pad_innerX,
            scrollX=self.scrollX,
            scrollY=self.scrollY,
            no_saved_settings=self.no_saved_settings,
        )
        
        return _ret

    def callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.callback is None:
            return None
        elif isinstance(self.callback, Callback):
            return self.callback.fn(sender=self)
        else:
            return self.callback()


@dataclasses.dataclass(repr=False)
class TableCell(MovableContainerWidget):
    """
    Refer:
    >>> dpg.table_cell

     Adds a table.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # height (int, optional): Height of the item.
    height: int = 0

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_table_cell(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TableRow(MovableContainerWidget):
    """
    Refer:
    >>> dpg.table_row

     Adds a table row.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # height (int, optional): Height of the item.
    height: int = 0

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_table_row(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TemplateRegistry(Registry):
    """
    Refer:
    >>> dpg.template_registry

     Adds a template registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _ret = internal_dpg.add_template_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TextureRegistry(Registry):
    """
    Refer:
    >>> dpg.texture_registry

     Adds a dynamic texture.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = False

    def build(self) -> int:

        _ret = internal_dpg.add_texture_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ThemeComponent(MovableContainerWidget):
    """
    Refer:
    >>> dpg.theme_component

     Adds a theme component.

    """

    # item_type (int, optional): ...
    item_type: int = 0

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # enabled_state (bool, optional): ...
    enabled_state: bool = True

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_theme_component(
            tag=self.guid,
            parent=_parent_guid,
            item_type=self.item_type,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            enabled_state=self.enabled_state,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Tooltip(ContainerWidget):
    """
    Refer:
    >>> dpg.tooltip

     Adds a tooltip window.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # delay (float, optional): Activation delay
    delay: float = 0.0

    # hide_on_activity (bool, optional): Hide the tooltip if the user has moved the mouse.  If False, the tooltip will follow mouse pointer.
    hide_on_activity: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_tooltip(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
            delay=self.delay,
            hide_on_activity=self.hide_on_activity,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class TreeNode(MovableContainerWidget):
    """
    Refer:
    >>> dpg.tree_node

     Adds a tree node to add items to.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: t.Union[Callback, t.Callable] = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: t.Union[Callback, t.Callable] = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_open (bool, optional): Sets the tree node open by default.
    default_open: bool = False

    # open_on_double_click (bool, optional): Need double-click to open node.
    open_on_double_click: bool = False

    # open_on_arrow (bool, optional): Only open when clicking on the arrow part.
    open_on_arrow: bool = False

    # leaf (bool, optional): No collapsing, no arrow (use as a convenience for leaf nodes).
    leaf: bool = False

    # bullet (bool, optional): Display a bullet instead of arrow.
    bullet: bool = False

    # selectable (bool, optional): Makes the tree selectable.
    selectable: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_tree_node(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            default_open=self.default_open,
            open_on_double_click=self.open_on_double_click,
            open_on_arrow=self.open_on_arrow,
            leaf=self.leaf,
            bullet=self.bullet,
            selectable=self.selectable,
        )
        
        return _ret

    def drag_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        elif isinstance(self.drag_callback, Callback):
            return self.drag_callback.fn(sender=self)
        else:
            return self.drag_callback()

    def drop_callback_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        elif isinstance(self.drop_callback, Callback):
            return self.drop_callback.fn(sender=self)
        else:
            return self.drop_callback()


@dataclasses.dataclass(repr=False)
class ValueRegistry(Registry):
    """
    Refer:
    >>> dpg.value_registry

     Adds a value registry.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    def build(self) -> int:

        _ret = internal_dpg.add_value_registry(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class ViewportMenuBar(ContainerWidget):
    """
    Refer:
    >>> dpg.viewport_menu_bar

     Adds a menubar to the viewport.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    def build(self) -> int:

        _parent_guid = self.parent.guid

        _ret = internal_dpg.add_viewport_menu_bar(
            tag=self.guid,
            parent=_parent_guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            show=self.show,
            delay_search=self.delay_search,
        )
        
        return _ret


@dataclasses.dataclass(repr=False)
class Window(ContainerWidget):
    """
    Refer:
    >>> dpg.window

     Creates a new window for following items to be added to.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: USER_DATA = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [])

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # min_size (Union[List[int], Tuple[int, ...]], optional): Minimum window size.
    min_size: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [100, 100])

    # max_size (Union[List[int], Tuple[int, ...]], optional): Maximum window size.
    max_size: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [30000, 30000])

    # menubar (bool, optional): Shows or hides the menubar.
    menubar: bool = False

    # collapsed (bool, optional): Collapse the window.
    collapsed: bool = False

    # autosize (bool, optional): Autosized the window to fit it's items.
    autosize: bool = False

    # no_resize (bool, optional): Allows for the window size to be changed or fixed.
    no_resize: bool = False

    # no_title_bar (bool, optional): Title name for the title bar of the window.
    no_title_bar: bool = False

    # no_move (bool, optional): Allows for the window's position to be changed or fixed.
    no_move: bool = False

    # no_scrollbar (bool, optional): Disable scrollbars. (window can still scroll with mouse or programmatically)
    no_scrollbar: bool = False

    # no_collapse (bool, optional): Disable user collapsing window by double-clicking on it.
    no_collapse: bool = False

    # horizontal_scrollbar (bool, optional): Allow horizontal scrollbar to appear. (off by default)
    horizontal_scrollbar: bool = False

    # no_focus_on_appearing (bool, optional): Disable taking focus when transitioning from hidden to visible state.
    no_focus_on_appearing: bool = False

    # no_bring_to_front_on_focus (bool, optional): Disable bringing window to front when taking focus. (e.g. clicking on it or programmatically giving it focus)
    no_bring_to_front_on_focus: bool = False

    # no_close (bool, optional): Disable user closing the window by removing the close button.
    no_close: bool = False

    # no_background (bool, optional): Sets Background and border alpha to transparent.
    no_background: bool = False

    # modal (bool, optional): Fills area behind window according to the theme and disables user ability to interact with anything except the window.
    modal: bool = False

    # popup (bool, optional): Fills area behind window according to the theme, removes title bar, collapse and close. Window can be closed by selecting area in the background behind the window.
    popup: bool = False

    # no_saved_settings (bool, optional): Never load/save settings in .ini file.
    no_saved_settings: bool = False

    # no_open_over_existing_popup (bool, optional): Don't open if there's already a popup
    no_open_over_existing_popup: bool = True

    # no_scroll_with_mouse (bool, optional): Disable user vertically scrolling with mouse wheel.
    no_scroll_with_mouse: bool = False

    # on_close (Callable, optional): Callback ran when window is closed.
    on_close: t.Union[Callback, t.Callable] = None

    def build(self) -> int:

        _ret = internal_dpg.add_window(
            tag=self.guid,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
            delay_search=self.delay_search,
            min_size=self.min_size,
            max_size=self.max_size,
            menubar=self.menubar,
            collapsed=self.collapsed,
            autosize=self.autosize,
            no_resize=self.no_resize,
            no_title_bar=self.no_title_bar,
            no_move=self.no_move,
            no_scrollbar=self.no_scrollbar,
            no_collapse=self.no_collapse,
            horizontal_scrollbar=self.horizontal_scrollbar,
            no_focus_on_appearing=self.no_focus_on_appearing,
            no_bring_to_front_on_focus=self.no_bring_to_front_on_focus,
            no_close=self.no_close,
            no_background=self.no_background,
            modal=self.modal,
            popup=self.popup,
            no_saved_settings=self.no_saved_settings,
            no_open_over_existing_popup=self.no_open_over_existing_popup,
            no_scroll_with_mouse=self.no_scroll_with_mouse,
            on_close=self.on_close_fn,
        )
        
        return _ret

    def on_close_fn(self, sender_guid: int):
        # eventually remove this sanity check in (dpg_widgets_generator.py)...
        assert sender_guid == self.guid, \
            'was expecting the guid to match ...'

        # logic ...
        if self.on_close is None:
            return None
        elif isinstance(self.on_close, Callback):
            return self.on_close.fn(sender=self)
        else:
            return self.on_close()
