"""
********************************************************************************
This code is auto-generated using script:
    toolcraft/gui/scripts/dpg_widgets_generator.py
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dataclasses
import dearpygui.dearpygui as dpg
import typing as t
import enum

from ... import marshalling as m
from .. import Widget, Callback


class EnDir(m.FrozenEnum, enum.Enum):

    Left = dpg.mvDir_Left  # 0
    Up = dpg.mvDir_Up  # 2
    Down = dpg.mvDir_Down  # 3
    Right = dpg.mvDir_Right  # 1
    NONE = dpg.mvDir_None  # -1

    @classmethod
    def yaml_tag(cls) -> str:
        return "!gui_EnDir"


class EnComboHeight(m.FrozenEnum, enum.Enum):

    Small = dpg.mvComboHeight_Small  # 0
    Regular = dpg.mvComboHeight_Regular  # 1
    Large = dpg.mvComboHeight_Large  # 2
    Largest = dpg.mvComboHeight_Largest  # 3

    @classmethod
    def yaml_tag(cls) -> str:
        return "!gui_EnComboHeight"


class EnPlotLocation(m.FrozenEnum, enum.Enum):

    Center = dpg.mvPlot_Location_Center  # 0
    East = dpg.mvPlot_Location_East  # 8
    North = dpg.mvPlot_Location_North  # 1
    NorthEast = dpg.mvPlot_Location_NorthEast  # 9
    NorthWest = dpg.mvPlot_Location_NorthWest  # 5
    South = dpg.mvPlot_Location_South  # 2
    SouthEast = dpg.mvPlot_Location_SouthEast  # 10
    SouthWest = dpg.mvPlot_Location_SouthWest  # 6
    West = dpg.mvPlot_Location_West  # 4

    @classmethod
    def yaml_tag(cls) -> str:
        return "!gui_EnPlotLocation"


class EnPlotColormap(m.FrozenEnum, enum.Enum):

    BrBG = dpg.mvPlotColormap_BrBG  # 12
    Cool = dpg.mvPlotColormap_Cool  # 7
    Dark = dpg.mvPlotColormap_Dark  # 1
    Deep = dpg.mvPlotColormap_Deep  # 0
    Default = dpg.mvPlotColormap_Default  # 0
    Greys = dpg.mvPlotColormap_Greys  # 15
    Hot = dpg.mvPlotColormap_Hot  # 6
    Jet = dpg.mvPlotColormap_Jet  # 9
    Paired = dpg.mvPlotColormap_Paired  # 3
    Pastel = dpg.mvPlotColormap_Pastel  # 2
    PiYG = dpg.mvPlotColormap_PiYG  # 13
    Pink = dpg.mvPlotColormap_Pink  # 8
    Plasma = dpg.mvPlotColormap_Plasma  # 5
    RdBu = dpg.mvPlotColormap_RdBu  # 11
    Spectral = dpg.mvPlotColormap_Spectral  # 14
    Twilight = dpg.mvPlotColormap_Twilight  # 10
    Viridis = dpg.mvPlotColormap_Viridis  # 4

    @classmethod
    def yaml_tag(cls) -> str:
        return "!gui_EnPlotColormap"


@dataclasses.dataclass(frozen=True)
class BTable(Widget):
    """
    Refer:
    >>> dpg.table

     Adds a table.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
class TableColumn(Widget):
    """
    Refer:
    >>> dpg.add_table_column

     Adds a table column.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table_column(
            **self.internal.dpg_kwargs,
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


@dataclasses.dataclass(frozen=True)
class TableRow(Widget):
    """
    Refer:
    >>> dpg.table_row

     Adds a table row.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # height (int, optional): Height of the item.
    height: int = 0

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table_row(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class TableCell(Widget):
    """
    Refer:
    >>> dpg.table_cell

     Adds a table.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # height (int, optional): Height of the item.
    height: int = 0

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_table_cell(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class TabButton(Widget):
    """
    Refer:
    >>> dpg.add_tab_button

     Adds a tab button to a tab bar.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab_button(
            **self.internal.dpg_kwargs,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab_bar(
            **self.internal.dpg_kwargs,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

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
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tab(
            **self.internal.dpg_kwargs,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    # direction (int, optional): Sets the cardinal direction for the arrow buy using constants mvDir_Left, mvDir_Up, mvDir_Down, mvDir_Right, mvDir_None. Arrow keyword must be set to True.
    direction: EnDir = EnDir.Left

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_button(
            **self.internal.dpg_kwargs,
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

     Adds a combo dropdown that allows a user to select a single option from a drop down window. All items will be shown as selectables on the dropdown.

    """

    # items (Union[List[str], Tuple[str, ...]], optional): A tuple of items to be shown in the drop down window. Can consist of any combination of types but will convert all items to strings to be shown.
    items: t.Union[t.List[str], t.Tuple[str, ...]] = ()

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_combo(
            **self.internal.dpg_kwargs,
            items=self.items,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds a horizontal line separator.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_separator(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class ChildWindow(Widget):
    """
    Refer:
    >>> dpg.child_window

     Adds an embedded child window. Will show scrollbars when items do not fit.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    # autosize_x (bool, optional): Autosize the window to fit it's items in the x.
    autosize_x: bool = False

    # autosize_y (bool, optional): Autosize the window to fit it's items in the y.
    autosize_y: bool = False

    # no_scrollbar (bool, optional): Disable scrollbars (window can still scroll with mouse or programmatically).
    no_scrollbar: bool = False

    # horizontal_scrollbar (bool, optional): Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    # menubar (bool, optional): Shows/Hides the menubar at the top.
    menubar: bool = False

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_child_window(
            **self.internal.dpg_kwargs,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # min_size (Union[List[int], Tuple[int, ...]], optional): Minimum window size.
    min_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # max_size (Union[List[int], Tuple[int, ...]], optional): Maximum window size.
    max_size: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    # on_close (Callable, optional): Callback ran when window is closed.
    on_close: Callback = None

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_window(
            **self.internal.dpg_kwargs,
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
            on_close=self.on_close_fn,
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

     Adds text. Text can have an optional label that will display to the right of the text.

    """

    # default_value (str, optional): ...
    default_value: str = ''

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    # color (Union[List[float], Tuple[float, ...]], optional): Color of the text (rgba).
    color: t.Union[t.List[float], t.Tuple[float, ...]] = (-1, -1, -1, -1)

    # show_label (bool, optional): Displays the label to teh right of the text.
    show_label: bool = False

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_text(
            **self.internal.dpg_kwargs,
            default_value=self.default_value,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds a collapsing header to add items to. Must be closed with the end command.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_collapsing_header(
            **self.internal.dpg_kwargs,
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

     Creates a group that other widgets can belong to. The group allows item commands to be issued for all of its members.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_group(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
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
class PlotLegend(Widget):
    """
    Refer:
    >>> dpg.add_plot_legend

     Adds a plot legend to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # location (int, optional): location, mvPlot_Location_*
    location: EnPlotLocation = EnPlotLocation.NorthWest

    # horizontal (bool, optional): ...
    horizontal: bool = False

    # outside (bool, optional): ...
    outside: bool = False

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_legend(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            location=self.location.value,
            horizontal=self.horizontal,
            outside=self.outside,
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
class BXAxis(Widget):
    """
    Refer:
    >>> dpg.plot_axis

     Adds an axis to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_axis(
            **self.internal.dpg_kwargs,
            axis=dpg.mvXAxis,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
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
class BYAxis(Widget):
    """
    Refer:
    >>> dpg.plot_axis

     Adds an axis to a plot.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot_axis(
            **self.internal.dpg_kwargs,
            axis=dpg.mvYAxis,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
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
class Subplots(Widget):
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
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # width (int, optional): Width of the item.
    width: int = 0

    # height (int, optional): Height of the item.
    height: int = 0

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # row_ratios (Union[List[float], Tuple[float, ...]], optional): ...
    row_ratios: t.Union[t.List[float], t.Tuple[float, ...]] = \
        dataclasses.field(default_factory=list)

    # column_ratios (Union[List[float], Tuple[float, ...]], optional): ...
    column_ratios: t.Union[t.List[float], t.Tuple[float, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_subplots(
            **self.internal.dpg_kwargs,
            rows=self.rows,
            columns=self.columns,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = ()

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_simple_plot(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds a plot which is used to hold series, and can be drawn to with draw commands.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # delay_search (bool, optional): Delays searching container for specified items until the end of the app. Possible optimization when a container has many children that are not accessed often.
    delay_search: bool = False

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # no_title (bool, optional): ...
    no_title: bool = False

    # no_menus (bool, optional): ...
    no_menus: bool = False

    # no_box_select (bool, optional): ...
    no_box_select: bool = False

    # no_mouse_pos (bool, optional): ...
    no_mouse_pos: bool = False

    # no_highlight (bool, optional): ...
    no_highlight: bool = False

    # no_child (bool, optional): ...
    no_child: bool = False

    # query (bool, optional): ...
    query: bool = False

    # crosshairs (bool, optional): ...
    crosshairs: bool = False

    # anti_aliased (bool, optional): ...
    anti_aliased: bool = False

    # equal_aspects (bool, optional): ...
    equal_aspects: bool = False

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_plot(
            **self.internal.dpg_kwargs,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_input_intx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
            if_entered=self.on_enter,
            readonly=self.readonly,
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

     Adds input for an int. +/- buttons can be activated by setting the value of step.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    # step (int, optional): Increment to change value by when the step buttons are pressed. Setting this to a value of 0 or smaller will turn off step buttons.
    step: int = 1

    # step_fast (int, optional): After holding the step buttons for extended time the increments will switch to this value.
    step_fast: int = 100

    # min_clamped (bool, optional): Activates and deactivates the enforcment of min_value.
    min_clamped: bool = False

    # max_clamped (bool, optional): Activates and deactivates the enforcment of max_value.
    max_clamped: bool = False

    # on_enter (bool, optional): Only runs callback on enter key press.
    if_entered: bool = False

    # readonly (bool, optional): Activates read only mode where no text can be input but text can still be highlighted.
    readonly: bool = False

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_input_int(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
            if_entered=self.on_enter,
            readonly=self.readonly,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_progress_bar(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
class Checkbox(Widget):
    """
    Refer:
    >>> dpg.add_checkbox

     Adds a checkbox.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # indent (int, optional): Offsets the widget to the right the specified number multiplied by the indent style.
    indent: int = -1

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # payload_type (str, optional): Sender string type must be the same as the target for the target to run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (bool, optional): Sets the default value of the checkmark
    default_value: bool = False

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_checkbox(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
class ColormapScale(Widget):
    """
    Refer:
    >>> dpg.add_colormap_scale

     Adds a legend that pairs values with colors. This is typically used with a heat series. 

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # colormap (Union[int, str], optional): mvPlotColormap_* constants or mvColorMap uuid from a color map registry
    colormap: EnPlotColormap = EnPlotColormap.Default

    # min_scale (float, optional): Sets the min number of the color scale. Typically is the same as the min scale from the heat series.
    min_scale: float = 0.0

    # max_scale (float, optional): Sets the max number of the color scale. Typically is the same as the max scale from the heat series.
    max_scale: float = 1.0

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_colormap_scale(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
            payload_type=self.payload_type,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            colormap=self.colormap.value,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_value (Any, optional): ...
    default_value: t.Any = 0.0

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # show_label (bool, optional): ...
    show_label: bool = True

    # vertical (bool, optional): ...
    vertical: bool = True

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_drag_line(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=getattr(self.source, 'dpg_id', 0),
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color,
            thickness=self.thickness,
            show_label=self.show_label,
            vertical=self.vertical,
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # source (Union[int, str], optional): Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # callback (Callable, optional): Registers a callback.
    callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # default_value (Any, optional): ...
    default_value: t.Any = (0.0, 0.0)

    # color (Union[List[int], Tuple[int, ...]], optional): ...
    color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255)

    # thickness (float, optional): ...
    thickness: float = 1.0

    # show_label (bool, optional): ...
    show_label: bool = True

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_drag_point(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            source=getattr(self.source, 'dpg_id', 0),
            callback=self.callback_fn,
            show=self.show,
            default_value=self.default_value,
            color=self.color,
            thickness=self.thickness,
            show_label=self.show_label,
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

     Adds slider for a single int value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_int(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds multi slider for up to 4 int values. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_intx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds slider for a single float value. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_float(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

     Adds multi slider for up to 4 float values. Directly entry can be done with double click or CTRL+Click. Min and Max alone are a soft limit for the slider. Use clamped keyword to also apply limits to the direct entry modes.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # enabled (bool, optional): Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0, 0.0, 0.0)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_slider_floatx(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

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
    callback: Callback = None

    # drag_callback (Callable, optional): Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # drop_callback (Callable, optional): Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    # pos (Union[List[int], Tuple[int, ...]], optional): Places the item relative to window coordinates, [0,0] is top left.
    pos: t.Union[t.List[int], t.Tuple[int, ...]] = \
        dataclasses.field(default_factory=list)

    # filter_key (str, optional): Used by filter widget.
    filter_key: str = ''

    # tracked (bool, optional): Scroll tracking
    tracked: bool = False

    # track_offset (float, optional): 0.0f
    track_offset: float = 0.5

    # default_value (Union[List[float], Tuple[float, ...]], optional): ...
    default_value: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0, 0.0, 0.0)

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

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_3d_slider(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=getattr(self.source, 'dpg_id', 0),
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
class Tooltip(Widget):
    """
    Refer:
    >>> dpg.tooltip

     Adds a tooltip window.

    """

    # label (str, optional): Overrides 'name' as label.
    label: str = None

    # user_data (Any, optional): User data for callbacks
    user_data: t.Union[Widget, t.List[Widget]] = None

    # use_internal_label (bool, optional): Use generated internal label instead of user specified (appends ### uuid).
    use_internal_label: bool = True

    # show (bool, optional): Attempt to render widget.
    show: bool = True

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    def build(self) -> t.Union[int, str]:
        _ret = dpg.add_tooltip(
            **self.internal.dpg_kwargs,
            label=self.label,
            user_data=self.user_data,
            use_internal_label=self.use_internal_label,
            show=self.show,
        )
        
        return _ret
