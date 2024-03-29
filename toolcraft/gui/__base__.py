"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import asyncio
import hashlib
import inspect
import sys
import traceback
import typing as t
import enum
import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future

import yaml

from . import asset
from . import util

# noinspection PyUnreachableCode
if False:
    from . import EnPlatform
    from . import BlockingTask
    from .. import gui
    from . import plot
    from ..marshalling import HashableClass


TWidget = t.TypeVar('TWidget', bound='Widget')
TYamlRepr = t.TypeVar('TYamlRepr', bound='YamlRepr')
COLOR_TYPE = t.Tuple[int, int, int, int]
# PLOT_DATA_TYPE = t.Union[t.List[float], t.Tuple[float, ...]]
PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]

try:
    # either borrow from settings
    from ..settings import PYC_DEBUGGING
except ImportError:
    # else in standalone set configuration here
    PYC_DEBUGGING = True

# container widget stack ... to add to parent automatically
_CONTAINER_WIDGET_STACK: t.List["ContainerWidget"] = []


class EnColor(enum.Enum):
    DEFAULT = (-1, -1, -1, -1)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    GREY = (127, 127, 127, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    RED = (255, 0, 0, 255)


class EscapeWithContext:

    def __init__(self):
        self._backup = None

    def __enter__(self):
        global _CONTAINER_WIDGET_STACK
        self._backup = _CONTAINER_WIDGET_STACK
        _CONTAINER_WIDGET_STACK = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _CONTAINER_WIDGET_STACK
        _CONTAINER_WIDGET_STACK = self._backup


@dataclasses.dataclass(repr=False)
class _WidgetDpg(abc.ABC):
    """
    This class is just to keep all dpg related things in one place ...
    Anything specific to our API will go in Widget class
    """

    @property
    def post_build_fns(self) -> t.List[t.Callable]:
        return self._post_build_fns

    @property
    def guid(self) -> int:
        try:
            # noinspection PyUnresolvedReferences
            return self._guid
        except AttributeError as _ae:
            # for any other gui interface update this ....
            # for dearpygui we can safely use this
            dpg.create_context()
            # noinspection PyAttributeOutsideInit
            self._guid = dpg.generate_uuid()
            return self._guid

    @property
    def dpg_state(self) -> t.Dict[str, t.Union[bool, t.List[int]]]:
        return internal_dpg.get_item_state(self.guid)

    @property
    def dpg_config(self) -> t.Dict[str, t.Union[bool, t.List[int]]]:
        return internal_dpg.get_item_configuration(self.guid)

    @property
    def dpg_info(self) -> t.Dict[str, t.Any]:
        return internal_dpg.get_item_info(self.guid)

    @property
    def is_built(self) -> bool:
        return self._is_built

    @property
    def is_hovered(self) -> bool:
        return self.dpg_state['hovered']

    @property
    def is_active(self) -> bool:
        return self.dpg_state['active']

    @property
    def is_focused(self) -> bool:
        return self.dpg_state['focused']

    @property
    def is_clicked(self) -> bool:
        return self.dpg_state['clicked']

    @property
    def is_left_clicked(self) -> bool:
        return self.dpg_state['left_clicked']

    @property
    def is_right_clicked(self) -> bool:
        return self.dpg_state['right_clicked']

    @property
    def is_middle_clicked(self) -> bool:
        return self.dpg_state['middle_clicked']

    @property
    def is_visible(self) -> bool:
        return self.dpg_state['visible']

    @property
    def is_edited(self) -> bool:
        return self.dpg_state['edited']

    @property
    def is_activated(self) -> bool:
        return self.dpg_state['activated']

    @property
    def is_deactivated(self) -> bool:
        return self.dpg_state['deactivated']

    @property
    def is_deactivated_after_edit(self) -> bool:
        return self.dpg_state['deactivated_after_edit']

    @property
    def is_toggled_open(self) -> bool:
        return self.dpg_state['toggled_open']

    @property
    def is_ok(self) -> bool:
        return self.dpg_state['ok']

    @property
    def is_shown(self) -> bool:
        return self.dpg_config['show']

    @property
    def is_enabled(self) -> bool:
        return self.dpg_config['enabled']

    # @property
    # def pos(self) -> t.Tuple[int, int]:
    #     return tuple(self.dpg_state['pos'])

    @property
    def available_content_region(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state['content_region_avail'])

    @property
    def rect_size(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state['rect_size'])

    @property
    def rect_min(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state['rect_min'])

    @property
    def rect_max(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state['rect_max'])

    @property
    def dataclass_field_names(self) -> t.List[str]:
        return [_.name for _ in dataclasses.fields(self)]

    @classmethod
    def __init_subclass__(cls, **kwargs):

        # hookup build
        util.HookUp(
            cls=cls,
            method=cls.build,
            pre_method=cls.build_pre_runner,
            post_method=cls.build_post_runner,
        )

    def __post_init__(self):
        # call guid to set it
        _ = self.guid
        # some internal vars
        self._post_build_fns = []
        self._is_built = False
        # init pipeline
        self.init_validate()
        self.init()

    def __setattr__(self, key, value):
        from .form import Form
        if key in self.dataclass_field_names:
            # needed as this is dataclass and class building happens before
            # __post_init__ will add this attribute to class
            try:
                _is_built = self.is_built
            except AttributeError as _ae:
                _is_built = False
            # this might not always work especially when key is custom ...
            # in that case catch exception and figure out how to handle
            if _is_built:
                # The default behaviour is to update configure the dpg item but
                # note that Form is not a typical Widget and is subclass of CollapsingHeader
                # It can have more dataclass fields than provided by dpg
                if isinstance(self, Form):
                    if key in internal_dpg.get_item_configuration(self.guid).keys():
                        internal_dpg.configure_item(self.guid, **{key: value})
                else:
                    internal_dpg.configure_item(self.guid, **{key: value})
        # any other attribute that is not field
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"{self.guid}:{self.__class__.__name__}"

    def clone(self) -> "_WidgetDpg":
        _kwargs = dict()
        for _k in self.dataclass_field_names:
            _v = getattr(self, _k)
            if isinstance(_v, _WidgetDpg):
                _v = _v.clone()
            _kwargs[_k] = _v
        # noinspection PyArgumentList
        return self.__class__(**_kwargs)

    def init_validate(self):

        from .form import Form

        # loop over fields
        for f_name in self.dataclass_field_names:
            # get value
            v = getattr(self, f_name)

            # check if Widget and only allow if Form
            if isinstance(v, Widget):
                if not isinstance(self, Form):
                    raise Exception(
                        f"Check field {self.__class__}.{f_name}",
                        f"You cannot have instance of class {v.__class__} as "
                        f"dataclass fields of {self.__class__}.",
                        f"This is only allowed for {Form} where we only allow "
                        f"{Widget}"
                    )

    def init(self):
        ...

    def delete(self):
        """
        Note that this will be scheduled for deletion via destroy with help of WidgetEngine
        """
        _guid = self.guid

        # adapt widget engine
        # unregister update
        try:
            del Engine.update[_guid]
        except KeyError:
            ...
        # unregister fixed_update
        try:
            del Engine.fixed_update[_guid]
        except KeyError:
            ...

        # delete the dpg UI counterpart .... skip line series
        # from .plot import LineSeries
        dpg.delete_item(item=_guid, children_only=False, slot=-1)

        # todo: make _widget unusable ... figure out

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            # noinspection PyUnresolvedReferences
            raise Exception(
                f"Widget {self} is already built and registered with:",
                f"'parent': {self.parent}"
            )

    @abc.abstractmethod
    def build(self) -> int:
        ...

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # if None raise error ... we expect int
        if hooked_method_return_value is None:
            raise Exception(f"We expect build to return int which happens to be guid")

        # test if remaining important internals are set
        from . import window
        if isinstance(self, window.Window):
            if self._dash_board is None:
                raise Exception(
                    f"We expect 'dash_board' property for instance of class {self.__class__} to be set by now"
                )
        elif isinstance(self, Widget):
            if self._parent is None:
                raise Exception(
                    f"We expect 'parent' property for instance of class {self.__class__} to be set by now"
                )
        else:
            raise Exception(
                f"Not supported type {self.__class__}"
            )

        # set guid
        assert self.guid == hooked_method_return_value, "was expecting this to be same"

        # indicate that things are build
        assert not self._is_built, "was expecting this to be False"
        # noinspection PyAttributeOutsideInit
        self._is_built = True

        # call post_build_fns
        if bool(self.post_build_fns):
            for _fn in self.post_build_fns:
                _fn()
            self.post_build_fns.clear()

        # register in WidgetEngine
        if Widget.update != self.__class__.update:
            Engine.update[self.guid] = self
        if Widget.fixed_update != self.__class__.fixed_update:
            Engine.fixed_update[self.guid] = self

    def get_value(self) -> t.Any:
        """
        Refer:
        >>> dpg.get_value
        """
        return internal_dpg.get_value(self.guid)

    def set_value(self, value: t.Any):
        """
        Refer:
        >>> dpg.set_value
        """
        return internal_dpg.set_value(self.guid, value)

    def set_x_scroll(self, value: float):
        """
        Refer:
        >>> dpg.set_x_scroll
        """
        return internal_dpg.set_x_scroll(self.guid, value)

    def get_x_scroll(self) -> float:
        """
        Refer:
        >>> dpg.get_x_scroll
        """
        return internal_dpg.get_x_scroll(self.guid)

    def get_x_scroll_max(self) -> float:
        """
        Refer:
        >>> dpg.get_x_scroll_max
        """
        return internal_dpg.get_x_scroll_max(self.guid)

    def set_y_scroll(self, value: float):
        """
        Refer:
        >>> dpg.set_y_scroll
        """
        return internal_dpg.set_y_scroll(self.guid, value)

    def get_y_scroll(self) -> float:
        """
        Refer:
        >>> dpg.get_y_scroll
        """
        return internal_dpg.get_y_scroll(self.guid)

    def show_debug(self):
        """
        Refer:
        >>> dpg.show_item_debug
        """
        return internal_dpg.show_item_debug(self.guid)

    def unstage(self):
        """
        Refer:
        >>> dpg.unstage
        """
        return internal_dpg.unstage(self.guid)

    def get_y_scroll_max(self) -> float:
        """
        Refer:
        >>> dpg.get_y_scroll_max
        """
        return internal_dpg.get_y_scroll_max(self.guid)

    def reset_pos(self):
        internal_dpg.reset_pos(self.guid)

    def show_widget(self):
        """
        Refer:
        >>> dpg.show_item
        """
        internal_dpg.configure_item(self.guid, show=True)

    def hide_widget(self):
        """
        Refer:
        >>> dpg.hide_item
        """
        internal_dpg.configure_item(self.guid, show=False)

    def bind_theme(self, theme: asset.Theme):
        dpg.bind_item_theme(item=self.guid, theme=theme.get())

    def set_widget_configuration(self, **kwargs):
        # if any value is widget then get its guid
        _new_kwargs = {}
        for _k in kwargs.keys():
            _v = kwargs[_k]
            if isinstance(_v, Widget):
                _v = _v.guid
            _new_kwargs[_k] = _v
        # configure
        dpg.configure_item(item=self.guid, **_new_kwargs)

    def display_raw_configuration(self) -> t.Dict:
        """
        Note that raw guid is not treated
        """
        return dpg.get_item_configuration(item=self.guid)

    def focus(self):
        """
        Refer:
        >>> dpg.focus_item
        """
        dpg.focus_item(self.guid)

    def enable(self):
        """
        Refer:
        >>> dpg.enable_item
        """
        internal_dpg.configure_item(self.guid, enabled=True)

    def disable(self):
        """
        Refer:
        >>> dpg.disable_item
        """
        internal_dpg.configure_item(self.guid, enabled=False)

    async def fixed_update(self):
        ...

    async def update(self):
        """
        todo: async update that can have await ... (Try this is try_* rough work first ...)
          A method run can be spread over multiple frames where
            only part of code until next await executes in a given frame ...
          Note that also deletion needs to happen after entire update is executed ...
            or maybe for every await in update method check if deletion is requested

        """
        ...


@dataclasses.dataclass
class BlockingTask:
    """
    Note multi-threading for IO and multi-processing for CPU intensive tasks
    https://engineering.contentsquare.com/2018/multithreading-vs-multiprocessing-in-python/

    multi-threading ... use for infinite threads that are light weight nut run concurrently
                        note that asyncio syntax is great but we need to await and make sure that code
                        within await is fast
    multiprocessing ... True parallelism but there is overhead to launch threads or else need to maintain pool
                        of fix threads

    Note that AwaitableTask tasks need you to await ... so keep fast running code between two awaits
    Note AwaitableTask and BlockingTask with concurrent=True is same .... with only difference that you need not
    care for using await syntax and normal blocking function run in interleaved fashion
    """

    fn: t.Callable
    # if true will use multi-threading else will use multiprocessing
    concurrent: bool
    fn_kwargs: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    @property
    def future(self) -> Future:
        return self._future

    def __post_init__(self):
        # validation
        if inspect.iscoroutinefunction(self.fn):
            raise Exception(f"The function {self.fn} should not be async i.e. awaitable ...")

        # set some vars
        self._future = None

    async def _run_concurrently(self):
        """
        This method will dispatch job to ProcessPoolExecutor or ThreadPoolExecutor and quickly return
        """
        try:
            if self._future is not None:
                raise Exception("_future must be None")

            if self.concurrent:
                _future = Engine.thread_pool_executor.submit(self.fn, **self.fn_kwargs)
            else:
                _future = Engine.process_pool_executor.submit(self.fn, **self.fn_kwargs)

            self._future = _future

        except SystemError as _e:
            # todo: see AwaitableTask._run_concurrently
            ...
        except Exception as _e:
            _exc_type, _exc_obj, _exc_tb = sys.exc_info()
            traceback.print_exception(_exc_type, _exc_obj, _exc_tb)
            raise Exception(
                f"The blocking async task (concurrent={self.concurrent}) has failed",
                {
                    "module": self.__module__,
                    "class": self.__class__,
                    "_exc_type": str(_exc_type),
                    "_exc_obj": str(_exc_obj),
                    "_exc_tb": str(_exc_tb),
                },
                _e
            )

    def add_to_task_queue(self):
        Engine.task_queue.put_nowait(self)


@dataclasses.dataclass
class AwaitableTask(abc.ABC):

    """
    Note that AwaitableTask tasks need you to await ... so keep fast running code between two awaits
    Note AwaitableTask and BlockingTask with concurrent=True is same .... with only difference that you need not
    care for using await syntax and normal blocking function run in interleaved fashion

    This makes call in try catch so that any errors in async task can be grabbed ...

    Note that this executes in same process and thread and you have full control as it is interlaced
    execution and ideal for gui

    In current form only lite weight fn can be used as we use concurrency and there is no threading so any delays
    will stall UI .... so need to have ThreadPoolExecutor and ProcessPoolExecutor to do things in parallel process or
    parallel thread instead of concurrent interlaced execution ...

    todo: also animations and transitions can be handled with this ...
      i.e. without need for ThreadPoolExecutor and ProcessPoolExecutor
      Note that we need to remove widget from async updates via `widget.stop_async_update()` ...
        so this needs to be done in fn ... this will allow us to track lot of widgets for async updates

    todo: implement ThreadPoolExecutor (for IO-bound tasks) and ProcessPoolExecutor (for CPU-bound tasks)
      use for CPU-bound and IO-bound task task ... but note that you have no access to vars in main process (may-be)
      might need to make this more general so move to `toolcraft.job`
      most likely make fn await on these threads after deciding on API and understanding asyncio pool's
      Refer: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor

    todo: when widgets are deleted the fn sill raise SystemError as calls to dpg_internal will fail
      so we bypass it here ... make sure to take care of things as `AsyncUpdateFn.fn` are not aware of
      widget deletions plus `AsyncUpdateFn.fn` can work with multiple widgets so do not have any magic
      solution ...
      The more complex solution will be Unity style where all widgets have life cycle
      ... setup, update, final
      ... but this will require having async task run for each widget and build complex Unity3D system
    """

    fn: t.Callable
    fn_kwargs: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    def __post_init__(self):
        # validation
        if not inspect.iscoroutinefunction(self.fn):
            raise Exception(f"The function {self.fn} needs to be async i.e. awaitable ...")

        # set some vars
        self._is_completed = False

    async def _run_concurrently(self):
        try:
            if self._is_completed:
                raise Exception("_is_completed must be false")
            _ret = await self.fn(**self.fn_kwargs)
            if self._is_completed:
                raise Exception(
                    "_is_completed must be false",
                    f"looks like {self.fn} has set it ..."
                )
            if _ret is not None:
                raise Exception(
                    f"The fn {self.fn} must return None",
                    "Please do not return anything"
                )
            self._is_completed = True
        except SystemError as _e:
            # todo: when widgets are deleted the fn sill raise SystemError as calls to dpg_internal will fail
            #   so we bypass it here ... make sure to take care of things as `AsyncUpdateFn.fn` are not aware of
            #   widget deletions plus `AsyncUpdateFn.fn` can work with multiple widgets so do not have any magic
            #   solution ...
            #   The more complex solution will be Unity style where all widgets have life cycle
            #   ... setup, update, final
            #   ... but this will require having async task run for each widget and build complex Unity3D system
            ...
        except Exception as _e:
            _exc_type, _exc_obj, _exc_tb = sys.exc_info()
            traceback.print_exception(_exc_type, _exc_obj, _exc_tb)
            raise Exception(
                "The awaitable async task has failed",
                {
                    "module": self.__module__,
                    "class": self.__class__,
                    "_exc_type": str(_exc_type),
                    "_exc_obj": str(_exc_obj),
                    "_exc_tb": str(_exc_tb),
                },
                _e
            )

    def add_to_task_queue(self):
        Engine.task_queue.put_nowait(self)


class Engine:
    """
    > tags
    We save tagged widgets for all windows and widgets to access
    todo: check contextvars ... might not be needed for tag ....
      but can be useful when we want simple names which are repeatable
      across many windows ... this will keep tags have readable names but based on
      context we can bring uniqueness ... especially useful for asyncio
      https://docs.python.org/3/library/contextvars.html

    > lifecycle
    todo: Explore making game engine style async project inspired by unity or find any opensource solution in python
      https://docs.unity3d.com/ScriptReference/MonoBehaviour.html
      Implement MonoBehaviour things like:
      + Start - Use this for initialization
      + Update - Update is called once per frame
      + FixedUpdate - Frame-rate independent message for physics calculations
                      has the frequency of the physics system; it is called every fixed frame-rate frame
      + LateUpdate - LateUpdate is called every frame, if the Behaviour is enabled.
      + OnGUI - OnGUI is called for rendering and handling GUI events.
      + OnDisable - This function is called when the behaviour becomes disabled.
      + OnEnable - This function is called when the object becomes enabled and active.
      + print - Logs message to the Unity Console (identical to Debug.Log).
      By figuring out which method is overridden we can decide to call it ...
    """

    # --------------------------------- 01
    # lifecycle method - updates every frame
    update: t.Dict[int, "Widget"] = {}
    # lifecycle method - updates at fix frequency ... still to improve
    fixed_update: t.Dict[int, "Widget"] = {}

    # --------------------------------- 02
    # queue that can process AwaitableTask and BlockingTask
    task_queue: asyncio.Queue = asyncio.Queue()

    # --------------------------------- 03
    # save reference to dashboard
    dashboard: t.Optional["Dashboard"] = None

    # --------------------------------- 04
    # note we have kept worker=1 so that logs will not pollute
    # todo: increase number of workers when logging is done entirely to files so that stdout doesn't get polluted
    #   especially useful for process_pool_executor
    # note that any tasks that will be executed by thread_pool_executor will slow main thread
    # todo: test if tasks executed by thread_pool_executor truly slow down main thread
    # note only purpose of thread_pool_executor is so that ordinary non awaitable function can be run in async
    #   for awaitable functions anyways we have AwaitableTask .... but remember that there needs to be small
    #   pauses between await
    # used by BlockingTask when concurrent=True
    thread_pool_executor = ThreadPoolExecutor(max_workers=4)
    # used by BlockingTask when concurrent=False
    process_pool_executor = ProcessPoolExecutor(max_workers=4)

    @classmethod
    async def lifecycle_loop(cls):
        """
        Instead of maintaining finite worker pool (made via _loop.create_task) that processes async_update_fns_queue
        ... we launch task as and when the async_update_fn is available i.e. infinite tasks are spawned
            but note that this runs concurrently in main gui thread
        ... this seems okay as tasks are lightweight and gui all tasks need to be concurrent
            (also we might have a lot of them)

        todo: explore `_loop.to_thread` good for io bound tasks ...
          also good for cpu-bound if external lib releases gil-locks like cython ...
          NOTE: that this will spawn real threads
            so not ideal for gui
            but good for io and cpu tasks that release gil locks

        todo: also investigate
          ThreadPoolExecutor (for IO-bound tasks) and .... (`_loop.to_thread` actually uses this)
          ProcessPoolExecutor (for CPU-bound tasks)
          https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor

        todo: investigate for using all CPU cores to run lifecycle in parallel
          ThreadPoolExecutor (for IO-bound tasks) and ProcessPoolExecutor (for CPU-bound tasks)

        """
        try:

            # this will run infinitely ...
            while True:

                # await
                await asyncio.sleep(0)

                # call update phase
                # todo: asyncio.create_task or asyncio.to_thread
                for _ in Engine.update.values():
                    await _.update()

                # todo: other phases nut need to rethink design ...
                #   note that destroy for widget.delete is not effective
                # # call update_pause phase
                # for _ in Engine.update_pause:
                #     del Engine.update[_]
                # Engine.update_pause.clear()
                #
                # # call update_resume phase
                # for _ in Engine.update_resume:
                #     Engine.update[_.uid] = _
                # Engine.update_resume.clear()
                #
                # # call destroy ... if there is something for deletion ...
                # # todo: when closed things will not get deleted appropriately
                # for _ in Engine.destroy:
                #     _.delete()
                # Engine.destroy.clear()

        except Exception as _e:
            raise Exception(f"Exception in {Engine.lifecycle_loop}", _e)

    @classmethod
    async def lifecycle_physics_loop(cls):
        """
        todo: pending ... the destroy in main_lifecycle can cause problems
        """
        try:
            # this will run infinitely ...
            while True:

                # await (physics will run at 2 Hz)
                # todo: make sure that all fixed_update's happen in 0.5 seconds
                await asyncio.sleep(0.5)

                # call fixed_update phase
                # todo: asyncio.create_task or asyncio.to_thread
                for _ in Engine.fixed_update.values():
                    _res = await _.fixed_update()
        except Exception as _e:
            raise Exception(f"Exception in {Engine.lifecycle_physics_loop}", _e)

    @classmethod
    async def task_runner_loop(cls):
        """
        for now we use .... improve to use threads if possible or something else

        - can have variation for io tasks, cpu tasks and tasks in thread where need to
          explore removing gil locks in cython
        """
        try:
            while True:
                _awaitable_task: t.Union[AwaitableTask, BlockingTask] = await Engine.task_queue.get()
                # noinspection PyProtectedMember
                asyncio.create_task(_awaitable_task._run_concurrently())
                Engine.task_queue.task_done()
        except Exception as _e:
            raise Exception(f"Exception in {Engine.task_runner_loop}", _e)

    @classmethod
    async def dpg_loop(cls):
        try:
            if PYC_DEBUGGING:
                while internal_dpg.is_dearpygui_running():
                    # add this extra line for callback debug
                    # https://pythonrepo.com/repo/hoffstadt-DearPyGui-python-graphical-user-interface-applications
                    dpg.run_callbacks(dpg.get_callback_queue())
                    # dpg frame render
                    internal_dpg.render_dearpygui_frame()
                    await asyncio.sleep(0)
            else:
                while internal_dpg.is_dearpygui_running():
                    # dpg frame render
                    internal_dpg.render_dearpygui_frame()
                    await asyncio.sleep(0)
        except Exception as _e:
            raise Exception(f"Exception in {Engine.dpg_loop}", _e)

    @classmethod
    async def main(cls):
        """
        Refer:
        >>> dpg.start_dearpygui()

        Also explore `asyncio.to_thread` which will launch io thread
        + useful for io-bound tasks
        + for cpu-bound with python no use due to GIL but can be used with external libs without that release gil-locks
          then this can be used for cpu-bound too ...
        >>> asyncio.to_thread

        todo: implement ThreadPoolExecutor (for IO-bound tasks) and ProcessPoolExecutor (for CPU-bound tasks)
          use for CPU-bound and IO-bound task task ... but note that you have no access to vars in main process (may-be)
          might need to make this more general so move to `toolcraft.job`
          most likely make fn await on these threads after deciding on API and understanding asyncio pool's
          Refer: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
                 https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread
        """
        # ----------------------------------------------------------- 01
        # create tasks dpg brad and butter
        # todo: use asyncio.to_thread but due to GIL no use hence only use for IO ... some hope if this lib is cython
        _dpg = asyncio.create_task(cls.dpg_loop())

        # ----------------------------------------------------------- 02
        # todo: work this out when we want to have lifecycle for widgets
        _lifecycle = asyncio.create_task(cls.lifecycle_loop())
        _lifecycle_physics = asyncio.create_task(cls.lifecycle_physics_loop())

        # ----------------------------------------------------------- 03
        # todo this loop can go on parallel processes where they will loop infinitely and wait for tasks
        #   but may be not overhead as we will have different tasks coming at rare intervals and we do not wat top
        #   rob cpus from tasks that run on different cpus
        _task_runner = asyncio.create_task(cls.task_runner_loop())

        # ----------------------------------------------------------- 04
        # fake task to just trigger the queue creation
        # _blocking_task = BlockingTask(fn=lambda: None, concurrent=False)
        # _blocking_task.add_to_task_queue()

        # ----------------------------------------------------------- 05
        # await on dpg task and cancel update task
        await _dpg
        # _lifecycle.cancel()
        # _lifecycle_physics.cancel()
        _task_runner.cancel()

        # ----------------------------------------------------------- 06
        # shutdown pool executors
        cls.thread_pool_executor.shutdown(wait=True)
        cls.process_pool_executor.shutdown(wait=True)

    @classmethod
    def run(cls, dash: "Dashboard"):
        # -------------------------------------------------- 01
        # setup dpg
        dpg.create_context()
        dpg.configure_app(manual_callback_management=PYC_DEBUGGING)
        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        if not internal_dpg.is_viewport_ok():
            raise RuntimeError("Viewport was not created and shown.")

        # -------------------------------------------------- 02
        # make sure that dashbord is not alread set
        if cls.dashboard is None:
            cls.dashboard = dash
        else:
            raise Exception(
                "Was not expecting dashboard to be set already"
            )

        # -------------------------------------------------- 03
        # call build and indicate build is done
        dash.build()

        # -------------------------------------------------- 04
        # call gui main code in async
        asyncio.run(cls.main(), debug=PYC_DEBUGGING, )

        # -------------------------------------------------- 05
        # destroy
        dpg.destroy_context()


@dataclasses.dataclass(repr=False)
class Widget(_WidgetDpg, abc.ABC):
    """
    todo: add async update where widget can be updated via long running python code
      need to also stop tracking if widget is closed in between ...
      also if selected it should resume based on what long running code is doing ...
      may be need to register job with gui subsystem ...
      VERY USEFUL FEATURE AND MUCH NEEDED ... but implementation can be delayed
    """

    @property
    def parent(self) -> "ContainerWidget":
        try:
            return self._parent
        except AttributeError as _ae:
            raise Exception(
                "You need to set self._parent to access parent property ..."
            )

    @property
    def root(self) -> "gui.window.Window":
        return self.parent.root

    @property
    def dash_board(self) -> "Dashboard":
        """
        root is always Window and Window has Dashboard
        """
        return self.root.dash_board

    @property
    def registered_as_child(self) -> bool:
        return True

    @property
    def is_in_gui_with_mode(self) -> bool:
        return bool(_CONTAINER_WIDGET_STACK)

    @property
    def restrict_parents_to(self) -> t.Tuple[t.Type["ContainerWidget"]]:
        # noinspection PyTypeChecker
        return ContainerWidget,

    @property
    def does_exist(self) -> bool:
        """
        Will return False if self.delete() is called as the dpg item will no longer be available
        """
        return dpg.does_item_exist(item=self.guid)

    def __enter__(self: TWidget) -> TWidget:

        # call on_enter
        self.on_enter()

        # return
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        todo handle exc_type, exc_val, exc_tb args for exception

        Args:
            exc_type:
            exc_val:
            exc_tb:

        Returns:

        """

        # call on exit
        self.on_exit(exc_type, exc_val, exc_tb)

    def __eq__(self, other):
        """
        Helps in finding children
        """
        return self.guid == other.guid

    # noinspection PyMethodOverriding
    def __call__(self):
        raise Exception(
            f"__call__ is blocked for class {self.__class__} ... "
            f"this is only allowed for {ContainerWidget}"
        )

    def init(self):
        global _CONTAINER_WIDGET_STACK

        # call super
        super().init()

        # set some vars
        # noinspection PyAttributeOutsideInit
        self._parent = None
        # noinspection PyAttributeOutsideInit
        self._dash_board = None
        # noinspection PyAttributeOutsideInit
        self._is_built = False

        # if there is parent container that is available via with context then add to it
        # this is only for using with `with` syntax
        if self.is_in_gui_with_mode:
            _CONTAINER_WIDGET_STACK[-1](widget=self)

    def on_enter(self):
        raise Exception(
            f"Widget for class {self.__class__} is not a {ContainerWidget.__name__!r} so "
            f"you cannot use with context"
        )

    def on_exit(self, exc_type, exc_val, exc_tb):
        raise Exception(
            f"Widget for class {self.__class__} is not a {ContainerWidget.__name__!r} so "
            f"you cannot use with context"
        )

    def get_user_data(self) -> 'USER_DATA':
        """
        Almost every subclassed Widget will have this field, but we cannot have it here
        as dataclass mechanism does not allow it. So we offer this utility method

        todo: raise issue with dpg for why they need user_data for Widgets which do
          not support any callbacks
        """
        try:
            # noinspection PyUnresolvedReferences
            return self.user_data
        except AttributeError:
            raise Exception(
                f"Was expecting class {self.__class__} to have field `user_data`",
                "This is intended to be used by callback mechanism"
            )

    def delete(self):
        # remove from parent
        # some widgets like XAxis, YAxis, Legend are not in parent.children
        _guid = self.guid
        if self.registered_as_child:
            del self.parent.children[_guid]

        # call super
        return super().delete()

    def add_tooltip(self, tooltip: t.Union[str, "gui.widget.Tooltip"]):
        """
        Some widgets that are not containes can still have tooltip
        So we hack it here ....

        Note that when we use this method to add tooltip in ContainerWidget
          it cannot be accessed via children

        """
        from .. import gui

        if isinstance(tooltip, str):
            with EscapeWithContext():
                tooltip = gui.widget.Text(default_value=tooltip)
        if tooltip._parent is None:
            # todo: this still does not work we also need to build
            #  tooltip widget .... figure out later .... need to pipe things
            #  so that there is delayed build
            tooltip._parent = self
        else:
            raise Exception(
                "The tooltip instance provided is already set to some parent. "
                f"You can also avoid this error by using {EscapeWithContext} if already in with context."
            )


USER_DATA = t.Dict[
    str, t.Union[
        int, float, str, slice, tuple, list, dict, None, Widget,
    ]
]


@dataclasses.dataclass(repr=False)
class MovableWidget(Widget, abc.ABC):

    def move(
        self,
        top: "ContainerWidget" = None,
        bottom: "ContainerWidget" = None,
        before: "MovableWidget" = None,
        after: "MovableWidget" = None,
    ):
        """
        Args:
            top: move the item to top of container
            bottom: move the item to bottom of container
            before: move before widget
            after: move after widget
        """
        # ---------------------------------------------- 01
        # check
        # only one kwarg must be provided
        _top_supplied = top is not None
        _bottom_supplied = bottom is not None
        _before_supplied = before is not None
        _after_supplied = after is not None
        if not (_top_supplied ^ _bottom_supplied ^ _before_supplied ^ _after_supplied):
            _d = dict(
                _top_supplied=_top_supplied, _bottom_supplied=_bottom_supplied,
                _before_supplied=_before_supplied, _after_supplied=_after_supplied
            )
            raise Exception(
                f"Only one of the move kwarg must be supplied. {_d}"
            )

        # ---------------------------------------------- 02
        # estimate parent and before to be used for move
        if _top_supplied:
            _parent = top
            try:
                _before = next(iter(top.children.values()))
            except StopIteration:
                # when children dict is empty
                _before = None
        elif _bottom_supplied:
            _parent = bottom
            _before = None
        elif _before_supplied:
            _parent = before.parent
            _before = before
        elif _after_supplied:
            _parent = after.parent
            _before = after.after()
        else:
            raise Exception("Should not happen ...")

        # ---------------------------------------------- 03
        # check if new parent allows adding the self
        if not isinstance(self, _parent.restrict_children_to):
            raise Exception(
                f"Cannot move item of type {self.__class__} in parent of type {_parent.__class__}. "
                f"Allowed children types for this parent are {_parent.restrict_children_to}"
            )

        # ---------------------------------------------- 04
        # first del from self.parent.children
        del self.parent.children[self.guid]
        # change the parent
        self._parent = _parent

        # ---------------------------------------------- 05
        # now move it to new parent.children
        if _before is None:
            _parent.children[self.guid] = self
        else:
            # noinspection PyProtectedMember
            _backup = _parent._children
            _parent._children = {}
            for _k in _backup.keys():
                if _k == before.guid:
                    # noinspection PyProtectedMember
                    _parent._children[self.guid] = self
                # noinspection PyProtectedMember
                _parent._children[_k] = _backup[_k]

        # ---------------------------------------------- 06
        # sync the move
        if self.is_built:
            # noinspection PyUnresolvedReferences
            internal_dpg.move_item(
                self.guid, parent=_parent.guid,
                before=0 if _before is None else _before.guid)

    def before(self) -> t.Optional["MovableWidget"]:
        _before = None
        for _v in self.parent.children.values():
            if self == _v:
                break
            _before = _v
        return _before

    def after(self) -> t.Optional["MovableWidget"]:
        _after = None
        _matched = False
        for _v in self.parent.children.values():
            if _matched:
                _after = _v
                break
            _matched = self == _v
        return _after

    def move_up(self) -> bool:
        """
        If already on top returns False
        Else moves up and return True as it moved up
        """
        _before = self.before()
        if _before is None:
            return False
        else:
            self.move(before=self.before())
            # if self.is_built:
            #     internal_dpg.move_item_up(self.guid)
            return True

    def move_down(self) -> bool:
        """
        If already at bottom returns False
        Else moves down and return True as it moved up
        """
        _after = self.after()
        if _after is None:
            return False
        else:
            self.move(after=_after)
            # if self.is_built:
            #     internal_dpg.move_item_down(self.guid)
            return True


@dataclasses.dataclass(repr=False)
class ContainerWidget(Widget, abc.ABC):
    """
    Widget that can hold children
    Example Group, ChildWindow etc.

    todo: add support to restrict which children can be added to container
    """

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[MovableWidget]]:
        """
        Default is to restrict MovableWidget but you can override this to have
        Widget's as the __call__ method can accept Widget
        """
        return MovableWidget,

    @property
    def children(self) -> t.Dict[int, Widget]:
        return self._children

    # noinspection PyMethodOverriding
    def __call__(self, widget: Widget, before: MovableWidget = None):
        self._add_child(_widget=widget)
        if before is not None:
            if isinstance(widget, MovableWidget):
                widget.move(before=before)
            else:
                raise Exception("Do not supply `before` as `widget` is not movable")

    def _add_child(self, _widget: Widget):
        from .. import gui
        # -------------------------------------------------- 01
        # if widget is already built then raise error
        # Note that this will also check if parent and root were not set already ;)
        if _widget.is_built:
            raise Exception(
                "The widget you are trying to add is already built",
                "May be you want to `move()` widget instead.",
            )
        # check if restricted parents
        if not isinstance(self, _widget.restrict_parents_to):
            raise Exception(
                f"Widget of type {_widget.__class__} can only be added "
                f"to parents of type {_widget.restrict_parents_to}. "
                f"While parent of type {self.__class__} is not allowed"
            )
        # we can now store widget inside children dict
        if not isinstance(_widget, self.restrict_children_to):
            raise Exception(
                f"The child widget instance you want to add is of type {_widget.__class__} instead we expect it "
                f"to be one of {self.restrict_children_to}"
            )
        # do not try to add again
        if _widget.guid in self._children.keys():
            print("wwwwwwwwwwww")
            print(self.guid, self)
            print(_widget.guid, _widget)
            for _k, _v in self._children.items():
                print(">>", _k, _v.guid, _v)
            raise Exception("This widget was already added")
        # do not allow tooltip to be child
        if isinstance(_widget, gui.widget.Tooltip):
            raise Exception(
                f"To add tooltip rely on {Widget.add_tooltip} method ..."
            )

        # -------------------------------------------------- 02
        # set internals
        _widget._parent = self

        # -------------------------------------------------- 03
        # noinspection PyTypeChecker
        self._children[_widget.guid] = _widget

        # -------------------------------------------------- 04
        # if thw parent widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            _widget.build()

    def init(self):
        # add var
        # noinspection PyAttributeOutsideInit
        self._children = dict()  # type: t.Dict[int, Widget]
        # call super
        super().init()

    def on_enter(self):
        global _CONTAINER_WIDGET_STACK
        _CONTAINER_WIDGET_STACK.append(self)

        # we do not want behaviour of parent as __call__ is overridden
        # super().on_enter()

    def on_exit(self, exc_type, exc_val, exc_tb):
        global _CONTAINER_WIDGET_STACK
        _CONTAINER_WIDGET_STACK.pop()

        # we do not want behaviour of parent as __call__ is overridden
        # super().on_exit()

    def clone(self) -> "ContainerWidget":
        if bool(self._children):
            raise Exception(
                "Cannot clone as you have added some widgets as children for "
                f"the container widget {self.__class__}"
            )
        # noinspection PyTypeChecker
        return super().clone()

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # call super
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

        # now as layout is completed and build for this widget is completed,
        # now it is time to render children
        for child in self._children.values():
            child.build()

    def hide_widget(self, children_only: bool = False):
        """
        Refer:
        >>> dpg.hide_item
        """
        if children_only:
            for child in self.children.values():
                child.hide_widget()
        else:
            super().hide_widget()

    def clear(self):
        _children = self._children
        for _k in list(_children.keys()):
            _children[_k].delete()

    def delete(self):
        self.clear()
        return super().delete()


@dataclasses.dataclass(repr=False)
class MovableContainerWidget(ContainerWidget, MovableWidget, abc.ABC):
    ...


class UseMethodInForm:
    """
    A decorator for HashableCLass methods that can then be used in forms like
    HashableMethodsRunnerForm and DoubleSplitForm

    Note than async behaviour is handled by callback HashableMethodRunnerCallback
    """

    def __init__(
        self,
        label_fmt: str = None,
        run_async: bool = False,
        display_in_form: bool = True,
        tag_for_caching_in_receiver: t.Optional[t.Union[str, t.Literal['auto']]] = 'auto',
        hide_previously_opened: bool = True,
        tooltip: str = None,
    ):
        """
        Check usage in below places
        >>> gui.callback.HashableMethodRunnerCallback.fn

        Args:
            label_fmt: label for button ... if str is property we will
              call it to get label
            run_async: can call method in async task ...
            display_in_form:
            tag_for_caching_in_receiver:
                When set to None the widget generated will not be cached. Use
                  this option if you want refreshing button. We add extra (*)
                  to indicate that it can be refreshed.
                When 'auto' (i.e. default) automatic unique tag for given
                  hashable and method name will be generated and that tag
                  will be used to cache
                When some str is provided then that will be used to tag and
                  any previous widget will be deleted to make way for new
                  widget generated by callback
            hide_previously_opened:
                Hides cached widgets in receiver before rendering current one (default)
                If set to True it will result in widget stacking
        """
        self.label_fmt = label_fmt
        self.run_async = run_async
        self.display_in_form = display_in_form
        self.tag_for_caching_in_receiver = tag_for_caching_in_receiver
        self.hide_previously_opened = hide_previously_opened
        self.tooltip = tooltip

    def __call__(self, fn: t.Callable):
        """
        todo: add signature test to confirm that Widget or any of its subclass
          is returned by fn
        todo: currently fn cannot have any kwargs but eventually read the kwargs and
          build a form do that parametrized widget running is possible ...
          a bit complex but possible
        """

        # set fn
        self.fn = fn

        # store self inside fn
        # also check `cls.get_from_hashable_fn` which will help get access
        # to this instance
        setattr(self.fn, f"_{self.__class__.__name__}", self)

        # return self.fn as this is decorator
        return self.fn

    @classmethod
    def get_from_hashable_fn(
        cls, hashable: t.Union["Hashable", "HashableClass"], fn_name: str
    ) -> "UseMethodInForm":
        try:
            _fn = getattr(hashable.__class__, fn_name)
        except AttributeError:
            raise Exception(
                f"Function with name {fn_name} is not present in class "
                f"{hashable.__class__}"
            )
        try:
            return getattr(_fn, f"_{cls.__name__}")
        except AttributeError:
            raise Exception(f"The function {_fn} was not decorated with {UseMethodInForm}")

    def get_button_widget(
        self,
        hashable: t.Union["Hashable", "HashableClass"],
        receiver: "gui.widget.ContainerWidget",
    ) -> "gui.widget.Button":

        # ---------------------------------------------------- 01
        # test callable name
        _callable_name = self.fn.__name__
        if not util.rhasattr(hashable, _callable_name):
            raise Exception(
                f"Callable `{_callable_name}` not available for "
                f"HashableClass {hashable.__class__}"
            )

        # ---------------------------------------------------- 02
        # make label for button
        if self.label_fmt is None:
            _button_label = f"{hashable.__class__.__name__}.{hashable.hex_hash} ({_callable_name})"
        elif isinstance(getattr(hashable.__class__, self.label_fmt, None), property):
            _button_label = getattr(hashable, self.label_fmt)
        elif isinstance(self.label_fmt, str):
            _button_label = self.label_fmt
        else:
            raise Exception(f"unknown type {type(self.label_fmt)}")

        # ---------------------------------------------------- 03
        # create callback
        from . import callback
        _callback = callback.HashableMethodRunnerCallback(
            hashable=hashable,
            callable_name=_callable_name,
            receiver=receiver,
        )
        # sanity check must be same
        # noinspection PyProtectedMember
        assert self == _callback._use_method_in_form_obj

        # ---------------------------------------------------- 04
        # create and return button
        from . import widget
        # this indicates that this button can be refreshed (as things are not caches)
        if self.tag_for_caching_in_receiver is None:
            _button_label += " (*)"
        _ret = widget.Button(
            label=_button_label,
            callback=_callback,
        )
        if self.tooltip is not None:
            _ret.add_tooltip(tooltip=self.tooltip)
        return _ret


class YamlDumper(yaml.Dumper):
    """
    todo: SafeDumper does not work with python builtin objects same problem
      with Loader ... figure out later
    Dumper that avoids using aliases in yaml representation .... makes
    it verbose ..., but we are sure that if we reuse an object a new repr will
    be created

    Note: we can go to default and reuse space ... and yaml load will also
    not create multiple instances ..., but the drawback is when someone
    reuses references the yaml lib will share repr with pointers
    """

    def ignore_aliases(self, data):
        return True

    @classmethod
    def dump(cls, item) -> str:
        """
        The method that dumps with specific yaml config for toolcraft
        """
        return yaml.dump(
            item,
            Dumper=YamlDumper,
            sort_keys=False,
            default_flow_style=False,
        )


class YamlLoader(yaml.UnsafeLoader):
    """
    todo: we need to make this inherit from yaml.SafeLoader
    """

    def __init__(self, stream, extra_kwargs):
        """
        Args:
            stream:
                the yaml text
            extra_kwargs:
                we use this extra_kwargs to do some updates to
                loaded dict from yaml file
        """
        self.extra_kwargs = extra_kwargs
        super().__init__(stream=stream)

    @staticmethod
    def load(cls, file_or_text: str, **kwargs) -> t.Union[dict, TYamlRepr]:
        # get text
        _text = file_or_text
        if not isinstance(file_or_text, str):
            raise Exception(
                "Only str is expected as value for kwarg `file_or_text`. ",
                "Note that this is gui related Hashable and not `m.HashableClass` "
                "which can work with yaml files on disk."
            )

        # load with Loader
        _loader = YamlLoader(stream=_text, extra_kwargs=kwargs)
        try:
            _instance = _loader.get_single_data()
        finally:
            _loader.dispose()

        # check
        if _instance.__class__ != cls:
            _msgs = {
                "expected": cls,
                "found": _instance.__class__,
                "yaml_txt": _text,
            }
            raise Exception(
                f"We expect yaml str is for correct class ",
                str(_msgs),
            )

        # return
        return _instance


@dataclasses.dataclass
class Hashable(abc.ABC):

    @property
    def hex_hash(self) -> str:
        return hashlib.md5(f"{self.yaml()}".encode("utf-8")).hexdigest()

    @UseMethodInForm(label_fmt="Info")
    def info_widget(self) -> "gui.widget.Text":
        # import
        from . import widget
        # make
        # noinspection PyUnresolvedReferences
        _ret_widget = widget.Text(
            default_value=f"Hex Hash: {self.hex_hash}\n\n{self.yaml()}"
        )
        # return
        return _ret_widget

    def yaml(self) -> str:
        try:
            return YamlDumper.dump(self)
        except Exception as _e:
            raise Exception(
                "Cannot be serialized by YamlDumper. "
                "Override this method in case you are using "
                "non-serializable fields.", str(_e)
            )

    @classmethod
    def from_yaml(cls, file_or_text: str, **kwargs) -> TYamlRepr:
        # return
        return YamlLoader.load(cls, file_or_text=file_or_text, **kwargs)


@dataclasses.dataclass
class Callback(abc.ABC):
    """
    Note that `Callback.fn` will as call back function.
    But when it comes to callback data we need not worry as the fields
    of this instance will serve as data ;)
    """

    def __post_init__(self):
        self.init_validate()
        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...

    @abc.abstractmethod
    def fn(self, sender: Widget):
        ...


@dataclasses.dataclass(repr=False)
class RegistryItem(Widget, abc.ABC):

    @property
    def restrict_parents_to(self) -> t.Tuple[t.Type["Registry"]]:
        raise Exception(
            "The dpg_generator script must auto generate this ..."
        )


@dataclasses.dataclass(repr=False)
class Registry(ContainerWidget, abc.ABC):
    """
    Registry is like ContainerWidget
    """

    @property
    def restrict_children_to(self) -> t.Tuple[t.Type[RegistryItem]]:
        raise Exception(
            "The dpg_generator script must auto generate this ..."
        )

    def bind(self, widget: Widget):
        # import
        from .registry import WidgetHandlerRegistry, GlobalHandlerRegistry

        # check if built
        if not widget.is_built:
            raise Exception("the widget is not yet built. Can bind only when Registry and Widget are built.")
        if not self.is_built:
            raise Exception("the registry is not yet built. Can bind only when Registry and Widget are built.")

        # if WidgetHandlerRegistry
        if isinstance(self, WidgetHandlerRegistry):
            dpg.bind_item_handler_registry(item=widget.guid, handler_registry=self.guid)
        # if GlobalHandlerRegistry
        elif isinstance(self, GlobalHandlerRegistry):
            raise Exception(f"bind is not available for {GlobalHandlerRegistry}")
        # else
        else:
            raise Exception(f"bind is not yet supported for {self.__class__}")


@dataclasses.dataclass(repr=False)
class PlotSeries(Widget, abc.ABC):

    @property
    def parent(self) -> "plot.YAxis":
        return self._parent


@dataclasses.dataclass(repr=False)
class PlotItem(MovableWidget, abc.ABC):

    @property
    def parent(self) -> "plot.Plot":
        # noinspection PyTypeChecker
        return self._parent


@dataclasses.dataclass
class Dashboard(abc.ABC):
    """
    Dashboard is not a Widget.
    As of now we think of having only items that do not have parent; like
    + Window
    + Registry
    + theme

    The `primary_window` property holds primary Window which will occupy entire screen

    Figure out having more windows that can be popped inside or can be added
    dynamically.

    Here we will take care of things like
    + screen resolution
    + theme
    + closing even handlers
    + favicon
    + login mechanism

    Note that we make this as primary window when we start GUI

    todo: add less important fields to config and save it to disk ... on
      config field change trigger ui update ... plus also update ui when
      config loaded from disk ... this will indirectly help save ui state :)
      Or maybe have only one config for Dashboard alone and make key value
      pairs ... may be introduce new State file for that
      Also maybe add field save_state for Widget so that we know that only
      these widgets state needs to be saved
    """
    # todo: this title needs to set the main title of the entire UI ...
    #  i.e. it should replace "DearPyGui" ... right now has no effect
    title: str
    width: int = 1370
    height: int = 1200

    @property
    def dataclass_field_names(self) -> t.List[str]:
        # noinspection PyUnresolvedReferences
        return list(self.__dataclass_fields__.keys())

    @property
    def is_built(self) -> bool:
        return self._is_built

    def __post_init__(self):
        self._is_built = False
        self.init_validate()
        self.init()

    def init_validate(self):
        ...

    def init(self):
        """
        WHY DO WE CLONE??

        To be called from init. Will be only called for fields that are
        Widget or Callback

        Purpose:
        + When defaults are provided copy them to mimic immutability
        + Each immutable field can have his own parent

        Why is this needed??
          Here we trick dataclass to treat some Hashable classes that were
          assigned as default to be treated as non mutable ... this helps us
          avoid using default_factory

        Who is using it ??
          + gui.Widget
            Needed only while building UI to reuse UI components and keep code
            readable. This will be in line with declarative syntax.
          + gui.Callback
            Although not needed we still allow this behaviour as it will be
            used by users that build GUI and they might get to used to assigning
            callbacks while defining class ... so just for convenience we allow
            this to happen

        Needed for fields that has default values
          When a instance is assigned during class definition then it is not
          longer usable with multiple instances of that classes. This applies in
          case of UI components. But not needed for fields like prepared_data as
          we actually might be interested to share that field with other
          instances.

          When such fields are bound for certain instance especially using the
          property internal we might want an immutable duplicate made for each
          instance.

        todo: Dont be tempted to use this behaviour in other cases like
          Model, HashableClass. Brainstorm if you think this needs
          to be done. AVOID GENERALIZING THIS FUNCTION.

        """

        # ------------------------------------------------------- 01
        # loop over fields
        for f_name in self.dataclass_field_names:
            # --------------------------------------------------- 01.01
            # get value
            v = getattr(self, f_name)
            # --------------------------------------------------- 01.02
            # if None then make sure that it is supplied ..
            # needed as we need to define values for each field
            if v is None:
                raise Exception(
                    f"Please supply value for field `{f_name}` in class "
                    f"{self.__class__}"
                )
            # --------------------------------------------------- 01.03
            # if not Widget class continue
            # that means Widgets and Containers will be clones if default supplied
            # While Hashable class and even Callbacks will not be cloned
            # note that for UI we only need Dpg elements to be clones as they have
            # build() method
            if not isinstance(v, Widget):
                continue
            # --------------------------------------------------- 01.04
            # get field and its default value
            # noinspection PyUnresolvedReferences
            _field = self.__dataclass_fields__[f_name]
            _default_value = _field.default
            # --------------------------------------------------- 01.05
            # if id(_default_value) == id(v) then that means the default value is
            # supplied ... so now we need to trick dataclass and assigned a clone of
            # default_value
            # To understand why we clone ... read __doc_string__
            # Note that the below code can also handle but we use id(...)
            #   to be more specific
            # _default_value == dataclasses.MISSING
            if id(_default_value) == id(v):
                # make clone
                v_cloned = v.clone()
                # hack to overwrite field value (as this is frozen)
                self.__dict__[f_name] = v_cloned

    @staticmethod
    def is_dearpygui_running() -> bool:
        return internal_dpg.is_dearpygui_running()

    @staticmethod
    def is_key_down(key: int) -> bool:
        return internal_dpg.is_key_down(key)

    @staticmethod
    def is_key_pressed(key: int) -> bool:
        return internal_dpg.is_key_pressed(key)

    @staticmethod
    def is_key_released(key: int) -> bool:
        return internal_dpg.is_key_released(key)

    @staticmethod
    def is_mouse_button_clicked(button: int) -> bool:
        return internal_dpg.is_mouse_button_clicked(button)

    @staticmethod
    def is_mouse_button_double_clicked(button: int) -> bool:
        return internal_dpg.is_mouse_button_double_clicked(button)

    @staticmethod
    def is_mouse_button_down(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def is_mouse_button_dragging(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def is_mouse_button_released(button: int) -> bool:
        return internal_dpg.is_mouse_button_down(button)

    @staticmethod
    def get_active_window(**kwargs) -> int:
        """
        Refer:
        >>> dpg.get_active_window

        todo: we will return Window widget later ... once we can track Window's in
          Dashboard
        """
        # noinspection PyArgumentList
        return internal_dpg.get_active_window(**kwargs)

    @staticmethod
    def get_windows(**kwargs) -> t.List[int]:
        """
        Refer:
        >>> dpg.get_windows

        todo: we will return Window widgets later ... once we can track Window's in
          Dashboard
        """
        # noinspection PyArgumentList
        return internal_dpg.get_windows(**kwargs)

    @staticmethod
    def get_app_configuration(**kwargs) -> t.Dict:
        """
        Refer:
        >>> dpg.get_app_configuration
        """
        # noinspection PyArgumentList
        return internal_dpg.get_app_configuration(**kwargs)

    @staticmethod
    def get_delta_time(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_delta_time
        """
        # noinspection PyArgumentList
        return internal_dpg.get_delta_time(**kwargs)

    @staticmethod
    def get_drawing_mouse_pos(**kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_drawing_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_drawing_mouse_pos(**kwargs))

    @staticmethod
    def get_frame_count(**kwargs) -> int:
        """
        Refer:
        >>> dpg.get_frame_count
        """
        # noinspection PyArgumentList
        return internal_dpg.get_frame_count(**kwargs)

    @staticmethod
    def get_frame_rate(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_frame_rate
        """
        # noinspection PyArgumentList
        return internal_dpg.get_frame_rate(**kwargs)

    @staticmethod
    def get_global_font_scale(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_global_font_scale
        """
        # noinspection PyArgumentList
        return internal_dpg.get_global_font_scale(**kwargs)

    @staticmethod
    def get_item_types(**kwargs) -> t.Dict:
        """
        Refer:
        >>> dpg.get_item_types
        """
        # noinspection PyArgumentList
        return internal_dpg.get_item_types(**kwargs)

    @staticmethod
    def get_mouse_drag_delta(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_mouse_drag_delta
        """
        # noinspection PyArgumentList
        return internal_dpg.get_mouse_drag_delta(**kwargs)

    @staticmethod
    def get_mouse_pos(local: bool = True, **kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_mouse_pos(local=local, **kwargs))

    @staticmethod
    def get_plot_mouse_pos(**kwargs) -> t.Tuple[int, int]:
        """
        Refer:
        >>> dpg.get_plot_mouse_pos
        """
        # noinspection PyArgumentList
        return tuple(internal_dpg.get_plot_mouse_pos(**kwargs))

    @staticmethod
    def get_platform(**kwargs) -> "EnPlatform":
        """
        Refer:
        >>> dpg.get_platform
        """
        from . import EnPlatform
        # noinspection PyArgumentList
        return EnPlatform(internal_dpg.get_platform(**kwargs))

    @staticmethod
    def get_total_time(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_total_time
        """
        # noinspection PyArgumentList
        return internal_dpg.get_total_time(**kwargs)

    def add_window(self, window: "gui.window.Window"):
        window.dash_board = self
        window.build()

    @abc.abstractmethod
    def layout(self) -> "gui.window.Window":
        ...

    def build(self):
        # check
        if self.is_built:
            raise Exception("The Dashboard is already built ... call this only once")

        # build
        _primary_window = self.layout()
        _primary_window.dash_board = self
        _primary_window.build()
        # primary window guid
        _primary_window_guid = _primary_window.guid
        # set the things for primary window
        dpg.set_primary_window(window=_primary_window_guid, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_guid=_ret, size=16)
        dpg.bind_item_theme(item=_primary_window_guid, theme=asset.Theme.DARK.get())

        # set is_built
        # noinspection PyAttributeOutsideInit
        self._is_built = True
