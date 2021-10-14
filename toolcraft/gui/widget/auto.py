"""
********************************************************************************
** This code is auto-generated using script `scripts/dpg_widget_generator.py` **
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dataclasses
import dearpygui.dearpygui as dpg
import typing as t
import enum

from ... import marshalling as m
from .. import Widget, Callback, Color


class ColorPicker(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    bar = dpg.mvColorPicker_bar
    wheel = dpg.mvColorPicker_wheel

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_ColorPicker"


class ComboHeight(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Large = dpg.mvComboHeight_Large
    Largest = dpg.mvComboHeight_Largest
    Regular = dpg.mvComboHeight_Regular
    Small = dpg.mvComboHeight_Small

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_ComboHeight"


class DatePickerLevel(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Day = dpg.mvDatePickerLevel_Day
    Month = dpg.mvDatePickerLevel_Month
    Year = dpg.mvDatePickerLevel_Year

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_DatePickerLevel"


class Dir(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Down = dpg.mvDir_Down
    Left = dpg.mvDir_Left
    NONE = dpg.mvDir_None
    Right = dpg.mvDir_Right
    Up = dpg.mvDir_Up

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_Dir"


class FontRangeHint(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Chinese_Full = dpg.mvFontRangeHint_Chinese_Full
    Chinese_Simplified_Common = dpg.mvFontRangeHint_Chinese_Simplified_Common
    Cyrillic = dpg.mvFontRangeHint_Cyrillic
    Default = dpg.mvFontRangeHint_Default
    Japanese = dpg.mvFontRangeHint_Japanese
    Korean = dpg.mvFontRangeHint_Korean
    Thai = dpg.mvFontRangeHint_Thai
    Vietnamese = dpg.mvFontRangeHint_Vietnamese

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_FontRangeHint"


class FormatFloat(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    rgb = dpg.mvFormat_Float_rgb
    rgba = dpg.mvFormat_Float_rgba

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_FormatFloat"


class KeyBrowser(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Back = dpg.mvKey_Browser_Back
    Favorites = dpg.mvKey_Browser_Favorites
    Forward = dpg.mvKey_Browser_Forward
    Home = dpg.mvKey_Browser_Home
    Refresh = dpg.mvKey_Browser_Refresh
    Search = dpg.mvKey_Browser_Search
    Stop = dpg.mvKey_Browser_Stop

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_KeyBrowser"


class KeyLaunch(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    App1 = dpg.mvKey_Launch_App1
    App2 = dpg.mvKey_Launch_App2
    Mail = dpg.mvKey_Launch_Mail
    Media_Select = dpg.mvKey_Launch_Media_Select

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_KeyLaunch"


class KeyVolume(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Down = dpg.mvKey_Volume_Down
    Mute = dpg.mvKey_Volume_Mute
    Up = dpg.mvKey_Volume_Up

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_KeyVolume"


class MouseButton(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Left = dpg.mvMouseButton_Left
    Middle = dpg.mvMouseButton_Middle
    Right = dpg.mvMouseButton_Right
    X1 = dpg.mvMouseButton_X1
    X2 = dpg.mvMouseButton_X2

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_MouseButton"


class NodeCol(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    BoxSelector = dpg.mvNodeCol_BoxSelector
    BoxSelectorOutline = dpg.mvNodeCol_BoxSelectorOutline
    GridBackground = dpg.mvNodeCol_GridBackground
    GridLine = dpg.mvNodeCol_GridLine
    Link = dpg.mvNodeCol_Link
    LinkHovered = dpg.mvNodeCol_LinkHovered
    LinkSelected = dpg.mvNodeCol_LinkSelected
    NodeBackground = dpg.mvNodeCol_NodeBackground
    NodeBackgroundHovered = dpg.mvNodeCol_NodeBackgroundHovered
    NodeBackgroundSelected = dpg.mvNodeCol_NodeBackgroundSelected
    NodeOutline = dpg.mvNodeCol_NodeOutline
    Pin = dpg.mvNodeCol_Pin
    PinHovered = dpg.mvNodeCol_PinHovered
    TitleBar = dpg.mvNodeCol_TitleBar
    TitleBarHovered = dpg.mvNodeCol_TitleBarHovered
    TitleBarSelected = dpg.mvNodeCol_TitleBarSelected

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_NodeCol"


class NodeStyleVar(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    GridSpacing = dpg.mvNodeStyleVar_GridSpacing
    LinkHoverDistance = dpg.mvNodeStyleVar_LinkHoverDistance
    LinkLineSegmentsPerLength = dpg.mvNodeStyleVar_LinkLineSegmentsPerLength
    LinkThickness = dpg.mvNodeStyleVar_LinkThickness
    NodeBorderThickness = dpg.mvNodeStyleVar_NodeBorderThickness
    NodeCornerRounding = dpg.mvNodeStyleVar_NodeCornerRounding
    NodePaddingHorizontal = dpg.mvNodeStyleVar_NodePaddingHorizontal
    NodePaddingVertical = dpg.mvNodeStyleVar_NodePaddingVertical
    PinCircleRadius = dpg.mvNodeStyleVar_PinCircleRadius
    PinHoverRadius = dpg.mvNodeStyleVar_PinHoverRadius
    PinLineThickness = dpg.mvNodeStyleVar_PinLineThickness
    PinOffset = dpg.mvNodeStyleVar_PinOffset
    PinQuadSideLength = dpg.mvNodeStyleVar_PinQuadSideLength
    PinTriangleSideLength = dpg.mvNodeStyleVar_PinTriangleSideLength

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_NodeStyleVar"


class NodeAttr(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Input = dpg.mvNode_Attr_Input
    Output = dpg.mvNode_Attr_Output
    Static = dpg.mvNode_Attr_Static

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_NodeAttr"


class NodePinShape(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Circle = dpg.mvNode_PinShape_Circle
    CircleFilled = dpg.mvNode_PinShape_CircleFilled
    Quad = dpg.mvNode_PinShape_Quad
    QuadFilled = dpg.mvNode_PinShape_QuadFilled
    Triangle = dpg.mvNode_PinShape_Triangle
    TriangleFilled = dpg.mvNode_PinShape_TriangleFilled

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_NodePinShape"


class PlotBin(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Rice = dpg.mvPlotBin_Rice
    Scott = dpg.mvPlotBin_Scott
    Sqrt = dpg.mvPlotBin_Sqrt
    Sturges = dpg.mvPlotBin_Sturges

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotBin"


class PlotCol(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Crosshairs = dpg.mvPlotCol_Crosshairs
    ErrorBar = dpg.mvPlotCol_ErrorBar
    Fill = dpg.mvPlotCol_Fill
    FrameBg = dpg.mvPlotCol_FrameBg
    InlayText = dpg.mvPlotCol_InlayText
    LegendBg = dpg.mvPlotCol_LegendBg
    LegendBorder = dpg.mvPlotCol_LegendBorder
    LegendText = dpg.mvPlotCol_LegendText
    Line = dpg.mvPlotCol_Line
    MarkerFill = dpg.mvPlotCol_MarkerFill
    MarkerOutline = dpg.mvPlotCol_MarkerOutline
    PlotBg = dpg.mvPlotCol_PlotBg
    PlotBorder = dpg.mvPlotCol_PlotBorder
    Query = dpg.mvPlotCol_Query
    Selection = dpg.mvPlotCol_Selection
    TitleText = dpg.mvPlotCol_TitleText
    XAxis = dpg.mvPlotCol_XAxis
    XAxisGrid = dpg.mvPlotCol_XAxisGrid
    YAxis = dpg.mvPlotCol_YAxis
    YAxis2 = dpg.mvPlotCol_YAxis2
    YAxis3 = dpg.mvPlotCol_YAxis3
    YAxisGrid = dpg.mvPlotCol_YAxisGrid
    YAxisGrid2 = dpg.mvPlotCol_YAxisGrid2
    YAxisGrid3 = dpg.mvPlotCol_YAxisGrid3

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotCol"


class PlotColormap(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    BrBG = dpg.mvPlotColormap_BrBG
    Cool = dpg.mvPlotColormap_Cool
    Dark = dpg.mvPlotColormap_Dark
    Deep = dpg.mvPlotColormap_Deep
    Default = dpg.mvPlotColormap_Default
    Greys = dpg.mvPlotColormap_Greys
    Hot = dpg.mvPlotColormap_Hot
    Jet = dpg.mvPlotColormap_Jet
    Paired = dpg.mvPlotColormap_Paired
    Pastel = dpg.mvPlotColormap_Pastel
    PiYG = dpg.mvPlotColormap_PiYG
    Pink = dpg.mvPlotColormap_Pink
    Plasma = dpg.mvPlotColormap_Plasma
    RdBu = dpg.mvPlotColormap_RdBu
    Spectral = dpg.mvPlotColormap_Spectral
    Twilight = dpg.mvPlotColormap_Twilight
    Viridis = dpg.mvPlotColormap_Viridis

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotColormap"


class PlotMarker(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Asterisk = dpg.mvPlotMarker_Asterisk
    Circle = dpg.mvPlotMarker_Circle
    Cross = dpg.mvPlotMarker_Cross
    Diamond = dpg.mvPlotMarker_Diamond
    Down = dpg.mvPlotMarker_Down
    Left = dpg.mvPlotMarker_Left
    NONE = dpg.mvPlotMarker_None
    Plus = dpg.mvPlotMarker_Plus
    Right = dpg.mvPlotMarker_Right
    Square = dpg.mvPlotMarker_Square
    Up = dpg.mvPlotMarker_Up

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotMarker"


class PlotStyleVar(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    AnnotationPadding = dpg.mvPlotStyleVar_AnnotationPadding
    DigitalBitGap = dpg.mvPlotStyleVar_DigitalBitGap
    DigitalBitHeight = dpg.mvPlotStyleVar_DigitalBitHeight
    ErrorBarSize = dpg.mvPlotStyleVar_ErrorBarSize
    ErrorBarWeight = dpg.mvPlotStyleVar_ErrorBarWeight
    FillAlpha = dpg.mvPlotStyleVar_FillAlpha
    FitPadding = dpg.mvPlotStyleVar_FitPadding
    LabelPadding = dpg.mvPlotStyleVar_LabelPadding
    LegendInnerPadding = dpg.mvPlotStyleVar_LegendInnerPadding
    LegendPadding = dpg.mvPlotStyleVar_LegendPadding
    LegendSpacing = dpg.mvPlotStyleVar_LegendSpacing
    LineWeight = dpg.mvPlotStyleVar_LineWeight
    MajorGridSize = dpg.mvPlotStyleVar_MajorGridSize
    MajorTickLen = dpg.mvPlotStyleVar_MajorTickLen
    MajorTickSize = dpg.mvPlotStyleVar_MajorTickSize
    Marker = dpg.mvPlotStyleVar_Marker
    MarkerSize = dpg.mvPlotStyleVar_MarkerSize
    MarkerWeight = dpg.mvPlotStyleVar_MarkerWeight
    MinorAlpha = dpg.mvPlotStyleVar_MinorAlpha
    MinorGridSize = dpg.mvPlotStyleVar_MinorGridSize
    MinorTickLen = dpg.mvPlotStyleVar_MinorTickLen
    MinorTickSize = dpg.mvPlotStyleVar_MinorTickSize
    MousePosPadding = dpg.mvPlotStyleVar_MousePosPadding
    PlotBorderSize = dpg.mvPlotStyleVar_PlotBorderSize
    PlotDefaultSize = dpg.mvPlotStyleVar_PlotDefaultSize
    PlotMinSize = dpg.mvPlotStyleVar_PlotMinSize
    PlotPadding = dpg.mvPlotStyleVar_PlotPadding

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotStyleVar"


class PlotLocation(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Center = dpg.mvPlot_Location_Center
    East = dpg.mvPlot_Location_East
    North = dpg.mvPlot_Location_North
    NorthEast = dpg.mvPlot_Location_NorthEast
    NorthWest = dpg.mvPlot_Location_NorthWest
    South = dpg.mvPlot_Location_South
    SouthEast = dpg.mvPlot_Location_SouthEast
    SouthWest = dpg.mvPlot_Location_SouthWest
    West = dpg.mvPlot_Location_West

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_PlotLocation"


class StyleVar(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Alpha = dpg.mvStyleVar_Alpha
    ButtonTextAlign = dpg.mvStyleVar_ButtonTextAlign
    CellPadding = dpg.mvStyleVar_CellPadding
    ChildBorderSize = dpg.mvStyleVar_ChildBorderSize
    ChildRounding = dpg.mvStyleVar_ChildRounding
    FrameBorderSize = dpg.mvStyleVar_FrameBorderSize
    FramePadding = dpg.mvStyleVar_FramePadding
    FrameRounding = dpg.mvStyleVar_FrameRounding
    GrabMinSize = dpg.mvStyleVar_GrabMinSize
    GrabRounding = dpg.mvStyleVar_GrabRounding
    IndentSpacing = dpg.mvStyleVar_IndentSpacing
    ItemInnerSpacing = dpg.mvStyleVar_ItemInnerSpacing
    ItemSpacing = dpg.mvStyleVar_ItemSpacing
    PopupBorderSize = dpg.mvStyleVar_PopupBorderSize
    PopupRounding = dpg.mvStyleVar_PopupRounding
    ScrollbarRounding = dpg.mvStyleVar_ScrollbarRounding
    ScrollbarSize = dpg.mvStyleVar_ScrollbarSize
    SelectableTextAlign = dpg.mvStyleVar_SelectableTextAlign
    TabRounding = dpg.mvStyleVar_TabRounding
    WindowBorderSize = dpg.mvStyleVar_WindowBorderSize
    WindowMinSize = dpg.mvStyleVar_WindowMinSize
    WindowPadding = dpg.mvStyleVar_WindowPadding
    WindowRounding = dpg.mvStyleVar_WindowRounding
    WindowTitleAlign = dpg.mvStyleVar_WindowTitleAlign

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_StyleVar"


class TabOrder(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Fixed = dpg.mvTabOrder_Fixed
    Leading = dpg.mvTabOrder_Leading
    Reorderable = dpg.mvTabOrder_Reorderable
    Trailing = dpg.mvTabOrder_Trailing

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_TabOrder"


class TableSizing(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    FixedFit = dpg.mvTable_SizingFixedFit
    FixedSame = dpg.mvTable_SizingFixedSame
    StretchProp = dpg.mvTable_SizingStretchProp
    StretchSame = dpg.mvTable_SizingStretchSame

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_TableSizing"


class ThemeCat(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Core = dpg.mvThemeCat_Core
    Nodes = dpg.mvThemeCat_Nodes
    Plots = dpg.mvThemeCat_Plots

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_ThemeCat"


class ThemeCol(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    Border = dpg.mvThemeCol_Border
    BorderShadow = dpg.mvThemeCol_BorderShadow
    Button = dpg.mvThemeCol_Button
    ButtonActive = dpg.mvThemeCol_ButtonActive
    ButtonHovered = dpg.mvThemeCol_ButtonHovered
    CheckMark = dpg.mvThemeCol_CheckMark
    ChildBg = dpg.mvThemeCol_ChildBg
    DockingEmptyBg = dpg.mvThemeCol_DockingEmptyBg
    DockingPreview = dpg.mvThemeCol_DockingPreview
    DragDropTarget = dpg.mvThemeCol_DragDropTarget
    FrameBg = dpg.mvThemeCol_FrameBg
    FrameBgActive = dpg.mvThemeCol_FrameBgActive
    FrameBgHovered = dpg.mvThemeCol_FrameBgHovered
    Header = dpg.mvThemeCol_Header
    HeaderActive = dpg.mvThemeCol_HeaderActive
    HeaderHovered = dpg.mvThemeCol_HeaderHovered
    MenuBarBg = dpg.mvThemeCol_MenuBarBg
    ModalWindowDimBg = dpg.mvThemeCol_ModalWindowDimBg
    NavHighlight = dpg.mvThemeCol_NavHighlight
    NavWindowingDimBg = dpg.mvThemeCol_NavWindowingDimBg
    NavWindowingHighlight = dpg.mvThemeCol_NavWindowingHighlight
    PlotHistogram = dpg.mvThemeCol_PlotHistogram
    PlotHistogramHovered = dpg.mvThemeCol_PlotHistogramHovered
    PlotLines = dpg.mvThemeCol_PlotLines
    PlotLinesHovered = dpg.mvThemeCol_PlotLinesHovered
    PopupBg = dpg.mvThemeCol_PopupBg
    ResizeGrip = dpg.mvThemeCol_ResizeGrip
    ResizeGripActive = dpg.mvThemeCol_ResizeGripActive
    ResizeGripHovered = dpg.mvThemeCol_ResizeGripHovered
    ScrollbarBg = dpg.mvThemeCol_ScrollbarBg
    ScrollbarGrab = dpg.mvThemeCol_ScrollbarGrab
    ScrollbarGrabActive = dpg.mvThemeCol_ScrollbarGrabActive
    ScrollbarGrabHovered = dpg.mvThemeCol_ScrollbarGrabHovered
    Separator = dpg.mvThemeCol_Separator
    SeparatorActive = dpg.mvThemeCol_SeparatorActive
    SeparatorHovered = dpg.mvThemeCol_SeparatorHovered
    SliderGrab = dpg.mvThemeCol_SliderGrab
    SliderGrabActive = dpg.mvThemeCol_SliderGrabActive
    Tab = dpg.mvThemeCol_Tab
    TabActive = dpg.mvThemeCol_TabActive
    TabHovered = dpg.mvThemeCol_TabHovered
    TabUnfocused = dpg.mvThemeCol_TabUnfocused
    TabUnfocusedActive = dpg.mvThemeCol_TabUnfocusedActive
    TableBorderLight = dpg.mvThemeCol_TableBorderLight
    TableBorderStrong = dpg.mvThemeCol_TableBorderStrong
    TableHeaderBg = dpg.mvThemeCol_TableHeaderBg
    TableRowBg = dpg.mvThemeCol_TableRowBg
    TableRowBgAlt = dpg.mvThemeCol_TableRowBgAlt
    Text = dpg.mvThemeCol_Text
    TextDisabled = dpg.mvThemeCol_TextDisabled
    TextSelectedBg = dpg.mvThemeCol_TextSelectedBg
    TitleBg = dpg.mvThemeCol_TitleBg
    TitleBgActive = dpg.mvThemeCol_TitleBgActive
    TitleBgCollapsed = dpg.mvThemeCol_TitleBgCollapsed
    WindowBg = dpg.mvThemeCol_WindowBg

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_ThemeCol"


class Tool(m.FrozenEnum, enum.Enum):

    DEFAULT = 0
    About = dpg.mvTool_About
    Debug = dpg.mvTool_Debug
    Doc = dpg.mvTool_Doc
    Font = dpg.mvTool_Font
    ItemRegistry = dpg.mvTool_ItemRegistry
    Metrics = dpg.mvTool_Metrics
    Style = dpg.mvTool_Style

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_Tool"


@dataclasses.dataclass(frozen=True)
class Column(Widget):
    """
    Refer:
    >>> dpg.add_table_column

    Adds a table column.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # ...
    init_width_or_weight: float = 0.0

    # Default as a hidden/disabled column.
    default_hide: bool = False

    # Default as a sorting column.
    default_sort: bool = False

    # Column will stretch. Preferable with horizontal scrolling disabled
    # (default if table sizing policy is _SizingStretchSame or
    # _SizingStretchProp).
    width_stretch: bool = False

    # Column will not stretch. Preferable with horizontal scrolling enabled
    # (default if table sizing policy is _SizingFixedFit and table is
    # resizable).
    width_fixed: bool = False

    # Disable manual resizing.
    no_resize: bool = False

    # Disable manual reordering this column, this will also prevent other
    # columns from crossing over this column.
    no_reorder: bool = False

    # Disable ability to hide/disable this column.
    no_hide: bool = False

    # Disable clipping for this column (all NoClip columns will render in a
    # same draw command).
    no_clip: bool = False

    # Disable ability to sort on this field (even if
    # ImGuiTableFlags_Sortable is set on the table).
    no_sort: bool = False

    # Disable ability to sort in the ascending direction.
    no_sort_ascending: bool = False

    # Disable ability to sort in the descending direction.
    no_sort_descending: bool = False

    # Disable header text width contribution to automatic column width.
    no_header_width: bool = False

    # Make the initial sort direction Ascending when first sorting on this
    # column (default).
    prefer_sort_ascending: bool = True

    # Make the initial sort direction Descending when first sorting on this
    # column.
    prefer_sort_descending: bool = False

    # Use current Indent value when entering cell (default for column 0).
    indent_enable: bool = False

    # Ignore current Indent value when entering cell (default for columns >
    # 0). Indentation changes _within_ the cell will still be honored.
    indent_disable: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table_column(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class Row(Widget):
    """
    Refer:
    >>> dpg.table_row

    Adds a table row.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Height of the item.
    height: int = 0

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table_row(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class BTable(Widget):
    """
    Refer:
    >>> dpg.table

    Adds a table.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # show headers at the top of the columns
    header_row: bool = True

    # Use clipper (rows must be same height).
    clipper: bool = False

    # ...
    inner_width: int = 0

    # ...
    policy: TableSizing = TableSizing.DEFAULT

    # ...
    freeze_rows: int = 0

    # ...
    freeze_columns: int = 0

    # Hold shift when clicking headers to sort on multiple column.
    sort_multi: bool = False

    # Allow no sorting, disable default sorting.
    sort_tristate: bool = False

    # Enable resizing columns
    resizable: bool = False

    # Enable reordering columns in header row (need calling
    # TableSetupColumn() + TableHeadersRow() to display headers)
    reorderable: bool = False

    # Enable hiding/disabling columns in context menu.
    hideable: bool = False

    # Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also
    # see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
    sortable: bool = False

    # Right-click on columns body/contents will display table context menu.
    # By default it is available in TableHeadersRow().
    context_menu_in_body: bool = False

    # Set each RowBg color with ImGuiCol_TableRowBg or
    # ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with
    # ImGuiTableBgFlags_RowBg0 on each row manually)
    row_background: bool = False

    # Draw horizontal borders between rows.
    borders_innerH: bool = False

    # Draw horizontal borders at the top and bottom.
    borders_outerH: bool = False

    # Draw vertical borders between columns.
    borders_innerV: bool = False

    # Draw vertical borders on the left and right sides.
    borders_outerV: bool = False

    # Make outer width auto-fit to columns, overriding outer_size.x value.
    # Only available when ScrollX/ScrollY are disabled and Stretch columns
    # are not used.
    no_host_extendX: bool = False

    # Make outer height stop exactly at outer_size.y (prevent auto-extending
    # table past the limit). Only available when ScrollX/ScrollY are
    # disabled. Data below the limit will be clipped and not visible.
    no_host_extendY: bool = False

    # Disable keeping column always minimally visible when ScrollX is off
    # and table gets too small. Not recommended if columns are resizable.
    no_keep_columns_visible: bool = False

    # Disable distributing remainder width to stretched columns (width
    # allocation on a 100-wide table with 3 columns
    precise_widths: bool = False

    # Disable clipping rectangle for every individual columns.
    no_clip: bool = False

    # Default if BordersOuterV is on. Enable outer-most padding. Generally
    # desirable if you have headers.
    pad_outerX: bool = False

    # Default if BordersOuterV is off. Disable outer-most padding.
    no_pad_outerX: bool = False

    # Disable inner padding between columns (double inner padding if
    # BordersOuterV is on, single inner padding if BordersOuterV is off).
    no_pad_innerX: bool = False

    # Enable horizontal scrolling. Require 'outer_size' parameter of
    # BeginTable() to specify the container size. Changes default sizing
    # policy. Because this create a child window, ScrollY is currently
    # generally recommended when using ScrollX.
    scrollX: bool = False

    # Enable vertical scrolling.
    scrollY: bool = False

    # Never load/save settings in .ini file.
    no_saved_settings: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            header_row=self.header_row,
            clipper=self.clipper,
            inner_width=self.inner_width,
            policy=self.policy.value,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class TabButton(Widget):
    """
    Refer:
    >>> dpg.add_tab_button

    Adds a tab button to a tab bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Disable reordering this tab or having another tab cross over this tab.
    no_reorder: bool = False

    # Enforce the tab position to the left of the tab bar (after the tab
    # list popup button).
    leading: bool = False

    # Enforce the tab position to the right of the tab bar (before the
    # scrolling buttons).
    trailing: bool = False

    # Disable tooltip for the given tab.
    no_tooltip: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab_button(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class TabBar(Widget):
    """
    Refer:
    >>> dpg.tab_bar

    Adds a tab bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Allows for the user to change the order of the tabs.
    reorderable: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab_bar(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            indent=self.indent,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            reorderable=self.reorderable,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Tab(Widget):
    """
    Refer:
    >>> dpg.tab

    Adds a tab to a tab bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Creates a button on the tab that can hide the tab.
    closable: bool = False

    # Disable tooltip for the given tab.
    no_tooltip: bool = False

    # set using a constant
    order_mode: bool = 0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Button(Widget):
    """
    Refer:
    >>> dpg.add_button

    Adds a button.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Small button, useful for embedding in text.
    small: bool = False

    # Arrow button, requires the direction keyword.
    arrow: bool = False

    # A cardinal direction for arrow.
    direction: int = 0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_button(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            direction=self.direction,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Combo(Widget):
    """
    Refer:
    >>> dpg.add_combo

    Adds a combo dropdown that allows a user to select a single option
    from a drop down window.
    """

    # A tuple of items to be shown in the drop down window. Can consist of
    # any combination of types.
    items: t.Union[t.List[str], t.Tuple[str, ...]] = ()

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: str = ''

    # Align the popup toward the left.
    popup_align_left: bool = False

    # Display the preview box without the square arrow button.
    no_arrow_button: bool = False

    # Display only the square arrow button.
    no_preview: bool = False

    # mvComboHeight_Small, _Regular, _Large, _Largest
    height_mode: int = 1

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_combo(
            **self.internal.dpg_kwargs,
            items=self.items,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            height_mode=self.height_mode,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Separator(Widget):
    """
    Refer:
    >>> dpg.add_separator

    Adds a horizontal separator.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_separator(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class ChildWindow(Widget):
    """
    Refer:
    >>> dpg.child_window

    Adds an embedded child window. Will show scrollbars when items do not
    fit.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Shows/Hides the border around the sides.
    border: bool = True

    # Autosize the window to fit it's items in the x.
    autosize_x: bool = False

    # Autosize the window to fit it's items in the y.
    autosize_y: bool = False

    # Disable scrollbars (window can still scroll with mouse or
    # programmatically).
    no_scrollbar: bool = False

    # Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    # Shows/Hides the menubar at the top.
    menubar: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_child_window(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Window(Widget):
    """
    Refer:
    >>> dpg.window

    Creates a new window for following items to be added to.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Minimum window size.
    min_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Maximum window size.
    max_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Shows or hides the menubar.
    menubar: bool = False

    # Collapse the window.
    collapsed: bool = False

    # Autosized the window to fit it's items.
    autosize: bool = False

    # Allows for the window size to be changed or fixed.
    no_resize: bool = False

    # Title name for the title bar of the window.
    no_title_bar: bool = False

    # Allows for the window's position to be changed or fixed.
    no_move: bool = False

    # Disable scrollbars. (window can still scroll with mouse or
    # programmatically)
    no_scrollbar: bool = False

    # Disable user collapsing window by double-clicking on it.
    no_collapse: bool = False

    # Allow horizontal scrollbar to appear. (off by default)
    horizontal_scrollbar: bool = False

    # Disable taking focus when transitioning from hidden to visible state.
    no_focus_on_appearing: bool = False

    # Disable bringing window to front when taking focus. (e.g. clicking on
    # it or programmatically giving it focus)
    no_bring_to_front_on_focus: bool = False

    # Disable user closing the window by removing the close button.
    no_close: bool = False

    # Sets Background and border alpha to transparent.
    no_background: bool = False

    # Fills area behind window according to the theme and disables user
    # ability to interact with anything except the window.
    modal: bool = False

    # Fills area behind window according to the theme, removes title bar,
    # collapse and close. Window can be closed by selecting area in the
    # background behind the window.
    popup: bool = False

    # Never load/save settings in .ini file.
    no_saved_settings: bool = False

    # Callback ran when window is closed.
    on_close: Callback = None

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_window(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            on_close=self.on_close_fn,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def on_close_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.on_close is None:
            return None
        else:
            return self.on_close.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Text(Widget):
    """
    Refer:
    >>> dpg.add_text

    Adds text. Text can have an optional label that will display to the
    right of the text.
    """

    # ...
    default_value: str = ''

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Number of pixels until wrapping starts.
    wrap: int = -1

    # Makes the text bulleted.
    bullet: bool = False

    # Color of the text (rgba).
    color: Color = Color.DEFAULT

    # Displays the label.
    show_label: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_text(
            **self.internal.dpg_kwargs,
            default_value=self.default_value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            color=self.color.value,
            show_label=self.show_label,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class CollapsingHeader(Widget):
    """
    Refer:
    >>> dpg.collapsing_header

    Adds a collapsing header to add items to. Must be closed with the end
    command.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Adds the ability to hide this widget by pressing the (x) in the top
    # right of widget.
    closable: bool = False

    # Sets the collapseable header open by default.
    default_open: bool = False

    # Need double-click to open node.
    open_on_double_click: bool = False

    # Only open when clicking on the arrow part.
    open_on_arrow: bool = False

    # No collapsing, no arrow (use as a convenience for leaf nodes).
    leaf: bool = False

    # Display a bullet instead of arrow.
    bullet: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_collapsing_header(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Group(Widget):
    """
    Refer:
    >>> dpg.group

    Creates a group that other widgets can belong to. The group allows
    item commands to be issued for all of its members.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Forces child widgets to be added in a horizontal layout.
    horizontal: bool = False

    # Spacing for the horizontal layout.
    horizontal_spacing: float = -1

    # Offset from containing window x item location within group.
    xoffset: float = 0.0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_group(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Legend(Widget):
    """
    Refer:
    >>> dpg.add_plot_legend

    Adds a plot legend to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # location, mvPlot_Location_*
    location: PlotLocation = PlotLocation.NorthWest

    # ...
    horizontal: bool = False

    # ...
    outside: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_legend(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            location=self.location.value,
            horizontal=self.horizontal,
            outside=self.outside,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class XAxis(Widget):
    """
    Refer:
    >>> dpg.plot_axis

    Adds an axis to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # ...
    no_gridlines: bool = False

    # ...
    no_tick_marks: bool = False

    # ...
    no_tick_labels: bool = False

    # ...
    log_scale: bool = False

    # ...
    invert: bool = False

    # ...
    lock_min: bool = False

    # ...
    lock_max: bool = False

    # ...
    time: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_axis(
            axis=dpg.mvXAxis,
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class YAxis(Widget):
    """
    Refer:
    >>> dpg.plot_axis

    Adds an axis to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # ...
    no_gridlines: bool = False

    # ...
    no_tick_marks: bool = False

    # ...
    no_tick_labels: bool = False

    # ...
    log_scale: bool = False

    # ...
    invert: bool = False

    # ...
    lock_min: bool = False

    # ...
    lock_max: bool = False

    # ...
    time: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_axis(
            axis=dpg.mvYAxis,
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SubPlot(Widget):
    """
    Refer:
    >>> dpg.subplots

    Adds a collection of plots.
    """

    # ...
    rows: int

    # ...
    columns: int

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    row_ratios: t.Union[t.List[float], t.Tuple[float, ...]] = \
        dataclasses.field(default_factory=list)

    # ...
    column_ratios: t.Union[t.List[float], t.Tuple[float, ...]] = \
        dataclasses.field(default_factory=list)

    # ...
    no_title: bool = False

    # the user will not be able to open context menus with right-click
    no_menus: bool = False

    # resize splitters between subplot cells will be not be provided
    no_resize: bool = False

    # subplot edges will not be aligned vertically or horizontally
    no_align: bool = False

    # link the y-axis limits of all plots in each row (does not apply
    # auxiliary y-axes)
    link_rows: bool = False

    # link the x-axis limits of all plots in each column
    link_columns: bool = False

    # link the x-axis limits in every plot in the subplot
    link_all_x: bool = False

    # link the y-axis limits in every plot in the subplot (does not apply to
    # auxiliary y-axes)
    link_all_y: bool = False

    # subplots are added in column major order instead of the default row
    # major order
    column_major: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_subplots(
            **self.internal.dpg_kwargs,
            rows=self.rows,
            columns=self.columns,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SimplePlot(Widget):
    """
    Refer:
    >>> dpg.add_simple_plot

    Adds a simple plot for visualization of a 1 dimensional set of values.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = ()

    # overlays text (similar to a plot title)
    overlay: str = ''

    # ...
    histogram: bool = False

    # ...
    autosize: bool = True

    # ...
    min_scale: float = 0.0

    # ...
    max_scale: float = 0.0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_simple_plot(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class BPlot(Widget):
    """
    Refer:
    >>> dpg.plot

    Adds a plot which is used to hold series, and can be drawn to with
    draw commands.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: bool = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    no_title: bool = False

    # ...
    no_menus: bool = False

    # ...
    no_box_select: bool = False

    # ...
    no_mouse_pos: bool = False

    # ...
    no_highlight: bool = False

    # ...
    no_child: bool = False

    # ...
    query: bool = False

    # ...
    crosshairs: bool = False

    # ...
    anti_aliased: bool = False

    # ...
    equal_aspects: bool = False

    # enables panning when held
    pan_button: int = 0

    # optional modifier that must be held for panning
    pan_mod: int = -1

    # fits visible data when double clicked
    fit_button: int = 0

    # opens plot context menu (if enabled) when clicked
    context_menu_button: int = 1

    # begins box selection when pressed and confirms selection when released
    box_select_button: int = 1

    # begins box selection when pressed and confirms selection when released
    box_select_mod: int = -1

    # cancels active box selection when pressed
    box_select_cancel_button: int = 0

    # begins query selection when pressed and end query selection when
    # released
    query_button: int = 2

    # optional modifier that must be held for query selection
    query_mod: int = -1

    # when held, active box selections turn into queries
    query_toggle_mod: int = 17

    # expands active box selection/query horizontally to plot edge when held
    horizontal_mod: int = 18

    # expands active box selection/query vertically to plot edge when held
    vertical_mod: int = 16

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class InputIntX(Widget):
    """
    Refer:
    >>> dpg.add_input_intx

    Adds multi int input for up to 4 integer values.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    # Value for lower limit of input for each cell. Use clamped to turn on.
    min_value: int = 0

    # Value for upper limit of input for each cell. Use clamped to turn on.
    max_value: int = 100

    # Number of components.
    size: int = 4

    # Activates and deactivates min_value.
    min_clamped: bool = False

    # Activates and deactivates max_value.
    max_clamped: bool = False

    # Only runs callback on enter.
    if_entered: bool = False

    # Activates a read only mode for the inputs.
    readonly: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_input_intx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class InputInt(Widget):
    """
    Refer:
    >>> dpg.add_input_int

    Adds input for an int.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: int = 0

    # Value for lower limit of input. By default this limits the step
    # buttons. Use clamped to limit manual input.
    min_value: int = 0

    # Value for upper limit of input. By default this limits the step
    # buttons. Use clamped to limit manual input.
    max_value: int = 100

    # Increment to change value by when the step buttons are pressed.
    # Setting this to a value of 0 or smaller will turn off step buttons.
    step: int = 1

    # After holding the step buttons for extended time the increments will
    # switch to this value.
    step_fast: int = 100

    # Activates and deactivates min_value.
    min_clamped: bool = False

    # Activates and deactivates max_value.
    max_clamped: bool = False

    # Only runs callback on enter key press.
    if_entered: bool = False

    # Activates a read only mode for the input.
    readonly: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_input_int(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class ProgressBar(Widget):
    """
    Refer:
    >>> dpg.add_progress_bar

    Adds a progress bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # Overlayed text.
    overlay: str = ''

    # Normalized value to fill the bar from 0.0 to 1.0.
    default_value: float = 0.0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_progress_bar(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class CheckBox(Widget):
    """
    Refer:
    >>> dpg.add_checkbox

    Adds a checkbox.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: bool = False

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_checkbox(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class ColorMapScale(Widget):
    """
    Refer:
    >>> dpg.add_colormap_scale

    Adds a legend that pairs values with colors. This is typically used
    with a heat series.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # mvPlotColormap_* constants or mvColorMap uuid
    colormap: t.Union[int, str] = 0

    # Sets the min number of the color scale. Typically is the same as the
    # min scale from the heat series.
    min_scale: float = 0.0

    # Sets the max number of the color scale. Typically is the same as the
    # max scale from the heat series.
    max_scale: float = 1.0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_colormap_scale(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            colormap=self.colormap,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class DragLine(Widget):
    """
    Refer:
    >>> dpg.add_drag_line

    Adds a drag line to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # ...
    default_value: t.Any = 0.0

    # ...
    color: Color = Color.DEFAULT

    # ...
    thickness: float = 1.0

    # ...
    show_label: bool = True

    # ...
    vertical: bool = True

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_drag_line(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            source=0 if self.source is None else self.source.dpg_id,
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color.value,
            thickness=self.thickness,
            show_label=self.show_label,
            vertical=self.vertical,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class DragPoint(Widget):
    """
    Refer:
    >>> dpg.add_drag_point

    Adds a drag point to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # ...
    default_value: t.Any = (0.0, 0.0)

    # ...
    color: Color = Color.DEFAULT

    # ...
    thickness: float = 1.0

    # ...
    show_label: bool = True

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_drag_point(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            source=0 if self.source is None else self.source.dpg_id,
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color.value,
            thickness=self.thickness,
            show_label=self.show_label,
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SliderInt(Widget):
    """
    Refer:
    >>> dpg.add_slider_int

    Adds slider for a single int value. Directly entry can be done with
    double click or CTRL+Click. Min and Max alone are a soft limit for the
    slider. Use clamped keyword to also apply limits to the direct entry
    modes.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: int = 0

    # Sets orientation to vertical.
    vertical: bool = False

    # Disable direct entry methods or Enter key allowing to input text
    # directly into the widget.
    no_input: bool = False

    # Applies the min and max limits to direct entry methods also such as
    # double click and CTRL+Click.
    clamped: bool = False

    # Applies a limit only to sliding entry only.
    min_value: int = 0

    # Applies a limit only to sliding entry only.
    max_value: int = 100

    # ...
    format: str = '%d'

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_int(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SliderIntX(Widget):
    """
    Refer:
    >>> dpg.add_slider_intx

    Adds multi slider for up to 4 int values. Directly entry can be done
    with double click or CTRL+Click. Min and Max alone are a soft limit
    for the slider. Use clamped keyword to also apply limits to the direct
    entry modes.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, 0)

    # number of components
    size: int = 4

    # Disable direct entry methods or Enter key allowing to input text
    # directly into the widget.
    no_input: bool = False

    # Applies the min and max limits to direct entry methods also such as
    # double click and CTRL+Click.
    clamped: bool = False

    # Applies a limit only to sliding entry only.
    min_value: int = 0

    # Applies a limit only to sliding entry only.
    max_value: int = 100

    # ...
    format: str = '%d'

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_intx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SliderFloat(Widget):
    """
    Refer:
    >>> dpg.add_slider_float

    Adds slider for a single float value. Directly entry can be done with
    double click or CTRL+Click. Min and Max alone are a soft limit for the
    slider. Use clamped keyword to also apply limits to the direct entry
    modes.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: float = 0.0

    # Sets orientation to vertical.
    vertical: bool = False

    # Disable direct entry methods or Enter key allowing to input text
    # directly into the widget.
    no_input: bool = False

    # Applies the min and max limits to direct entry methods also such as
    # double click and CTRL+Click.
    clamped: bool = False

    # Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # ...
    format: str = '%.3f'

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_float(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class SliderFloatX(Widget):
    """
    Refer:
    >>> dpg.add_slider_floatx

    Adds multi slider for up to 4 float values. Directly entry can be done
    with double click or CTRL+Click. Min and Max alone are a soft limit
    for the slider. Use clamped keyword to also apply limits to the direct
    entry modes.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0, 0.0, 0.0)

    # Number of components.
    size: int = 4

    # Disable direct entry methods or Enter key allowing to input text
    # directly into the widget.
    no_input: bool = False

    # Applies the min and max limits to direct entry methods also such as
    # double click and CTRL+Click.
    clamped: bool = False

    # Applies a limit only to sliding entry only.
    min_value: float = 0.0

    # Applies a limit only to sliding entry only.
    max_value: float = 100.0

    # ...
    format: str = '%.3f'

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_floatx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class Slider3D(Widget):
    """
    Refer:
    >>> dpg.add_3d_slider

    Adds a 3D box slider.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0, 0.0, 0.0)

    # Applies upper limit to slider.
    max_x: float = 100.0

    # Applies upper limit to slider.
    max_y: float = 100.0

    # Applies upper limit to slider.
    max_z: float = 100.0

    # Applies lower limit to slider.
    min_x: float = 0.0

    # Applies lower limit to slider.
    min_y: float = 0.0

    # Applies lower limit to slider.
    min_z: float = 0.0

    # Size of the widget.
    scale: float = 1.0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_3d_slider(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
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
            # kwargs=self.kwargs,
        )
        
        return _ret

    def callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.callback is None:
            return None
        else:
            return self.callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drag_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )

    def drop_callback_fn(
        self, 
        sender_dpg_id: int, 
        app_data: t.Any, 
        user_data: t.Any
    ):
        # eventually remove this sanity check (dpg_widgets_generator.py)...
        assert sender_dpg_id == self.dpg_id, \
            'was expecting the dpg_id to match ...'

        # logic ...
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn(
                sender=self, app_data=app_data, user_data=user_data
            )


@dataclasses.dataclass(frozen=True)
class ToolTip(Widget):
    """
    Refer:
    >>> dpg.tooltip

    Adds a tooltip window.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Attempt to render widget.
    show: bool = True

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tooltip(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            show=self.show,
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class Theme(Widget):
    """
    Refer:
    >>> dpg.theme

    Adds a theme.
    """

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_theme(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class ThemeColor(Widget):
    """
    Refer:
    >>> dpg.add_theme_color

    Adds a theme color.
    """

    # ...
    target: ThemeCol = ThemeCol.DEFAULT

    # ...
    value: Color = Color.BLACK

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Options include mvThemeCat_Core, mvThemeCat_Plots, mvThemeCat_Nodes.
    category: ThemeCat = ThemeCat.DEFAULT

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_theme_color(
            **self.internal.dpg_kwargs,
            target=self.target.value,
            value=self.value.value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            category=self.category.value,
            # kwargs=self.kwargs,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class ThemeStyle(Widget):
    """
    Refer:
    >>> dpg.add_theme_style

    Adds a theme style.
    """

    # ...
    target: ThemeCol = ThemeCol.DEFAULT

    # ...
    x: float = 1.0

    # ...
    y: float = -1.0

    # Overrides 'name' as label.
    label: str = None

    # User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # Use generated internal label instead of user specified (appends ###
    # uuid).
    use_internal_label: bool = True

    # Unique id used to programmatically refer to the item.If label is
    # unused this will be the label.
    tag: t.Union[int, str] = 0

    # Options include mvThemeCat_Core, mvThemeCat_Plots, mvThemeCat_Nodes.
    category: ThemeCat = ThemeCat.DEFAULT

    # kwargs: inspect._empty

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_theme_style(
            **self.internal.dpg_kwargs,
            target=self.target.value,
            x=self.x,
            y=self.y,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            tag=self.tag,
            category=self.category.value,
            # kwargs=self.kwargs,
        )
        
        return _ret
