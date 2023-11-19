import asyncio
import dataclasses
import functools
import traceback
import typing as t
import numpy as np
try:
    import dearpygui.dearpygui as dpg
    # noinspection PyUnresolvedReferences,PyProtectedMember
    import dearpygui._dearpygui as internal_dpg
except ImportError:
    dpg = None
    internal_dpg = None

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
# from ._auto import PlotDragLine
# noinspection PyUnresolvedReferences
# from ._auto import PlotDragPoint
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
# from ._auto import PlotAnnotation
# noinspection PyUnresolvedReferences
# from ._auto import PlotLegend
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
# noinspection PyUnresolvedReferences
# from ._auto import PlotXAxis
# noinspection PyUnresolvedReferences
# from ._auto import PlotYAxis
# auto pk; end <<<


@dataclasses.dataclass(repr=False)
class Simple(_auto.SimplePlot):
    ...


@dataclasses.dataclass(repr=False)
class Legend(_auto.PlotLegend):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @property
    def registered_as_child(self) -> bool:
        return False


@dataclasses.dataclass(repr=False)
class XAxis(_auto.PlotXAxis):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @property
    def registered_as_child(self) -> bool:
        return False

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        if self.is_built:
            return internal_dpg.get_axis_limits(self.guid)
        else:
            raise Exception("Can get limits only when things are built ...")

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        if self.is_built:
            internal_dpg.fit_axis_data(axis=self.guid)
        else:
            self.post_build_fns.append(self.fit_data)

    def reset_ticks(self):
        if self.is_built:
            internal_dpg.reset_axis_ticks(self.guid)
        else:
            self.post_build_fns.append(self.reset_ticks)

    def set_limits(self, x_min: float, x_max: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        if self.is_built:
            internal_dpg.set_axis_limits(self.guid, x_min, x_max)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_limits, x_min, x_max)
            )

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        if self.is_built:
            internal_dpg.set_axis_limits_auto(self.guid)
        else:
            self.post_build_fns.append(self.set_limits_auto)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        if self.is_built:
            internal_dpg.set_axis_ticks(self.guid, label_pairs)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_ticks, label_pairs)
            )


@dataclasses.dataclass(repr=False)
class YAxis(_auto.PlotYAxis):

    @property
    def parent(self) -> "Plot":
        return self._parent

    @property
    def registered_as_child(self) -> bool:
        return False

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[PlotSeries]]:
        return PlotSeries,

    # noinspection PyMethodOverriding
    def __call__(self, widget: PlotSeries):
        # noinspection PyUnresolvedReferences
        if widget.label is not None and widget.label.find("#") == -1:
            # noinspection PyUnresolvedReferences
            if widget.label in [_.label for _ in self.children.values()]:
                # noinspection PyUnresolvedReferences
                raise Exception(
                    f"There already exists a plot_series with label "
                    f"`{widget.label}`",
                    f"Note that if you want to share label across multiple series "
                    f"then append `#<some unique name>` to label to make it unique "
                    f"per plot series",
                )
        super().__call__(widget=widget, before=None)

    def clear(self):
        # todo: with many points the dpg crashes and also things are slow ... so we just resort to clear
        #   note that if any PlotSeries is tagged we will not be releasing it :( ...
        #   check super code where we call delete() on each child .... that behaviour is now stopped ...
        # todo: raise issue with dpg that why lot of PlotSeries items deleted with guid causes crash
        # this override will avoid deleting each PlotSeries one after other .... making this fast
        self._children.clear()

    def get_limits(self) -> t.List[float]:
        """
        Refer:
        >>> dpg.get_axis_limits
        """
        if self.is_built:
            return internal_dpg.get_axis_limits(self.guid)
        else:
            raise Exception("Can get limits only when things are built ...")

    def fit_data(self):
        """
        Refer:
        >>> dpg.fit_axis_data
        """
        if self.is_built:
            internal_dpg.fit_axis_data(axis=self.guid)
        else:
            self.post_build_fns.append(self.fit_data)

    def reset_ticks(self):
        if self.is_built:
            internal_dpg.reset_axis_ticks(self.guid)
        else:
            self.post_build_fns.append(self.reset_ticks)

    def set_limits(self, y_min: float, y_max: float):
        """
        Refer:
        >>> dpg.set_axis_limits
        """
        if self.is_built:
            internal_dpg.set_axis_limits(self.guid, y_min, y_max)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_limits, y_min, y_max)
            )

    def set_limits_auto(self):
        """
        Refer:
        >>> dpg.set_axis_limits_auto
        """
        if self.is_built:
            internal_dpg.set_axis_limits_auto(self.guid)
        else:
            self.post_build_fns.append(self.set_limits_auto)

    def set_ticks(self, label_pairs: t.Any):
        """
        Refer:
        >>> dpg.set_axis_ticks
        """
        if self.is_built:
            internal_dpg.set_axis_ticks(self.guid, label_pairs)
        else:
            self.post_build_fns.append(
                functools.partial(self.set_ticks, label_pairs)
            )


@dataclasses.dataclass(repr=False)
class Annotation(_auto.PlotAnnotation):
    ...


@dataclasses.dataclass(repr=False)
class DragLine(_auto.PlotDragLine):
    ...


@dataclasses.dataclass(repr=False)
class DragPoint(_auto.PlotDragPoint):
    ...


@dataclasses.dataclass(repr=False)
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
                self._legend._parent = self
        return self._legend

    @property
    def x_axis(self) -> XAxis:
        if self._x_axis is None:
            with self:
                self._x_axis = XAxis()
                self._x_axis._parent = self
        return self._x_axis

    @property
    def y1_axis(self) -> YAxis:
        if self._y1_axis is None:
            with self:
                self._y1_axis = YAxis()
                self._y1_axis._parent = self
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
                self._y2_axis._parent = self
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
                self._y3_axis._parent = self
        return self._y3_axis

    @property
    def is_queried(self) -> bool:
        return internal_dpg.is_plot_queried(self.guid)

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
        return tuple(internal_dpg.get_plot_query_area(self.guid))

    def delete(self):

        # to delete any plot series
        self.legend.delete()
        self.x_axis.delete()
        self.y1_axis.delete()
        if self.num_of_y_axis == 2:
            self.y2_axis.delete()
        if self.num_of_y_axis == 3:
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


@dataclasses.dataclass(repr=False)
class SpecialPlot1D(Plot):
    x_indices: np.ndarray = None
    y_data: np.ndarray = None
    num_points_to_display: int = None
    subsampling_mode: t.Literal['none', 'max', 'min', 'mean'] = 'none'

    @property
    def x_axis_limit_update(self) -> t.Optional[t.Tuple[float, float]]:
        if self.is_visible:
            _new_x_limits = tuple(self.x_axis.get_limits())
            if _new_x_limits == self._previous_x_axis_limits:
                return None
            else:
                # noinspection PyAttributeOutsideInit
                self._previous_x_axis_limits = _new_x_limits
                # noinspection PyTypeChecker
                return _new_x_limits
        else:
            return None

    def init_validate(self):
        if self.x_indices is None:
            raise Exception("Please supply `x_indices`")
        if self.y_data is None:
            raise Exception("Please supply `y_data`")
        if self.num_points_to_display is None:
            raise Exception("Please supply `num_points_to_display`")

    def init(self):
        # call super
        super().init()

        # cast things
        self.x_indices = self.x_indices.astype(np.int32)
        self.y_data = self.y_data.astype(np.float32)

        # other values to store
        # noinspection PyAttributeOutsideInit
        self._line_seres = dict()  # type: t.Dict[int, LineSeries]
        # noinspection PyAttributeOutsideInit
        self._previous_x_axis_limits = (0., 0.)
        # noinspection PyAttributeOutsideInit
        self._fit_data_at_start = False

    def register_line_series(self, key: int, line_series: LineSeries):
        if key >= self.y_data.shape[0]:
            raise Exception(f"Value {key=} is too large !!!")
        if key in self._line_seres.keys():
            raise Exception(f"Value {key=} is already registered !!!")
        self._line_seres[key] = line_series

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):

        # just make sure that all line series are registered
        if len(self._line_seres) != self.y_data.shape[0]:
            raise Exception(
                f"please register {self.y_data.shape[0]} line series ... found {len(self._line_seres)} line series"
            )

        # now it is time to render children ... call super
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

        # if samples are less than samples to display then no need for fixed_update ...
        # we will do things here
        _x_indices = self.x_indices
        if len(_x_indices) <= self.num_points_to_display:
            from .. import gui
            _y_data = self.y_data
            for _k, _ls in self._line_seres.items():
                _ls.set_value([_x_indices, _y_data[_k]])
            del gui.Engine.fixed_update[self.guid]

    def sub_sampling_mode_fn(self) -> t.Callable:
        _subsampling_mode = self.subsampling_mode
        if _subsampling_mode == 'none':
            return lambda arr: arr[:, 0]
        elif _subsampling_mode == 'max':
            return lambda arr: np.max(arr, axis=1)
        elif _subsampling_mode == 'min':
            return lambda arr: np.min(arr, axis=1)
        elif _subsampling_mode == 'mean':
            return lambda arr: np.mean(arr, axis=1)
        else:
            raise Exception(f"Unsupported {_subsampling_mode=}")

    async def fixed_update(self):
        try:
            # ------------------------------------------------------------ 01
            # some init
            # ------------------------------------------------------------ 01.01
            # get update and return if update not needed
            _updates_x_axis_limits = self.x_axis_limit_update
            if _updates_x_axis_limits is None:
                return
            # ------------------------------------------------------------ 01.02
            # get vars
            _x_indices = self.x_indices
            _y_data = self.y_data
            _num_points_to_display = self.num_points_to_display
            _sub_sampling_mode_fn = self.sub_sampling_mode_fn()

            # ------------------------------------------------------------ 02
            # compute view buffers
            # ------------------------------------------------------------ 02.01
            # make _new_x_indices
            _x_view_min, _x_view_max = int(_updates_x_axis_limits[0]), int(_updates_x_axis_limits[1])
            # do this only once to fit data at start
            # we ignore 0th and last (i.e. -1) index as
            if not self._fit_data_at_start:
                _x_view_min, _x_view_max = _x_indices[1], _x_indices[-2]
            else:
                if _x_view_min < _x_indices[1]:
                    _x_view_min = _x_indices[1]
                if _x_view_max > _x_indices[-2]:
                    _x_view_max = _x_indices[-2]
            _samples_to_view = np.where((_x_indices >= _x_view_min) & (_x_indices <= _x_view_max))[0]
            _step_size = (len(_samples_to_view) // _num_points_to_display) + 1
            _samples_to_view = _samples_to_view[::_step_size]
            # ------------------------------------------------------------ 02.02
            # skip if not enough samples
            if len(_samples_to_view) == 0:
                return
            # ------------------------------------------------------------ 02.03
            # augment samples to view so that end samples are added
            # this helps to center the plot on double-click
            # The first and last value help us to keep x-bound intact so that double click on plot can center plot
            # The first two values and end two values help us to draw flat lines at end cases
            _samples_to_view = np.asarray(
                [0, _samples_to_view[0], *_samples_to_view, _samples_to_view[-1], len(_x_indices)-1], dtype=np.int32
            )
            _samples_to_view_len = len(_samples_to_view)
            # ------------------------------------------------------------ 02.04
            # create empty buffer for y data
            _new_y_data = np.zeros(shape=(_y_data.shape[0], _samples_to_view_len), dtype=_y_data.dtype)
            # compute for index 0
            _new_y_data[:, 0] = _sub_sampling_mode_fn(arr=_y_data[:, _samples_to_view[0]:_samples_to_view[1]])
            # compute for index 1 ... we copy from index 0 to make flat line
            _new_y_data[:, 1] = _new_y_data[:, 0]
            # compute for index 2 to (_samples_to_view_len-3)-1
            for _ in range(2, _samples_to_view_len-3):
                _new_y_data[:, _] = _sub_sampling_mode_fn(arr=_y_data[:, _samples_to_view[_]:_samples_to_view[_+1]])
            # compute for index _samples_to_view_len-2
            _new_y_data[:, _samples_to_view_len-2] = _sub_sampling_mode_fn(
                arr=_y_data[:, _samples_to_view_len-2:_samples_to_view_len-1]
            )
            # compute for index _samples_to_view_len-1 and _samples_to_view_len-3
            # ... we copy from index _new_x_indices_len-2 to make flat line
            _new_y_data[:, _samples_to_view_len-1] = _new_y_data[:, _samples_to_view_len-2]
            _new_y_data[:, _samples_to_view_len-3] = _new_y_data[:, _samples_to_view_len-2]
            # ------------------------------------------------------------ 02.05
            # await for async speedup
            await asyncio.sleep(0)

            # ------------------------------------------------------------ 03
            # lets make updates
            _new_x_indices = _x_indices[_samples_to_view]
            for _k, _ls in self._line_seres.items():
                _ls.set_value([_new_x_indices, _new_y_data[_k]])
                # await for async speedup
                await asyncio.sleep(0)

            # ------------------------------------------------------------ 04
            # do this only once to fit data at start
            if not self._fit_data_at_start:
                # noinspection PyAttributeOutsideInit
                self._fit_data_at_start = True
                # set x limits
                self.x_axis.fit_data()
                # set y limits
                self.y1_axis.fit_data()
                if self.num_of_y_axis > 1:
                    self.y2_axis.fit_data()
                if self.num_of_y_axis > 2:
                    self.y3_axis.fit_data()
                # await for async speedup
                await asyncio.sleep(0)

            # ------------------------------------------------------------ 05
            # async await for some time ... decides refresh rate
            await asyncio.sleep(0.)

        except Exception as _exp:
            traceback.print_exception(_exp)


@dataclasses.dataclass(repr=False)
class SubPlots(_auto.SubPlots):

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[Plot]]:
        return Plot,

    def __call__(self, widget: Plot, before: Plot = None):
        super().__call__(widget, before)
