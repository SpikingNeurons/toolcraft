
import dataclasses
import typing as t
import dearpygui.dearpygui as dpg

from ... import error as e
from .. import Widget, Callback
from . import PLOT_DATA_TYPE
from .auto import BTable, BPlot, Group
from .auto import YAxis, XAxis, Legend, Column, Row, Text


@dataclasses.dataclass(frozen=True)
class Table(BTable):
    # ...
    rows: t.Union[int, t.List[Row]] = None

    # ...
    columns: t.Union[int, t.List[t.Union[str, Column]]] = None

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
                    guid=f"c{_}", widget=Column(),
                )
            _num_columns = self.columns
        elif isinstance(self.columns, list):
            for _ in self.columns:
                self.add_child(
                    guid=f"c{_}",
                    widget=Column(label=_) if isinstance(_, str) else _,
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
            _rows = [Row() for _ in range(self.rows)]
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

    def get_cell(self, row: int, column: int) -> "Group":
        # noinspection PyTypeChecker
        return self.children[f"r{row}"].children[f"{column}"]

    def get_column(self, column: int) -> Column:
        # noinspection PyTypeChecker
        return self.children[f"c{column}"]

    def get_row(self, row: int) -> Row:
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


# noinspection PyDefaultArgument
@dataclasses.dataclass(frozen=True)
class Plot(BPlot):
    # ...
    legend: t.Optional[Legend] = "legend"

    # ...
    x_axis: t.Union[str, XAxis] = ""

    # ...
    y1_axis: t.Union[str, YAxis] = ""

    # ...
    y2_axis: t.Union[str, YAxis] = None

    # ...
    y3_axis: t.Union[str, YAxis] = None

    #
    width: int = -1

    #
    height: int = 400

    def init(self):

        # call super
        super().init()

        # add legend and axis which are same as widgets but are immediate
        # part of Plot widget and needs to be added well in advance
        if self.legend is not None:
            if isinstance(self.legend, str):
                self.add_child(
                    guid="legend",
                    widget=Legend(label=self.legend)
                )
        if self.x_axis is not None:
            if isinstance(self.x_axis, str):
                self.add_child(
                    guid="x_axis",
                    widget=XAxis(label=self.x_axis)
                )
        if self.y1_axis is not None:
            if isinstance(self.y1_axis, str):
                self.add_child(
                    guid="y1_axis",
                    widget=YAxis(label=self.y1_axis)
                )
        if self.y2_axis is not None:
            if isinstance(self.y2_axis, str):
                self.add_child(
                    guid="y2_axis",
                    widget=YAxis(label=self.y2_axis)
                )
        if self.y3_axis is not None:
            if isinstance(self.y3_axis, str):
                self.add_child(
                    guid="y3_axis",
                    widget=YAxis(label=self.y3_axis)
                )

    def clear(self):
        # plot series are added to YAxis so we clear its children to clear
        # the plot
        for _v in self.children.values():
            if isinstance(_v, YAxis):
                dpg.delete_item(item=_v.dpg_id, children_only=True)

    def get_y_axis(self, axis_dim: int) -> YAxis:
        if axis_dim not in [1, 2, 3]:
            e.code.CodingError(
                msgs=[
                    f"for y axis axis_dim should be one of {[1, 2, 3]} ... "
                    f"but found unsupported {axis_dim}"
                ]
            )
        try:
            # noinspection PyTypeChecker
            return self.children[f"y{axis_dim}_axis"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    f"field `y{axis_dim}_axis` is not supplied while "
                    f"creating Plot instance"
                ]
            )

    def get_x_axis(self) -> XAxis:
        try:
            # noinspection PyTypeChecker
            return self.children["x_axis"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    "field `x_axis` is not supplied"
                ]
            )

    def get_legend(self) -> Legend:
        try:
            # noinspection PyTypeChecker
            return self.children["legend"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    f"field `legend` is not supplied"
                ]
            )

    # noinspection PyMethodMayBeStatic
    def update_series(self, series_dpg_id: int, **kwargs):
        # todo: test code to see if series_dpg_id belongs to this plot ...
        #  this will need some tracking code when series are added
        dpg.configure_item(series_dpg_id, **kwargs)

    def add_area_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        fill: t.Union[t.List[int], t.Tuple[int]] = (0, 0, 0, -255),
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_area_series

        Adds an area series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            fill:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_area_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            fill=fill,
            contribute_to_bounds=contribute_to_bounds,
        )

        return _dpg_id

    def add_bar_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        weight: float = 1.0,
        horizontal: bool = False,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_bar_series

        Adds a bar series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            weight:
              ...
            horizontal:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_bar_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            weight=weight,
            horizontal=horizontal,
        )

        return _dpg_id

    def add_candle_series(
        self, *,
        dates: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        opens: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        closes: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        lows: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        highs: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        bull_color: t.Union[t.List[int], t.Tuple[int]] = (0, 255, 113, 255),
        bear_color: t.Union[t.List[int], t.Tuple[int]] = (218, 13, 79, 255),
        weight: int = 0.25,
        tooltip: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_candle_series

        Adds a candle series to a plot.

        Args:
            dates:
              ...
            opens:
              ...
            closes:
              ...
            lows:
              ...
            highs:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            bull_color:
              ...
            bear_color:
              ...
            weight:
              ...
            tooltip:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_candle_series(
            parent=_y_axis.dpg_id,
            dates=dates,
            opens=opens,
            closes=closes,
            lows=lows,
            highs=highs,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            bull_color=bull_color,
            bear_color=bear_color,
            weight=weight,
            tooltip=tooltip,
        )

        return _dpg_id

    def add_drag_line(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        default_value: t.Any = 0.0,
        color: t.Union[t.List[int], t.Tuple[int]] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        vertical: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_drag_line

        Adds a drag line to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            callback:
              Registers a callback.
            show:
              Attempt to render widget.
            default_value:
              ...
            color:
              ...
            thickness:
              ...
            show_label:
              ...
            vertical:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_drag_line(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
            vertical=vertical,
        )

        return _dpg_id

    def add_drag_point(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        default_value: t.Any = (0.0, 0.0),
        color: t.Union[t.List[int], t.Tuple[int]] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_drag_point

        Adds a drag point to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            callback:
              Registers a callback.
            show:
              Attempt to render widget.
            default_value:
              ...
            color:
              ...
            thickness:
              ...
            show_label:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_drag_point(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
        )

        return _dpg_id

    def add_error_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        negative: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        positive: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        contribute_to_bounds: bool = True,
        horizontal: bool = False,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_error_series

        Adds an error series to a plot.

        Args:
            x:
              ...
            y:
              ...
            negative:
              ...
            positive:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            contribute_to_bounds:
              ...
            horizontal:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_error_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            negative=negative,
            positive=positive,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            contribute_to_bounds=contribute_to_bounds,
            horizontal=horizontal,
        )

        return _dpg_id

    def add_heat_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        rows: int,
        cols: int,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        scale_min: float = 0.0,
        scale_max: float = 1.0,
        bounds_min: t.Any = (0.0, 0.0),
        bounds_max: t.Any = (1.0, 1.0),
        format: str = '%0.1f',
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_heat_series

        Adds a heat series to a plot. Typically a color scale widget is also
        added to show the legend.

        Args:
            x:
              ...
            rows:
              ...
            cols:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            scale_min:
              Sets the color scale min. Typically paired with the color
              scale widget scale_min.
            scale_max:
              Sets the color scale max. Typically paired with the color
              scale widget scale_max.
            bounds_min:
              ...
            bounds_max:
              ...
            format:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_heat_series(
            parent=_y_axis.dpg_id,
            x=x,
            rows=rows,
            cols=cols,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            scale_min=scale_min,
            scale_max=scale_max,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            format=format,
            contribute_to_bounds=contribute_to_bounds,
        )

        return _dpg_id

    def add_histogram_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        bins: int = -1,
        bar_scale: float = 1.0,
        min_range: float = 0.0,
        max_range: float = 1.0,
        cumlative: bool = False,
        density: bool = False,
        outliers: bool = True,
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_histogram_series

        Adds a histogram series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            bins:
              ...
            bar_scale:
              ...
            min_range:
              ...
            max_range:
              ...
            cumlative:
              ...
            density:
              ...
            outliers:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_histogram_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            bins=bins,
            bar_scale=bar_scale,
            min_range=min_range,
            max_range=max_range,
            cumlative=cumlative,
            density=density,
            outliers=outliers,
            contribute_to_bounds=contribute_to_bounds,
        )

        return _dpg_id

    def add_hline_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_hline_series

        Adds a infinite horizontal line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_hline_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            contribute_to_bounds=contribute_to_bounds,
        )

        return _dpg_id

    def add_image_series(
        self, *,
        texture_id: t.Union[int, str],
        bounds_min: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        bounds_max: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        uv_min: t.Union[t.List[float], t.Tuple[float]] = (0.0, 0.0),
        uv_max: t.Union[t.List[float], t.Tuple[float]] = (1.0, 1.0),
        tint_color: t.Union[t.List[int], t.Tuple[int]] = (255, 255, 255, 255),
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_image_series

        Adds a image series to a plot.

        Args:
            texture_id:
              ...
            bounds_min:
              ...
            bounds_max:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            uv_min:
              normalized texture coordinates
            uv_max:
              normalized texture coordinates
            tint_color:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_image_series(
            parent=_y_axis.dpg_id,
            texture_id=texture_id,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            uv_min=uv_min,
            uv_max=uv_max,
            tint_color=tint_color,
        )

        return _dpg_id

    def add_line_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_line_series

        Adds a line series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_line_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
        )

        return _dpg_id

    def add_pie_series(
        self, *,
        x: float,
        y: float,
        radius: float,
        values: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        labels: t.Union[t.List[str], t.Tuple[str]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        format: str = '%0.2f',
        angle: float = 90.0,
        normalize: bool = False,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_pie_series

        Adds a pie series to a plot.

        Args:
            x:
              ...
            y:
              ...
            radius:
              ...
            values:
              ...
            labels:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            format:
              ...
            angle:
              ...
            normalize:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_pie_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            radius=radius,
            values=values,
            labels=labels,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            format=format,
            angle=angle,
            normalize=normalize,
        )

        return _dpg_id

    def add_plot_annotation(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        default_value: t.Any = (0.0, 0.0),
        offset: t.Union[t.List[float], t.Tuple[float]] = (0.0, 0.0),
        color: t.Union[t.List[int], t.Tuple[int]] = (0, 0, 0, -255),
        clamped: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_plot_annotation

        Adds an annotation to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            default_value:
              ...
            offset:
              ...
            color:
              ...
            clamped:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_plot_annotation(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            default_value=default_value,
            offset=offset,
            color=color,
            clamped=clamped,
        )

        return _dpg_id

    def add_scatter_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_scatter_series

        Adds a scatter series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_scatter_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
        )

        return _dpg_id

    def add_shade_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y1: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y2: t.Any = [],
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_shade_series

        Adds a shade series to a plot.

        Args:
            x:
              ...
            y1:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y2:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_shade_series(
            parent=_y_axis.dpg_id,
            x=x,
            y1=y1,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            y2=y2,
        )

        return _dpg_id

    def add_stair_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_stair_series

        Adds a stair series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_stair_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
        )

        return _dpg_id

    def add_stem_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        indent: int = -1,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_stem_series

        Adds a stem series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            indent:
              Offsets the widget to the right the specified number
              multiplied by the indent style.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_stem_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            indent=indent,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
        )

        return _dpg_id

    def add_text_point(
        self, *,
        x: float,
        y: float,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        x_offset: int = Ellipsis,
        y_offset: int = Ellipsis,
        vertical: bool = False,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_text_point

        Adds a labels series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            x_offset:
              ...
            y_offset:
              ...
            vertical:
              ...
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_text_point(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            x_offset=x_offset,
            y_offset=y_offset,
            vertical=vertical,
        )

        return _dpg_id

    def add_vline_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y_axis_dim: int = 1,
    ) -> int:
        """
        Refer:
        >>> dpg.add_vline_series

        Adds a infinite vertical line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks.
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            y_axis_dim:
              ...

        Returns:
            int

        """
        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)

        _dpg_id = dpg.add_vline_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
        )

        return _dpg_id

