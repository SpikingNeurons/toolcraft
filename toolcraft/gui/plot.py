import dataclasses
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .__base__ import PlotSeries, PlotItem
from . import _auto
from .. import error as e
from .. import util

# auto pk; start >>>
# noinspection PyUnresolvedReferences
from ._auto import HistogramSeries2D
# noinspection PyUnresolvedReferences
from ._auto import AreaSeries
# noinspection PyUnresolvedReferences
from ._auto import BarSeries
# noinspection PyUnresolvedReferences
from ._auto import CandleSeries
# noinspection PyUnresolvedReferences
from ._auto import DragLine
# noinspection PyUnresolvedReferences
from ._auto import DragPoint
# noinspection PyUnresolvedReferences
from ._auto import ErrorSeries
# noinspection PyUnresolvedReferences
from ._auto import HeatSeries
# noinspection PyUnresolvedReferences
from ._auto import HistogramSeries
# noinspection PyUnresolvedReferences
from ._auto import HLineSeries
# noinspection PyUnresolvedReferences
from ._auto import LineSeries
# noinspection PyUnresolvedReferences
from ._auto import PieSeries
# noinspection PyUnresolvedReferences
from ._auto import Annotation
# noinspection PyUnresolvedReferences
from ._auto import ScatterSeries
# noinspection PyUnresolvedReferences
from ._auto import ShadeSeries
# noinspection PyUnresolvedReferences
from ._auto import StairSeries
# noinspection PyUnresolvedReferences
from ._auto import StemSeries
# noinspection PyUnresolvedReferences
from ._auto import VLineSeries
# auto pk; end <<<


@dataclasses.dataclass
class Simple(_auto.SimplePlot):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"


@dataclasses.dataclass
class Legend(_auto.PlotLegend):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"


@dataclasses.dataclass
class XAxis(_auto.XAxis):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        internal_dpg.fit_axis_data(axis=self.dpg_id)

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
class YAxis(_auto.YAxis):

    @property
    @util.CacheResult
    def all_plot_series(self) -> t.Dict[str, PlotSeries]:
        return {}

    # noinspection PyMethodOverriding,PyUnresolvedReferences
    def __call__(self, plot_series: PlotSeries):
        if isinstance(plot_series, PlotSeries):
            if plot_series.label in self.all_plot_series.keys():
                e.validation.NotAllowed(
                    msgs=[
                        f"There already exists a plot_series with label "
                        f"`{plot_series.label}`",
                        f"Note that if you want to share label across multiple series "
                        f"then append `#<some unique name>` to label to make it unique "
                        f"per plot series",
                    ]
                )
            self.all_plot_series[plot_series.label] = plot_series
            plot_series.internal.parent = self
            if self.is_built:
                plot_series.build()
        else:
            e.code.ShouldNeverHappen(msgs=[f"unknown type {type(plot_series)}"])

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # call super
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

        # now it is time to render children
        for _ps in self.all_plot_series.values():
            _ps.build()

    def delete(self):
        self.clear()
        return super().delete()

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
        # internal_dpg.delete_item(item=self.dpg_id, children_only=True, slot=1)
        _ks = list(self.all_plot_series.keys())
        for _k in _ks:
            self.all_plot_series[_k].delete()

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
class Plot(_auto.Plot):
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

    width: int = -1

    height: int = 400

    num_of_y_axis: t.Literal[1, 2, 3] = 1

    @property
    @util.CacheResult
    def all_plot_items(self) -> t.Dict[str, PlotItem]:
        return {}

    @property
    @util.CacheResult
    def legend(self) -> Legend:
        _ret = Legend()
        _ret.internal.parent = self
        return _ret

    @property
    @util.CacheResult
    def x_axis(self) -> XAxis:
        _ret = XAxis()
        _ret.internal.parent = self
        return _ret

    @property
    @util.CacheResult
    def y1_axis(self) -> YAxis:
        _ret = YAxis()
        _ret.internal.parent = self
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
        _ret.internal.root = self.root
        return _ret

    @property
    def is_queried(self) -> bool:
        return internal_dpg.is_plot_queried(self.dpg_id)

    # noinspection PyMethodOverriding,PyUnresolvedReferences
    def __call__(self, plot_item: PlotItem):
        if isinstance(plot_item, PlotItem):
            if plot_item.label in self.all_plot_items.keys():
                e.validation.NotAllowed(
                    msgs=[
                        f"There already exists a plot_series with label "
                        f"`{plot_item.label}`"
                    ]
                )
            self.all_plot_items[plot_item.label] = plot_item
            plot_item.internal.parent = self
            if self.is_built:
                plot_item.build()
        else:
            e.code.ShouldNeverHappen(msgs=[f"unknown type {type(plot_item)}"])

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"

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

    def delete(self):
        self.clear()
        return super().delete()

    def get_query_area(self) -> t.Tuple[float, float]:
        """
        Refer:
        >>> dpg.get_plot_query_area
        """
        return tuple(internal_dpg.get_plot_query_area(self.dpg_id))

    def clear(
        self,
        y1_axis: bool = True,
        y2_axis: bool = True,
        y3_axis: bool = True,
        annotations: bool = True,
        drag_lines: bool = True,
        drag_points: bool = True,
    ):
        # to delete any plot series
        if y1_axis:
            self.y1_axis.clear()
        if self.num_of_y_axis == 2:
            if y2_axis:
                self.y2_axis.clear()
        elif self.num_of_y_axis == 3:
            if y2_axis:
                self.y2_axis.clear()
            if y3_axis:
                self.y3_axis.clear()

        # to delete annotations, drag_line, drag_plot
        _plot_items_keys = list(self.all_plot_items.keys())
        for _k in _plot_items_keys:
            _plot_item = self.all_plot_items[_k]
            if isinstance(_plot_item, Annotation) and annotations:
                _plot_item.delete()
            elif isinstance(_plot_item, DragLine) and drag_lines:
                _plot_item.delete()
            elif isinstance(_plot_item, DragPoint) and drag_points:
                _plot_item.delete()

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):

        # call super
        super().build_post_runner(
            hooked_method_return_value=hooked_method_return_value)

        # build other things
        # note that annotations if any will be taken care by build_post_runner as
        # they will eb residing in children
        self.legend.build()
        self.x_axis.build()
        self.y1_axis.build()
        if self.num_of_y_axis == 2:
            self.y2_axis.build()
        elif self.num_of_y_axis == 3:
            self.y2_axis.build()
            self.y3_axis.build()

        # now it is time to render children
        for _ps in self.all_plot_items.values():
            _ps.build()


@dataclasses.dataclass
class SubPlots(_auto.SubPlots):

    def __call__(self, widget: Plot, before: Plot = None):
        # we also need to add cells in row
        if isinstance(widget, Plot):
            super().__call__(widget, before)
        else:
            e.code.ShouldNeverHappen(msgs=[f"unknown type {type(widget)}"])

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"
