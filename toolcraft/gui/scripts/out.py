import dearpygui.dearpygui as dpg
import dataclasses
import typing as t
import Widget
import Callback
import numpy as np

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]


@dataclasses.dataclass(frozen=True)
class ___:

    def add_area_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        fill: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255),
        contribute_to_bounds: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_area_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            fill=fill,
            contribute_to_bounds=contribute_to_bounds,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_bar_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        weight: float = 1.0,
        horizontal: bool = False,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_bar_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            weight=weight,
            horizontal=horizontal,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_candle_series(
        self, *,
        dates: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        opens: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        closes: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        lows: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        highs: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        bull_color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 255, 113, 255),
        bear_color: t.Union[t.List[int], t.Tuple[int, ...]] = (218, 13, 79, 255),
        weight: int = 0.25,
        tooltip: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

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
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            bull_color=bull_color,
            bear_color=bear_color,
            weight=weight,
            tooltip=tooltip,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_drag_line(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        default_value: t.Any = 0.0,
        color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        vertical: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_drag_line

        Adds a drag line to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_drag_line(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
            vertical=vertical,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_drag_point(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        default_value: t.Any = (0.0, 0.0),
        color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_drag_point

        Adds a drag point to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_drag_point(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_error_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        negative: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        positive: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        contribute_to_bounds: bool = True,
        horizontal: bool = False,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

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
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            contribute_to_bounds=contribute_to_bounds,
            horizontal=horizontal,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_heat_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        rows: int,
        cols: int,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        scale_min: float = 0.0,
        scale_max: float = 1.0,
        bounds_min: t.Any = (0.0, 0.0),
        bounds_max: t.Any = (1.0, 1.0),
        format: str = '%0.1f',
        contribute_to_bounds: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_heat_series

        Adds a heat series to a plot.

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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

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
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            scale_min=scale_min,
            scale_max=scale_max,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            format=format,
            contribute_to_bounds=contribute_to_bounds,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_histogram_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
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
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_histogram_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
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
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_hline_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_hline_series

        Adds an infinite horizontal line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_hline_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_image_series(
        self, *,
        texture_tag: t.Union[int, str],
        bounds_min: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        bounds_max: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        uv_min: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0),
        uv_max: t.Union[t.List[float], t.Tuple[float, ...]] = (1.0, 1.0),
        tint_color: t.Union[t.List[int], t.Tuple[int, ...]] = (255, 255, 255, 255),
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_image_series

        Adds an image series to a plot.

        Args:
            texture_tag:
              ...
            bounds_min:
              ...
            bounds_max:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_image_series(
            parent=_y_axis.dpg_id,
            texture_tag=texture_tag,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            uv_min=uv_min,
            uv_max=uv_max,
            tint_color=tint_color,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_line_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_line_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_pie_series(
        self, *,
        x: float,
        y: float,
        radius: float,
        values: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        labels: t.Union[t.List[str], t.Tuple[str, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        format: str = '%0.2f',
        angle: float = 90.0,
        normalize: bool = False,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_pie_series

        Adds an pie series to a plot.

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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

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
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            format=format,
            angle=angle,
            normalize=normalize,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_plot_annotation(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        default_value: t.Any = (0.0, 0.0),
        offset: t.Union[t.List[float], t.Tuple[float, ...]] = (0.0, 0.0),
        color: t.Union[t.List[int], t.Tuple[int, ...]] = (0, 0, 0, -255),
        clamped: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_plot_annotation

        Adds an annotation to a plot.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_plot_annotation(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            default_value=default_value,
            offset=offset,
            color=color,
            clamped=clamped,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_scatter_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_scatter_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_series_value(
        self, *,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        source: t.Optional[Widget] = None,
        default_value: t.Any = (),
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_series_value

        Adds a plot series value.

        Args:
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
            source:
              Overrides 'id' as value storage key.
            default_value:
              ...
            y_axis_dim:
              ...

        Returns:
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_series_value(
            parent=_y_axis.dpg_id,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            source=0 if source is None else source.dpg_id,
            default_value=default_value,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_shade_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y1: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        y2: t.Any = [],
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_shade_series(
            parent=_y_axis.dpg_id,
            x=x,
            y1=y1,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            y2=y2,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_stair_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_stair_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_stem_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        y: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        indent: int = -1,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
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
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_stem_series(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            indent=indent,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_text_point(
        self, *,
        x: float,
        y: float,
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        x_offset: int = Ellipsis,
        y_offset: int = Ellipsis,
        vertical: bool = False,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_text_point

        Adds a label series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_text_point(
            parent=_y_axis.dpg_id,
            x=x,
            y=y,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            x_offset=x_offset,
            y_offset=y_offset,
            vertical=vertical,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
    def add_vline_series(
        self, *,
        x: t.Union[PLOT_DATA_TYPE, t.Tuple[float, ...]],
        label: str = None,
        user_data: t.Any = None,
        use_internal_label: bool = True,
        tag: t.Union[int, str] = 0,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        # kwargs: inspect._empty,
        y_axis_dim: int = 1,
    ) -> t.Union[int, str]:
        """
        Refer:
        >>> dpg.add_vline_series

        Adds an infinite vertical line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            user_data:
              User data for callbacks
            use_internal_label:
              Use generated internal label instead of user specified
              (appends ### uuid).
            tag:
              Unique id used to programmatically refer to the item.If
              label is unused this will be the label.
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
            t.Union[int, str]

        """

        _y_axis = self.get_y_axis(axis_dim=y_axis_dim)
        
        _dpg_id = dpg.add_vline_series(
            parent=_y_axis.dpg_id,
            x=x,
            label=label,
            user_data=user_data,
            use_internal_label=use_internal_label,
            tag=tag,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            # kwargs=kwargs,
        )
        
        return _dpg_id
        
