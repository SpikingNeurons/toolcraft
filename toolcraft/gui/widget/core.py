
import dataclasses
import distutils.archive_util
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from ... import error as e
from ... import util
from .. import Widget, Callback
from .auto import BTable, BPlot, BXAxis, BYAxis
from .auto import PlotLegend, TableColumn, TableRow, TableCell, Text


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
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

    # noinspection PyMethodMayBeStatic
    def update_series(self, series_dpg_id: int, **kwargs):
        # todo: test code to see if series_dpg_id belongs to this plot ...
        #  this will need some tracking code when series are added
        dpg.configure_item(series_dpg_id, **kwargs)

    # pk; start tag >>>
    def add_area_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        fill: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [0, 0, 0, -255]),
        contribute_to_bounds: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_area_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            fill: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            contribute_to_bounds: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_area_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            fill=fill,
            contribute_to_bounds=contribute_to_bounds,
        )

        return _dpg_id

    def add_bar_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        weight: float = 1.0,
        horizontal: bool = False,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_bar_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            weight: float
                ...
            horizontal: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_bar_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            weight=weight,
            horizontal=horizontal,
        )

        return _dpg_id

    def add_candle_series(
        self, *,
        dates: t.Union[t.List[float], t.Tuple[float, ...]],
        opens: t.Union[t.List[float], t.Tuple[float, ...]],
        closes: t.Union[t.List[float], t.Tuple[float, ...]],
        lows: t.Union[t.List[float], t.Tuple[float, ...]],
        highs: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        bull_color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [0, 255, 113, 255]),
        bear_color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [218, 13, 79, 255]),
        weight: int = 0.25,
        tooltip: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_candle_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            dates: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            opens: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            closes: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            lows: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            highs: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            bull_color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            bear_color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            weight: int
                ...
            tooltip: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_candle_series(
            parent=self.dpg_id,
            dates=dates,
            opens=opens,
            closes=closes,
            lows=lows,
            highs=highs,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
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
        color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [0, 0, 0, -255]),
        thickness: float = 1.0,
        show_label: bool = True,
        vertical: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_drag_line

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            callback: t.Optional[Callback]
                Registers a callback.
            show: bool
                Attempt to render widget.
            default_value: t.Any
                ...
            color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            thickness: float
                ...
            show_label: bool
                ...
            vertical: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_drag_line(
            parent=self.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            callback=getattr(callback, 'fn', None),
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
        default_value: t.Any = dataclasses.field(default_factory=lambda: [0.0, 0.0]),
        color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [0, 0, 0, -255]),
        thickness: float = 1.0,
        show_label: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_drag_point

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            callback: t.Optional[Callback]
                Registers a callback.
            show: bool
                Attempt to render widget.
            default_value: t.Any
                ...
            color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            thickness: float
                ...
            show_label: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_drag_point(
            parent=self.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            callback=getattr(callback, 'fn', None),
            show=show,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
        )

        return _dpg_id

    def add_error_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        negative: t.Union[t.List[float], t.Tuple[float, ...]],
        positive: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        contribute_to_bounds: bool = True,
        horizontal: bool = False,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_error_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            negative: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            positive: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            contribute_to_bounds: bool
                ...
            horizontal: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_error_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            negative=negative,
            positive=positive,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            contribute_to_bounds=contribute_to_bounds,
            horizontal=horizontal,
        )

        return _dpg_id

    def add_heat_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
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
        bounds_min: t.Any = dataclasses.field(default_factory=lambda: [0.0, 0.0]),
        bounds_max: t.Any = dataclasses.field(default_factory=lambda: [1.0, 1.0]),
        format: str = '%0.1f',
        contribute_to_bounds: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_heat_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            rows: int
                ...
            cols: int
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            scale_min: float
                Sets the color scale min. Typically paired with the color scale widget scale_min.
            scale_max: float
                Sets the color scale max. Typically paired with the color scale widget scale_max.
            bounds_min: t.Any
                ...
            bounds_max: t.Any
                ...
            format: str
                ...
            contribute_to_bounds: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_heat_series(
            parent=self.dpg_id,
            x=x,
            rows=rows,
            cols=cols,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
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
        x: t.Union[t.List[float], t.Tuple[float, ...]],
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
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_histogram_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            bins: int
                ...
            bar_scale: float
                ...
            min_range: float
                ...
            max_range: float
                ...
            cumlative: bool
                ...
            density: bool
                ...
            outliers: bool
                ...
            contribute_to_bounds: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_histogram_series(
            parent=self.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
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
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_hline_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_hline_series(
            parent=self.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
        )

        return _dpg_id

    def add_image_series(
        self, *,
        texture_tag: t.Union[int, str],
        bounds_min: t.Union[t.List[float], t.Tuple[float, ...]],
        bounds_max: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        uv_min: t.Union[t.List[float], t.Tuple[float, ...]] = dataclasses.field(default_factory=lambda: [0.0, 0.0]),
        uv_max: t.Union[t.List[float], t.Tuple[float, ...]] = dataclasses.field(default_factory=lambda: [1.0, 1.0]),
        tint_color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [255, 255, 255, 255]),
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_image_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            texture_tag: t.Union[int, str]
                ...
            bounds_min: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            bounds_max: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            uv_min: t.Union[t.List[float], t.Tuple[float, ...]]
                normalized texture coordinates
            uv_max: t.Union[t.List[float], t.Tuple[float, ...]]
                normalized texture coordinates
            tint_color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_image_series(
            parent=self.dpg_id,
            texture_tag=texture_tag,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            uv_min=uv_min,
            uv_max=uv_max,
            tint_color=tint_color,
        )

        return _dpg_id

    def add_line_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_line_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_line_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
        )

        return _dpg_id

    def add_pie_series(
        self, *,
        x: float,
        y: float,
        radius: float,
        values: t.Union[t.List[float], t.Tuple[float, ...]],
        labels: t.Union[t.List[str], t.Tuple[str, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        format: str = '%0.2f',
        angle: float = 90.0,
        normalize: bool = False,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_pie_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: float
                ...
            y: float
                ...
            radius: float
                ...
            values: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            labels: t.Union[t.List[str], t.Tuple[str, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            format: str
                ...
            angle: float
                ...
            normalize: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_pie_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            radius=radius,
            values=values,
            labels=labels,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
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
        default_value: t.Any = dataclasses.field(default_factory=lambda: [0.0, 0.0]),
        offset: t.Union[t.List[float], t.Tuple[float, ...]] = dataclasses.field(default_factory=lambda: [0.0, 0.0]),
        color: t.Union[t.List[int], t.Tuple[int, ...]] = dataclasses.field(default_factory=lambda: [0, 0, 0, -255]),
        clamped: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_plot_annotation

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            default_value: t.Any
                ...
            offset: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            color: t.Union[t.List[int], t.Tuple[int, ...]]
                ...
            clamped: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_plot_annotation(
            parent=self.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            default_value=default_value,
            offset=offset,
            color=color,
            clamped=clamped,
        )

        return _dpg_id

    def add_scatter_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_scatter_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_scatter_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
        )

        return _dpg_id

    def add_series_value(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        source: t.Optional[Widget] = None,
        default_value: t.Any = dataclasses.field(default_factory=lambda: []),
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_series_value

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            default_value: t.Any
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_series_value(
            parent=self.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            source=getattr(source, 'dpg_id', 0),
            default_value=default_value,
        )

        return _dpg_id

    def add_shade_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y1: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y2: t.Any = dataclasses.field(default_factory=lambda: []),
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_shade_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y1: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            y2: t.Any
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_shade_series(
            parent=self.dpg_id,
            x=x,
            y1=y1,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            y2=y2,
        )

        return _dpg_id

    def add_stair_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_stair_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_stair_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
        )

        return _dpg_id

    def add_stem_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        y: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        indent: int = -1,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_stem_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            y: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            indent: int
                Offsets the widget to the right the specified number multiplied by the indent style.
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_stem_series(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            indent=indent,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
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
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_text_point

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: float
                ...
            y: float
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.
            x_offset: int
                ...
            y_offset: int
                ...
            vertical: bool
                ...

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_text_point(
            parent=self.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
            x_offset=x_offset,
            y_offset=y_offset,
            vertical=vertical,
        )

        return _dpg_id

    def add_vline_series(
        self, *,
        x: t.Union[t.List[float], t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_vline_series

        (autogenerated by: toolcraft/gui/scripts/dpg_plot_widget_method_generator.py)

        Args:
            x: t.Union[t.List[float], t.Tuple[float, ...]]
                ...
            label: str
                Overrides 'name' as label.
            user_data: t.Any
                User data for callbacks
            use_internal_label: bool
                Use generated internal label instead of user specified (appends ### uuid).
            before: t.Optional[Widget]
                This item will be displayed before the specified item in the parent.
            source: t.Optional[Widget]
                Overrides 'id' as value storage key.
            show: bool
                Attempt to render widget.

        Returns:
            t.Union[int, str]

        """

        _dpg_id = dpg.add_vline_series(
            parent=self.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            before=getattr(before, 'dpg_id', 0),
            source=getattr(source, 'dpg_id', 0),
            show=show,
        )

        return _dpg_id

    # pk; end tag >>>


# noinspection PyDefaultArgument
@dataclasses.dataclass(frozen=True)
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
