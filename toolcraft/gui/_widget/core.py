
import dataclasses
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from ... import error as e
from ... import util
from .auto import BTable, BPlot, BXAxis, BYAxis, TableColumn, TableRow, TableCell
from .auto import PlotLegend, Text


@dataclasses.dataclass
class Table(BTable):
    # ...
    rows: t.Union[int, t.List[TableRow]] = None

    # ...
    columns: t.Union[int, t.List[t.Union[str, TableColumn]]] = None

    def init_validate(self):
        # call super
        super().init_validate()

        # check mandatory fields
        if self.rows is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `rows`"
                ]
            )
        if self.columns is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `columns`"
                ]
            )

    def init(self):
        # call super
        super().init()

        # add columns
        _num_columns = None
        if isinstance(self.columns, int):
            for _ in range(self.columns):
                self.add_child(
                    guid=f"c{_}", widget=TableColumn(),
                )
            _num_columns = self.columns
        elif isinstance(self.columns, list):
            for _ in self.columns:
                self.add_child(
                    guid=f"c{_}",
                    widget=TableColumn(label=_) if isinstance(_, str) else _,
                )
            _num_columns = len(self.columns)
        else:
            e.validation.NotAllowed(
                msgs=[
                    f"unknown type for field columns: {type(self.columns)}"
                ]
            )
            raise

        # add rows
        if isinstance(self.rows, int):
            _rows = [TableRow() for _ in range(self.rows)]
        else:
            _rows = self.rows
        for _, _row in enumerate(_rows):
            # add row
            self.add_child(
                guid=f"r{_}", widget=_row,
            )
            # add cells to row
            for _c in range(_num_columns):
                _row.add_child(
                    guid=f"{_c}", widget=Group()
                )

    def set_row_color(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.set_table_row_color
        """
        internal_dpg.set_table_row_color(self.dpg_id, row, color)

    def unset_row_color(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.unset_table_row_color
        """
        internal_dpg.unset_table_row_color(self.dpg_id, row)

    def get_cell(self, row: int, column: int) -> "Group":
        # noinspection PyTypeChecker
        return self.children[f"r{row}"].children[f"{column}"]

    def get_column(self, column: int) -> TableColumn:
        # noinspection PyTypeChecker
        return self.children[f"c{column}"]

    def get_row(self, row: int) -> TableRow:
        # noinspection PyTypeChecker
        return self.children[f"r{row}"]

    @classmethod
    def table_from_dict(
        cls, input_dict: t.Dict,
    ) -> "Table":
        _rows = list(input_dict.keys())
        _columns = ["\\"] + list(input_dict[_rows[0]].keys())
        _table = Table(
            rows=len(_rows), columns=_columns,
        )
        for _rid, _r in enumerate(_rows):
            for _cid, _c in enumerate(_columns):
                if _c == "\\":
                    _table.get_cell(
                        row=_rid, column=_cid
                    ).add_child(
                        guid=f"{_rid}_{_cid}",
                        widget=Text(default_value=f"{_r}")
                    )
                else:
                    _table.get_cell(
                        row=_rid, column=_cid
                    ).add_child(
                        guid=f"{_rid}_{_cid}",
                        widget=Text(default_value=f"{input_dict[_r][_c]}")
                    )
        return _table

    def highlight_cell(self, row: int, col: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_cell
        """
        internal_dpg.highlight_table_cell(self.dpg_id, row, col, color)

    def unhighlight_cell(self, row: int, col: int):
        """
        Refer:
        >>> dpg.unhighlight_table_cell
        """
        internal_dpg.unhighlight_table_cell(self.dpg_id, row, col)

    def is_cell_highlight(self, row: int, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_cell_highlight
        """
        return internal_dpg.is_table_cell_highlight(self.dpg_id, row, col)

    def highlight_column(self, col: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_column
        """
        internal_dpg.highlight_table_column(self.dpg_id, col, color)

    def unhighlight_column(self, col: int):
        """
        Refer:
        >>> dpg.unhighlight_table_column
        """
        internal_dpg.unhighlight_table_column(self.dpg_id, col)

    def is_column_highlight(self, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_column_highlight
        """
        return internal_dpg.is_table_column_highlight(self.dpg_id, col)

    def highlight_row(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_row
        """
        internal_dpg.highlight_table_row(self.dpg_id, row, color)

    def unhighlight_row(self, row: int):
        """
        Refer:
        >>> dpg.unhighlight_table_row
        """
        internal_dpg.unhighlight_table_row(self.dpg_id, row)

    def is_row_highlight(self, row: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_row_highlight
        """
        return internal_dpg.is_table_row_highlight(self.dpg_id, row)


@dataclasses.dataclass
class XAxis(BXAxis):

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        internal_dpg.fit_axis_data(axis=self.dpg_id)

    def clear(self):
        """
        Refer:
        >>> dpg.delete_item
        """
        # https://github.com/hoffstadt/DearPyGui/discussions/1328
        internal_dpg.delete_item(item=self.dpg_id, children_only=True, slot=1)

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        return internal_dpg.get_axis_limits(self.dpg_id)

    def reset_ticks(self):
        internal_dpg.reset_axis_ticks(self.dpg_id)

    def set_limits(self, ymin: float, ymax: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        internal_dpg.set_axis_limits(self.dpg_id, ymin, ymax)

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        internal_dpg.set_axis_limits_auto(self.dpg_id)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        internal_dpg.set_axis_ticks(self.dpg_id, label_pairs)


@dataclasses.dataclass
class YAxis(BYAxis):

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        internal_dpg.fit_axis_data(axis=self.dpg_id)

    def clear(self):
        """
        Refer:
        >>> dpg.delete_item
        """
        # https://github.com/hoffstadt/DearPyGui/discussions/1328
        internal_dpg.delete_item(item=self.dpg_id, children_only=True, slot=1)

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        return internal_dpg.get_axis_limits(self.dpg_id)

    def reset_ticks(self):
        internal_dpg.reset_axis_ticks(self.dpg_id)

    def set_limits(self, ymin: float, ymax: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        internal_dpg.set_axis_limits(self.dpg_id, ymin, ymax)

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        internal_dpg.set_axis_limits_auto(self.dpg_id)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        internal_dpg.set_axis_ticks(self.dpg_id, label_pairs)

    # noinspection PyMethodMayBeStatic
    def update_series(self, series_dpg_id: int, **kwargs):
        # todo: test code to see if series_dpg_id belongs to this plot ...
        #  this will need some tracking code when series are added
        dpg.configure_item(series_dpg_id, **kwargs)

    # pk; start tag >>>
    # pk; end tag >>>


# noinspection PyDefaultArgument
@dataclasses.dataclass
class Plot(BPlot):
    """
    Refer this to improve more:
      + https://dearpygui.readthedocs.io/en/latest/documentation/plots.html

    Clearing series: https://github.com/hoffstadt/DearPyGui/discussions/1328
    A series is no different than any other Dear PyGui item. Just delete it!
    The structure of a plot is as follows:

    plot
      slot 0
        legend (optional)
        annotations (optional)
        drag lines (optional)
        drag points (optional)
      slot 1
        x axis (required)
        y axis (required)
          series (optional)
        y axis 2 (optional)
          series (optional)
        y axis 3 (optional)
          series (optional)
      slot 2
        drawing items (optional)
      slot 3
        drag payloads (optional)

    To clear all of a plot's series. You just need to delete the y axes' slot 1
    children using delete_item(...) with children_only set to True and slot set to 1.
    """

    # width: int = -1
    #
    # height: int = 400

    num_of_y_axis: t.Literal[1, 2, 3] = 1

    @property
    @util.CacheResult
    def legend(self) -> PlotLegend:
        _ret = PlotLegend()
        _ret.internal.parent = self
        _ret.internal.before = None
        return _ret

    @property
    @util.CacheResult
    def x_axis(self) -> XAxis:
        _ret = XAxis()
        _ret.internal.parent = self
        _ret.internal.before = None
        return _ret

    @property
    @util.CacheResult
    def y1_axis(self) -> YAxis:
        _ret = YAxis()
        _ret.internal.parent = self
        _ret.internal.before = None
        return _ret

    @property
    @util.CacheResult
    def y2_axis(self) -> YAxis:
        if self.num_of_y_axis not in [2, 3]:
            e.code.CodingError(
                msgs=[
                    f"You cannot access this property. "
                    f"Please set the field `num_of_y_axis` to be one of [2, 3]"
                ]
            )
        _ret = YAxis()
        _ret.internal.parent = self
        _ret.internal.before = None
        return _ret

    @property
    @util.CacheResult
    def y3_axis(self) -> YAxis:
        if self.num_of_y_axis != 3:
            e.code.CodingError(
                msgs=[
                    f"You cannot access this property. "
                    f"Please set the field `num_of_y_axis` to be 3 to use this property"
                ]
            )
        _ret = YAxis()
        _ret.internal.parent = self
        _ret.internal.before = None
        return _ret

    @property
    def is_queried(self) -> bool:
        return internal_dpg.is_plot_queried(self.dpg_id)

    def init_validate(self):
        # call super
        super().init_validate()
        # check num_of_y_axis
        e.validation.ShouldBeOneOf(
            value=self.num_of_y_axis, values=[1, 2, 3],
            msgs=[
                "Please crosscheck the value for field num_of_y_axis"
            ]
        )

    def init(self):

        # call super
        super().init()

        # add legend and axis which are same as widgets but are immediate
        # part of Plot widget and needs to be added well in advance
        _ = self.legend, self.x_axis, self.y1_axis
        if self.num_of_y_axis == 2:
            _ = self.y2_axis
        elif self.num_of_y_axis == 3:
            _ = self.y2_axis, self.y3_axis

    def build(self) -> t.Union[int, str]:
        # call super
        _ret = super().build()

        # add other things
        self.legend.build()
        self.x_axis.build()
        self.y1_axis.build()
        if self.num_of_y_axis == 2:
            self.y2_axis.build()
        elif self.num_of_y_axis == 3:
            self.y2_axis.build()
            self.y3_axis.build()

        # return
        return _ret

    def clear(self):
        self.x_axis.clear()
        self.y1_axis.clear()
        if self.num_of_y_axis == 2:
            self.y2_axis.clear()
        elif self.num_of_y_axis == 3:
            self.y2_axis.clear()
            self.y3_axis.clear()

    def get_query_area(self) -> t.Tuple[float, float]:
        """
        Refer:
        >>> dpg.get_plot_query_area
        """
        return tuple(internal_dpg.get_plot_query_area(self.dpg_id))
