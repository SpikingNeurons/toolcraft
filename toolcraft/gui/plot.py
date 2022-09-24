import dataclasses
import functools
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .__base__ import PlotSeries, PlotItem
from . import _auto

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
    ...


@dataclasses.dataclass
class Legend(_auto.PlotLegend):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @parent.setter
    def parent(self, value: "Plot"):
        self._parent = value

    @property
    def registered_as_child(self) -> bool:
        return False


@dataclasses.dataclass
class XAxis(_auto.PlotXAxis):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @parent.setter
    def parent(self, value: "Plot"):
        self._parent = value

    @property
    def registered_as_child(self) -> bool:
        return False

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        if self.is_built:
            return internal_dpg.get_axis_limits(self.dpg_id)
        else:
            raise Exception("Can get limits only when things are built ...")

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        if self.is_built:
            internal_dpg.fit_axis_data(axis=self.dpg_id)
        else:
            self.post_build_fns.append(self.fit_data)

    def reset_ticks(self):
        if self.is_built:
            internal_dpg.reset_axis_ticks(self.dpg_id)
        else:
            self.post_build_fns.append(self.reset_ticks)

    def set_limits(self, ymin: float, ymax: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        if self.is_built:
            internal_dpg.set_axis_limits(self.dpg_id, ymin, ymax)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_limits, ymin, ymax)
            )

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        if self.is_built:
            internal_dpg.set_axis_limits_auto(self.dpg_id)
        else:
            self.post_build_fns.append(self.set_limits_auto)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        if self.is_built:
            internal_dpg.set_axis_ticks(self.dpg_id, label_pairs)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_ticks, label_pairs)
            )


@dataclasses.dataclass
class YAxis(_auto.PlotYAxis):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @parent.setter
    def parent(self, value: "Plot"):
        self._parent = value

    @property
    def registered_as_child(self) -> bool:
        return False

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[PlotSeries]]:
        return PlotSeries,

    # noinspection PyMethodOverriding
    def __call__(self, widget: PlotSeries):
        if widget.label is not None and widget.label.find("#") == -1:
            if widget.label in [_.label for _ in self.children.values()]:
                raise Exception(
                    f"There already exists a plot_series with label "
                    f"`{widget.label}`",
                    f"Note that if you want to share label across multiple series "
                    f"then append `#<some unique name>` to label to make it unique "
                    f"per plot series",
                )
        super().__call__(widget=widget, before=None)

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        if self.is_built:
            return internal_dpg.get_axis_limits(self.dpg_id)
        else:
            raise Exception("Can get limits only when things are built ...")

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        if self.is_built:
            internal_dpg.fit_axis_data(axis=self.dpg_id)
        else:
            self.post_build_fns.append(self.fit_data)

    def reset_ticks(self):
        if self.is_built:
            internal_dpg.reset_axis_ticks(self.dpg_id)
        else:
            self.post_build_fns.append(self.reset_ticks)

    def set_limits(self, ymin: float, ymax: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        if self.is_built:
            internal_dpg.set_axis_limits(self.dpg_id, ymin, ymax)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_limits, ymin, ymax)
            )

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        if self.is_built:
            internal_dpg.set_axis_limits_auto(self.dpg_id)
        else:
            self.post_build_fns.append(self.set_limits_auto)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        if self.is_built:
            internal_dpg.set_axis_ticks(self.dpg_id, label_pairs)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_ticks, label_pairs)
            )


@dataclasses.dataclass
class Annotation(_auto.PlotAnnotation):
    ...


@dataclasses.dataclass
class DragLine(_auto.PlotDragLine):
    ...


@dataclasses.dataclass
class DragPoint(_auto.PlotDragPoint):
    ...


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
    def restrict_children_to(self) -> t.Tuple[t.Type[PlotItem]]:
        return PlotItem,

    @property
    def legend(self) -> Legend:
        if self._legend is None:
            with self:
                self._legend = Legend()
                self._legend.parent = self
        return self._legend

    @property
    def x_axis(self) -> XAxis:
        if self._x_axis is None:
            with self:
                self._x_axis = XAxis()
                self._x_axis.parent = self
        return self._x_axis

    @property
    def y1_axis(self) -> YAxis:
        if self._y1_axis is None:
            with self:
                self._y1_axis = YAxis()
                self._y1_axis.parent = self
        return self._y1_axis

    @property
    def y2_axis(self) -> YAxis:
        if self._y2_axis is None:
            if self.num_of_y_axis not in [2, 3]:
                raise Exception(
                    f"You cannot access this property. "
                    f"Please set the field `num_of_y_axis` to be one of [2, 3]"
                )
            with self:
                self._y2_axis = YAxis()
                self._y2_axis.parent = self
        return self._y2_axis

    @property
    def y3_axis(self) -> YAxis:
        if self._y3_axis is None:
            if self.num_of_y_axis != 3:
                raise Exception(
                    f"You cannot access this property. "
                    f"Please set the field `num_of_y_axis` to be 3 to use this property"
                )
            with self:
                self._y3_axis = YAxis()
                self._y3_axis.parent = self
        return self._y3_axis

    @property
    def is_queried(self) -> bool:
        return internal_dpg.is_plot_queried(self.dpg_id)

    # noinspection PyMethodOverriding
    def __call__(self, widget: PlotItem, before: PlotItem = None):
        # these are not movable children and will be fixed for a given plot,
        # so we don't want them to be in `self.children`
        # but for build to happen we have taken care in property and post_build_runner
        if isinstance(widget, (Legend, XAxis, YAxis)):
            return

        # call super for normal process
        super().__call__(widget=widget, before=before)

    def init(self):
        # call super
        super().init()

        # add some important vars
        self._legend = None
        self._x_axis = None
        self._y1_axis = None
        self._y2_axis = None
        self._y3_axis = None

    def init_validate(self):
        # call super
        super().init_validate()
        # check num_of_y_axis
        if self.num_of_y_axis not in [1, 2, 3]:
            raise ValueError(
                "Please crosscheck the value for field num_of_y_axis. Should be one of [1, 2, 3]"
            )

    def get_query_area(self) -> t.Tuple[float, float]:
        """
        Refer:
        >>> dpg.get_plot_query_area
        """
        return tuple(internal_dpg.get_plot_query_area(self.dpg_id))

    def delete(self):

        # to delete any plot series
        self.legend.delete()
        self.x_axis.delete()
        self.y1_axis.delete()
        if self.num_of_y_axis == 2:
            self.y2_axis.delete()
        elif self.num_of_y_axis == 3:
            self.y2_axis.delete()
            self.y3_axis.delete()

        # super delete ... so that Plot is removed from parent ContainerWidget
        return super().delete()

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

        # calling super clear will remove all annotations, drag_lines and drag_points,
        # so we redefine here
        # clearing is deleting for annotations, drag_line, drag_plot
        _children = self.children
        for _k in list(_children.keys()):
            _c = _children[_k]
            if isinstance(_c, Annotation) and annotations:
                _c.delete()
            if isinstance(_c, DragLine) and drag_lines:
                _c.delete()
            if isinstance(_c, DragPoint) and drag_points:
                _c.delete()

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # now it is time to render children
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


@dataclasses.dataclass
class SubPlots(_auto.SubPlots):

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[Plot]]:
        return Plot,

    def __call__(self, widget: Plot, before: Plot = None):
        super().__call__(widget, before)
