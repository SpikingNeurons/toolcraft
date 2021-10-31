
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
