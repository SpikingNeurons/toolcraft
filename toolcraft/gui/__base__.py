"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import asyncio
import typing as t
import functools
import enum
import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import numpy as np

from .. import error as e
from .. import logger
from .. import util
from .. import marshalling as m
from .. import settings
from . import asset

# noinspection PyUnreachableCode
if False:
    from . import EnPlatform

_LOGGER = logger.get_logger()
COLOR_TYPE = t.Tuple[int, int, int, int]
# PLOT_DATA_TYPE = t.Union[t.List[float], t.Tuple[float, ...]]
PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]

# container widget stack ... to add to parent automatically
_CONTAINER_WIDGET_STACK: t.List["ContainerWidget"] = []


# noinspection PyUnresolvedReferences,PyUnreachableCode
if False:
    from . import window
    from . import plot


class Enum(m.FrozenEnum, enum.Enum):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.enum.{cls.__name__}"


class EnColor(Enum, enum.Enum):
    DEFAULT = (-1, -1, -1, -1)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)
    GREY = (127, 127, 127, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    RED = (255, 0, 0, 255)


class _WidgetDpgInternal(m.Internal):
    dpg_id: t.Union[int, str]


@dataclasses.dataclass
@m.RuleChecker(
    things_not_to_be_cached=['dpg_state', 'dpg_config', ]
)
class _WidgetDpg(m.YamlRepr, abc.ABC):
    """
    This class is just to keep all dpg related things in one place ...
    Anything specific to our API will go in Widget class
    """

    @property
    @util.CacheResult
    def internal(self) -> _WidgetDpgInternal:
        return _WidgetDpgInternal(owner=self)

    @property
    def dpg_id(self) -> t.Union[int, str]:
        return self.internal.dpg_id

    @property
    def dpg_state(self) -> t.Dict[str, t.Union[bool, t.List[int]]]:
        return internal_dpg.get_item_state(self.dpg_id)

    @property
    def dpg_config(self) -> t.Dict[str, t.Union[bool, t.List[int]]]:
        return internal_dpg.get_item_configuration(self.dpg_id)

    @property
    def dpg_info(self) -> t.Dict[str, t.Any]:
        return internal_dpg.get_item_info(self.dpg_id)

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

    def __post_init__(self):
        self.init_validate()
        self.init()

    def __setattr__(self, key, value):
        # this might not always work especially when key is custom ...
        # in that case catch exception and figure out how to handle
        if self.is_built:
            # The default behaviour is to update configure the dpg item but
            # note that Form is not a typical Widget and hence we have no need for
            # "`internal_dpg.configure_item` ...",
            if not isinstance(self, Form):
                internal_dpg.configure_item(self.dpg_id, **{key: value})
        return super().__setattr__(key, value)

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hookup build
        util.HookUp(
            cls=cls,
            method=cls.build,
            pre_method=cls.build_pre_runner,
            post_method=cls.build_post_runner,
        )

    def init_validate(self):

        # loop over fields
        for f_name in self.dataclass_field_names:
            # get value
            v = getattr(self, f_name)

            # check if Widget and only allow if Form
            if isinstance(v, Widget):
                if not isinstance(self, Form):
                    raise e.code.CodingError(
                        msgs=[
                            f"Check field {self.__class__}.{f_name}",
                            f"You cannot have instance of class {v.__class__} as "
                            f"dataclass fields of {self.__class__}.",
                            f"This is only allowed for {Form} where we only allow "
                            f"{Widget}"
                        ]
                    )

    def init(self):
        raise e.code.CodingError(
            msgs=["will be anyways overridden by Widget class so this can never be called ..."]
        )

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            raise e.code.CodingError(
                msgs=[
                    f"Widget {self.__class__} is already built and registered with:",
                    {
                        'parent': self.internal.parent.__class__,
                    },
                ]
            )

    @abc.abstractmethod
    def build(self) -> t.Union[int, str]:
        ...

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # if None raise error ... we expect int
        if hooked_method_return_value is None:
            raise e.code.CodingError(
                msgs=[
                    f"We expect build to return int which happens to be dpg_id"
                ]
            )

        # test if remaining internals are set
        self.internal.test_if_others_set()

        # set dpg_id
        self.internal.dpg_id = hooked_method_return_value

        # set flag to indicate build is done
        self.internal.is_build_done = True

    def as_dict(self) -> t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        for f_name in self.dataclass_field_names:
            _ret[f_name] = getattr(self, f_name)
        return _ret

    def get_value(self) -> t.Any:
        """
        Refer:
        >>> dpg.get_value
        """
        return internal_dpg.get_value(self.dpg_id)

    def set_value(self, value: t.Any):
        """
        Refer:
        >>> dpg.set_value
        """
        return internal_dpg.set_value(self.dpg_id, value)

    def set_x_scroll(self, value: float):
        """
        Refer:
        >>> dpg.set_x_scroll
        """
        return internal_dpg.set_x_scroll(self.dpg_id, value)

    def get_x_scroll(self) -> float:
        """
        Refer:
        >>> dpg.get_x_scroll
        """
        return internal_dpg.get_x_scroll(self.dpg_id)

    def get_x_scroll_max(self) -> float:
        """
        Refer:
        >>> dpg.get_x_scroll_max
        """
        return internal_dpg.get_x_scroll_max(self.dpg_id)

    def set_y_scroll(self, value: float):
        """
        Refer:
        >>> dpg.set_y_scroll
        """
        return internal_dpg.set_y_scroll(self.dpg_id, value)

    def get_y_scroll(self) -> float:
        """
        Refer:
        >>> dpg.get_y_scroll
        """
        return internal_dpg.get_y_scroll(self.dpg_id)

    def show_debug(self):
        """
        Refer:
        >>> dpg.show_item_debug
        """
        return internal_dpg.show_item_debug(self.dpg_id)

    def unstage(self):
        """
        Refer:
        >>> dpg.unstage
        """
        return internal_dpg.unstage(self.dpg_id)

    def get_y_scroll_max(self) -> float:
        """
        Refer:
        >>> dpg.get_y_scroll_max
        """
        return internal_dpg.get_y_scroll_max(self.dpg_id)

    def reset_pos(self):
        internal_dpg.reset_pos(self.dpg_id)

    def show(self):
        """
        Refer:
        >>> dpg.show_item
        """
        internal_dpg.configure_item(self.dpg_id, show=True)

    def hide(self):
        """
        Refer:
        >>> dpg.hide_item
        """
        internal_dpg.configure_item(self.dpg_id, show=False)

    def bind_theme(self, theme: asset.Theme):
        dpg.bind_item_theme(item=self.dpg_id, theme=theme.get())

    def set_widget_configuration(self, **kwargs):
        # if any value is widget then get its dpg_id
        _new_kwargs = {}
        for _k in kwargs.keys():
            _v = kwargs[_k]
            if isinstance(_v, Widget):
                _v = _v.dpg_id
            _new_kwargs[_k] = _v
        # configure
        dpg.configure_item(item=self.dpg_id, **_new_kwargs)

    def display_raw_configuration(self) -> t.Dict:
        """
        Note that raw dpg_id is not treated
        """
        return dpg.get_item_configuration(item=self.dpg_id)

    def focus(self):
        """
        Refer:
        >>> dpg.focus_item
        """
        dpg.focus_item(self.dpg_id)

    def enable(self):
        """
        Refer:
        >>> dpg.enable_item
        """
        internal_dpg.configure_item(self.dpg_id, enabled=True)

    def disable(self):
        """
        Refer:
        >>> dpg.disable_item
        """
        internal_dpg.configure_item(self.dpg_id, enabled=False)


@dataclasses.dataclass
class AsyncUpdateFn:
    """
    Note that this executes in same process and thread and you have full control as it is interlaced
    execution and ideal for gui

    In current form only lite weight fn can be used as we use concurrency ... while update period can be
      controlled via `update_period`
    But any delays will stall UI .... so need to have ThreadPoolExecutor and ProcessPoolExecutor to do things in
      parallel process or parallel thread instead of concurrent interlaced execution ...

    todo: also animations and transitions can be handled with this ...
      i.e. without need for ThreadPoolExecutor and ProcessPoolExecutor
      Note that we need to remove widget from async updates via `widget.stop_async_update()` ...
        so this needs to be done in fn ... this will allow us to track lot of widgets for async updates

    todo: implement ThreadPoolExecutor (for IO-bound tasks) and ProcessPoolExecutor (for CPU-bound tasks)
      use for CPU-bound and IO-bound task task ... but note that you have no access to vars in main process (may-be)
      might need to make this more general so move to `toolcraft.job`
      most likely make fn await on these threads after deciding on API and understanding asyncio pool's
      Refer: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    """
    fn: t.Callable
    widget: "Widget"
    extra_widgets: t.Dict[str, "Widget"] = None

    def __post_init__(self):
        if not self.widget.is_built:
            raise e.code.CodingError(
                msgs=[
                    "The main widget is not built so cannot create the instance",
                    f"You can still register to make instance later on build using class method {AsyncUpdateFn.create}"
                ]
            )

    @classmethod
    def create(
        cls,
        fn: t.Callable,
        widget: "Widget",
        extra_widgets: t.Dict[str, "Widget"] = None,
    ):
        """
        note that call to .create will auto register to dashboard for async update tracking
        """

        if widget.is_built:
            _nt = AsyncUpdateFn(
                fn=fn, widget=widget, extra_widgets=extra_widgets)
            widget.dash_board.async_update_fns_queue.put_nowait(_nt)
        else:
            if bool(widget.internal.post_build_fns):
                widget.internal.post_build_fns.append(
                    functools.partial(
                        widget.set_async_update_fn, fn=fn, extra_widgets=extra_widgets)
                )
            else:
                widget.internal.post_build_fns = [
                    functools.partial(
                        widget.set_async_update_fn, fn=fn, extra_widgets=extra_widgets)
                ]


class WidgetInternal(_WidgetDpgInternal):
    parent: "ContainerWidget"
    is_build_done: bool
    tag: str = None
    post_build_fns: t.List[t.Callable] = None

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + ["tag", "parent", "post_build_fns", ]

    def test_if_others_set(self):
        if not self.has("parent"):
            raise e.code.CodingError(
                msgs=[
                    f"Widget {self.__class__} is not a children to any parent",
                    f"Please use some container widget and add this Widget",
                ]
            )


@dataclasses.dataclass
@m.RuleChecker(
    things_not_to_be_cached=['is_tagged', 'get_tag']
)
class Widget(_WidgetDpg, abc.ABC):
    """
    todo: add async update where widget can be updated via long running python code
      need to also stop tracking if widget is closed in between ...
      also if selected it should resume based on what long running code is doing ...
      may be need to register job with gui subsystem ...
      VERY USEFUL FEATURE AND MUCH NEEDED ... but implementation can be delayed
    """

    @property
    def is_tagged(self) -> bool:
        return self.internal.tag is not None

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    def parent(self) -> "ContainerWidget":
        return self.internal.parent

    @property
    @util.CacheResult
    def root(self) -> "window.Window":
        return self.parent.root

    @property
    @util.CacheResult
    def dash_board(self) -> "Dashboard":
        """
        root is always Window and Window has Dashboard
        """
        return self.root.dash_board

    @property
    def restricted_parent_types(self) -> t.Optional[t.Tuple["Widget", ...]]:
        return None

    @property
    def registered_as_child(self) -> bool:
        return True

    @property
    def is_in_gui_with_mode(self) -> bool:
        return bool(_CONTAINER_WIDGET_STACK)

    def __eq__(self, other):
        """
        Needed for ContainerWidget.index_in_children to work ...
        as data related things like PlotSeries have numpy arrays
        """
        return id(self) == id(other)

    # noinspection PyMethodOverriding
    def __call__(self):
        raise e.code.NotAllowed(
            msgs=[f"__call__ is blocked for class {self.__class__} ... "
                  f"this is only allowed for {ContainerWidget}"]
        )

    def init(self):
        global _CONTAINER_WIDGET_STACK

        # if there is parent container that is available via with context then add to it
        # this is only for using with `with` syntax
        if bool(_CONTAINER_WIDGET_STACK):
            _CONTAINER_WIDGET_STACK[-1](widget=self)

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.widget.{cls.__name__}"

    def on_enter(self):
        raise e.code.NotAllowed(
            msgs=[f"Widget for class {self.__class__} is not a {ContainerWidget.__name__!r} so "
                  f"you cannot use with context"]
        )

        # we do not want behaviour of parent as __call__ is overridden
        # super().on_enter()

    def on_exit(self, exc_type, exc_val, exc_tb):
        raise e.code.NotAllowed(
            msgs=[f"Widget for class {self.__class__} is not a {ContainerWidget.__name__!r} so "
                  f"you cannot use with context"]
        )

        # we do not want behaviour of parent as __call__ is overridden
        # super().on_exit()

    def get_user_data(self) -> 'USER_DATA':
        """
        Almost every subclassed Widget will have this field but we cannot have it here
        as dataclass mechanism does not allow it. So we offer this utility method

        todo: raise issue with dpg for why they need user_data for Widgets which do
          not support any callbacks
        """
        try:
            # noinspection PyUnresolvedReferences
            return self.user_data
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"Was expecting class {self.__class__} to have field `user_data`",
                    "This is intended to be used by callback mechanism"
                ]
            )

    def get_tag(self) -> str:
        if self.is_tagged:
            return self.internal.tag
        raise e.validation.NotAllowed(
            msgs=["This widget was never tagged ... so we cannot retrieve the tag"]
        )

    def set_async_update_fn(
        self, fn: t.Callable, extra_widgets: t.Dict[str, "Widget"] = None
    ):
        """
        Shortcut method to apply async updates for widgets created on the fly
        Note that the fn can then only accept one kwarg named `widget`
        """
        # note that call to .create will auto register to dashboard for async update tracking
        AsyncUpdateFn.create(
            fn=fn, extra_widgets=extra_widgets, widget=self,
        )

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # call super
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

        # call post_build_fns
        if bool(self.internal.post_build_fns):
            for _fn in self.internal.post_build_fns:
                _fn()
            self.internal.post_build_fns = None

    def tag_it(self, tag: str):
        self.dash_board.tag_widget(tag=tag, widget=self)

    def untag_it(self, not_exists_ok: bool = False):
        self.dash_board.untag_widget(tag_or_widget=self, not_exists_ok=not_exists_ok)

    def delete(self):
        # remove from parent
        # some widgets like XAxis, YAxis, Legend are not in parent.children
        if self.registered_as_child:
            _widget = self.parent.children.pop(self.parent.index_in_children(self))

        # if tagged then untag
        if self.is_tagged:
            self.untag_it(not_exists_ok=True)

        # delete the dpg UI counterpart
        dpg.delete_item(item=self.dpg_id, children_only=False, slot=-1)
        # todo: make _widget unusable ... figure out


USER_DATA = t.Dict[
    str, t.Union[
        int, float, str, slice, tuple, list, dict, None,
        m.FrozenEnum, m.HashableClass, Widget,
    ]
]


@dataclasses.dataclass
class MovableWidget(Widget, abc.ABC):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.movable_widget.{cls.__name__}"

    def move(self, parent: "ContainerWidget" = None, before: "MovableWidget" = None):
        """
        Move the item in `parent` or put it before `before`
        """
        # ---------------------------------------------- 01
        # check
        # ---------------------------------------------- 01.01
        # either parent or before should be supplied
        if not((parent is None) ^ (before is None)):
            raise e.code.CodingError(
                msgs=[
                    "Either supply parent or before",
                    "No need to provide both as parent can extracted from before",
                    "While if you supply parent that means you want to add to "
                    "bottom of its children",
                ]
            )

        # ---------------------------------------------- 02
        # related to kwarg `before`
        if parent is None:
            # noinspection PyUnresolvedReferences
            parent = before.parent
        _before_index = None
        if before is not None:
            # if before is not None check if it is in parent and get its index
            _before_index = parent.index_in_children(before)
            if _before_index is None:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"We cannot find `before` widget in children of `parent` "
                        f"you want to move in",
                        "Provide `before` from same `parent` you want to move in or "
                        "supply `None`",
                    ]
                )

        # ---------------------------------------------- 03
        # first pop from self.parent.children
        self.parent.children.pop(self.parent.index_in_children(self))

        # ---------------------------------------------- 04
        # now move it to new parent.children
        if _before_index is None:
            parent.children.append(self)
        else:
            parent.children.insert(_before_index, self)

        # ---------------------------------------------- 05
        # sync the move
        self.internal.parent = parent
        if self.is_built:
            # noinspection PyUnresolvedReferences
            internal_dpg.move_item(
                self.dpg_id, parent=parent.dpg_id,
                before=0 if before is None else before.dpg_id)

    def move_up(self) -> bool:
        """
        If already on top returns False
        Else moves up by one index and returns True as it moved up
        """
        _children_list = self.parent.children
        _index = self.parent.index_in_children(self)
        if _index == 0:
            return False
        _children_list.insert(_index-1, _children_list.pop(_index))
        internal_dpg.move_item_up(self.dpg_id)
        return True

    def move_down(self) -> bool:
        """
        If already at bottom returns False
        Else moves down by one index and returns True as it moved down
        """
        _children_list = self.parent.children
        _index = self.parent.index_in_children(self)
        if _index == len(_children_list)-1:
            return False
        _children_list.insert(_index+1, _children_list.pop(_index))
        internal_dpg.move_item_down(self.dpg_id)
        return True


@dataclasses.dataclass
@m.RuleChecker(
    things_to_be_cached=['children'],
)
class ContainerWidget(Widget, abc.ABC):
    """
    Widget that can hold children
    Example Group, ChildWindow etc.

    todo: add support to restrict which children can be added to container
    """

    @property
    @util.CacheResult
    def children(self) -> t.List[MovableWidget]:
        return []

    @property
    def restrict_children_type(self) -> t.List[t.Type[MovableWidget]]:
        """
        Default is to restrict MovableWidget but you can override this to have
        Widget's as the __call__ method can accept Widget
        """
        return [MovableWidget]

    # noinspection PyMethodOverriding
    def __call__(self, widget: Widget, before: MovableWidget = None):
        self._add_child(widget=widget)
        if before is not None:
            if isinstance(widget, MovableWidget):
                widget.move(before=before)
            else:
                raise e.code.CodingError(
                    msgs=[
                        "Do not supply `before` as `widget` is not movable"
                    ]
                )

    def _add_child(self, widget: Widget):

        # -------------------------------------------------- 01
        # validate
        # -------------------------------------------------- 01.01
        # check if child supported
        if not isinstance(widget, tuple(self.restrict_children_type)):
            raise e.code.CodingError(
                msgs=[
                    f"The widget that can be added to {self.__class__} is "
                    f"restricted to type {self.restrict_children_type} "
                    f"but you are adding widget of type {type(widget)}",
                    f"Check if it is possible to have {widget.__class__} as a "
                    f"property of class {self.__class__} instead especially if "
                    f"it is not {MovableWidget}",
                ]
            )
        # -------------------------------------------------- 01.02
        # if widget is already built then raise error
        # Note that this will also check if parent and root were not set already ;)
        if widget.is_built:
            raise e.code.NotAllowed(
                msgs=[
                    "The widget you are trying to add is already built",
                    "May be you want to `move()` widget instead.",
                ]
            )

        # -------------------------------------------------- 03
        # set internals
        widget.internal.parent = self

        # -------------------------------------------------- 04
        # we can now store widget inside children list
        # noinspection PyTypeChecker
        self.children.append(widget)

        # -------------------------------------------------- 05
        # if thw parent widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            widget.build()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.container_widget.{cls.__name__}"

    def index_in_children(self, child: Widget) -> int:
        for _i, _ in enumerate(self.children):
            if id(_) == id(child):
                return _i
        # index does not work as there are numpy arrays in some
        # widgets like PlotSeries
        # todo: numpy data fields of Widget should be stored in some property
        #  (like `data`) rather than having it as dataclass field ...
        #  this will also avoid parsing to yaml by `m.Tracker` and data will be
        #  separate from Widget defination as anyways it can be updated
        # return self.children.index(child)

        # raise error if noting returned
        raise e.code.CodingError(
            msgs=[
                "You have not supplied valid child ... "
                "please make sure you use this only for valid children",
            ]
        )

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
        if bool(self.children):
            raise e.code.CodingError(
                msgs=[
                    "Cannot clone as you have added some widgets as children for "
                    f"the container widget {self.__class__}"
                ]
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
        for child in self.children:
            child.build()

    def hide(self, children_only: bool = False):
        """
        Refer:
        >>> dpg.hide_item
        """
        if children_only:
            for child in self.children:
                child.hide()
        else:
            super().hide()

    def clear(self):
        _children_copy = self.children.copy()
        for _c in _children_copy:
            _c.delete()
        del _children_copy

    def delete(self):
        self.clear()
        return super().delete()


@dataclasses.dataclass
class MovableContainerWidget(ContainerWidget, MovableWidget, abc.ABC):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.movable_container_widget.{cls.__name__}"


@dataclasses.dataclass
@m.RuleChecker(
    things_to_be_cached=['form_fields_container'],
    things_not_to_be_overridden=['build']
)
class Form(MovableWidget, abc.ABC):
    """
    Form is a special widget which creates a `form_fields_container` container and
    add all form fields to it as defined by layout() method.

    Note that Form itself is not a container and no children can be added to it.
    It only supports UI elements supplied via fields. Non Widget fields like Callbacks
    and constants will be can also be supplied to form to enhance form but obviously
    they are not UI elements and hence will be ignored by layout method.

    If you want dynamic widgets simple have a class field defined with container
    Widgets like Group and dynamically add elements to it.

    todo: the delete can be called on class field Widgets ... mostly we want to not
      allow fields of form to be dynamically deleted ... but that is not the case now
      So do only if needed
    """
    title: t.Optional[str]
    collapsing_header_open: bool

    @property
    @util.CacheResult
    def form_fields_container(self) -> MovableContainerWidget:
        """
        The container that holds all form fields.

        Note that this should be movable too .. i.e. you cannot use
        widgets like Window.

        Default is Group but you can have any widget that allows children.
        ChildWindow is also better option as it has menubar.

        Override this property to achieve the same.
        """
        from .widget import Group
        return Group()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.form.{cls.__name__}"

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
        # call super
        super().init()

        # ------------------------------------------------------- 02
        # loop over fields
        for f_name in self.dataclass_field_names:
            # --------------------------------------------------- 02.01
            # get value
            v = getattr(self, f_name)
            # --------------------------------------------------- 02.02
            # if not Widget class continue
            # that means Widgets and Containers will be clones if default supplied
            # While Hashable class and even Callbacks will not be cloned
            # note that for UI we only need Dpg elements to be clones as they have
            # build() method
            if not isinstance(v, Widget):
                continue
            # --------------------------------------------------- 02.03
            # get field and its default value
            # noinspection PyUnresolvedReferences
            _field = self.__dataclass_fields__[f_name]
            _default_value = _field.default
            # --------------------------------------------------- 02.04
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

    def layout(self):
        """
        Method to layout widgets in this form and assign Callbacks if any

        Note that default behaviour is to layout the UI elements in the order as
        defined in class fields.

        You can override this method to do layout in any order you wish.

        Note that if you have Callbacks for this form as class fields you need to take
        care to bind them to widgets. The default implementation is very simple

        For dynamic widgets add Group widget as dataclass field and add dynamic items
        to it
        """

        # if there is a widget which is field of this widget then add it
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if isinstance(v, MovableWidget):
                self.form_fields_container(widget=v)

    def build(self) -> t.Union[int, str]:
        # set internals
        from .widget import CollapsingHeader

        # if title present add collapsing header
        if self.title is None:
            _c = self.form_fields_container
        else:
            _c = CollapsingHeader(
                label=self.title, default_open=self.collapsing_header_open)
            _c(widget=self.form_fields_container)

        # set parent
        _c.internal.parent = self.parent

        # layout
        self.layout()

        # return
        return _c.build()

    def clear(self):
        _children_copy = self.form_fields_container.children.copy()
        for _c in _children_copy:
            _c.delete()
        del _children_copy

    def delete(self):
        self.clear()
        return super().delete()


@dataclasses.dataclass(frozen=True)
class Callback(m.YamlRepr, abc.ABC):
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

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.callback.{cls.__name__}"

    @abc.abstractmethod
    def fn(self, sender: Widget):
        ...

    def as_dict(self) -> t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        for f_name in self.dataclass_field_names:
            _ret[f_name] = getattr(self, f_name)
        return _ret


@dataclasses.dataclass(frozen=True)
class Registry(m.YamlRepr, abc.ABC):

    def __post_init__(self):
        self.init_validate()
        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.registry.{cls.__name__}"

    def get_user_data(self) -> USER_DATA:
        """
        Almost every subclassed Registry will have this field but we cannot have it here
        as dataclass mechanism does not allow it. So we offer this utility method

        todo: raise issue with dpg for why they need user_data for registry if they
          do not use any callbacks
        """
        try:
            # noinspection PyUnresolvedReferences
            return self.user_data
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"Was expecting class {self.__class__} to have field `user_data`",
                    "This is intended to be used by callback mechanism"
                ]
            )

    def as_dict(self) -> t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        for f_name in self.dataclass_field_names:
            _ret[f_name] = getattr(self, f_name)
        return _ret


class PlotSeriesInternal(WidgetInternal):
    parent: "plot.YAxis"


@dataclasses.dataclass
class PlotSeries(Widget, abc.ABC):

    @property
    @util.CacheResult
    def internal(self) -> PlotSeriesInternal:
        return PlotSeriesInternal(owner=self)

    @property
    def parent(self) -> "plot.YAxis":
        return self.internal.parent

    @classmethod
    def yaml_tag(cls) -> str:
        # ys -> Y Series
        return f"gui.plot.ys.{cls.__name__}"


class PlotItemInternal(WidgetInternal):
    parent: "plot.Plot"


@dataclasses.dataclass
class PlotItem(MovableWidget, abc.ABC):

    @property
    @util.CacheResult
    def internal(self) -> PlotItemInternal:
        return PlotItemInternal(owner=self)

    @property
    def parent(self) -> "plot.Plot":
        return self.internal.parent

    @classmethod
    def yaml_tag(cls) -> str:
        # ci -> movable item
        return f"gui.plot.{cls.__name__}"


class DashboardInternal(m.Internal):
    is_run_called: bool


@dataclasses.dataclass
@m.RuleChecker(
    things_not_to_be_overridden=['run', 'tags', 'async_update_fns_queue'],
    things_to_be_cached=['tags', 'async_update_fns_queue'],
)
class Dashboard(m.YamlRepr, abc.ABC):
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
    @util.CacheResult
    def internal(self) -> DashboardInternal:
        return DashboardInternal(owner=self)

    @property
    @util.CacheResult
    def async_update_fns_queue(self) -> asyncio.Queue:
        return asyncio.Queue()

    @property
    @util.CacheResult
    def tags(self) -> t.Dict[str, Widget]:
        """
        We save tagged widgets with dashboard for all windows and widgets to access

        todo: check contextvars ... might not be needed for tag ....
          but can be useful when we want simple names which are repeatable
          across many windows ... this will keep tags have readable names but based on
          context we can bring uniqueness ... especially useful for asyncio
          https://docs.python.org/3/library/contextvars.html
        """
        return {}

    def __post_init__(self):
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
        # ...

        # ------------------------------------------------------- 02
        # loop over fields
        for f_name in self.dataclass_field_names:
            # --------------------------------------------------- 02.01
            # get value
            v = getattr(self, f_name)
            # --------------------------------------------------- 02.02
            # if None then make sure that it is supplied ..
            # needed as we need to define values for each field
            if v is None:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"Please supply value for field `{f_name}` in class "
                        f"{self.__class__}"
                    ]
                )
            # --------------------------------------------------- 02.03
            # if not Widget class continue
            # that means Widgets and Containers will be clones if default supplied
            # While Hashable class and even Callbacks will not be cloned
            # note that for UI we only need Dpg elements to be clones as they have
            # build() method
            if not isinstance(v, Widget):
                continue
            # --------------------------------------------------- 02.04
            # get field and its default value
            # noinspection PyUnresolvedReferences
            _field = self.__dataclass_fields__[f_name]
            _default_value = _field.default
            # --------------------------------------------------- 02.05
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

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.dashboard.{cls.__name__}"

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

    def get_widget_from_tag(self, tag: str) -> Widget:
        if tag in self.tags.keys():
            return self.tags[tag]
        else:
            raise e.validation.NotAllowed(
                msgs=[
                    f"We cannot find widget for tag {tag!r}."
                ]
            )

    def tag_widget(self, tag: str, widget: Widget):
        # if tag is already used up
        if tag in self.tags.keys():
            raise e.code.NotAllowed(
                msgs=[
                    f"A widget with tag `{tag}` already exists. "
                    f"Please select some unique name."
                ]
            )

        # if already tagged raise error
        if widget.is_tagged:
            raise e.code.NotAllowed(
                msgs=[
                    f"The widget is already tagged with tag {widget.tag} "
                    f"so we cannot assign new tag {tag} ..."
                ]
            )

        # save reference inside widget
        widget.internal.tag = tag

        # save in global container
        self.tags[tag] = widget

    def untag_widget(self, tag_or_widget: t.Union[str, Widget], not_exists_ok: bool = False):
        # get tag
        _tag = tag_or_widget
        if isinstance(tag_or_widget, Widget):
            _tag = tag_or_widget.internal.tag

        # if tag name not present
        if _tag not in self.tags.keys():
            if not_exists_ok:
                return
            else:
                raise e.code.NotAllowed(
                    msgs=[
                        "There is no widget tagged with the tag name "
                        f"`{_tag}` hence there is nothing to remove"
                    ]
                )

        # get tag
        _widget = self.tags[_tag]

        # since tag exists remove it ... also set internal.tag to None
        _widget.internal.tag = None
        del self.tags[_tag]

    @abc.abstractmethod
    def setup(self):
        ...

    @abc.abstractmethod
    def layout(self):
        ...

    @abc.abstractmethod
    def build(self):
        ...

    async def async_main_update(self):
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

        """
        _q = self.async_update_fns_queue
        _loop = asyncio.get_event_loop()
        while True:
            # await and get any queued task
            _async_update_fn = await _q.get()

            # call _async_update_fn in async mode in event loop
            _kwargs = dict(widget=_async_update_fn.widget)
            if bool(_async_update_fn.extra_widgets):
                _kwargs.update(_async_update_fn.extra_widgets)
            _task = _loop.create_task(_async_update_fn.fn(**_kwargs))

            # this will remove task that just finished ... but note that the above task if not completed will
            # still run concurrently until completion
            _q.task_done()

    async def async_main_dpg(self):
        if settings.PYC_DEBUGGING:
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

    async def async_main(self):
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
        """
        # ----------------------------------------------------------- 01
        # get event loop
        _loop = asyncio.get_event_loop()

        # ----------------------------------------------------------- 02
        # create tasks
        _dpg_task = _loop.create_task(self.async_main_dpg())
        _update_task = _loop.create_task(self.async_main_update())

        # ----------------------------------------------------------- 03
        # await on dpg task and cancel update task
        await _dpg_task
        _update_task.cancel()

    def run(self):
        # -------------------------------------------------- 01
        # make sure if was already called
        if self.internal.has("is_run_called"):
            raise e.code.NotAllowed(
                msgs=[
                    f"You can run only once ..."
                ]
            )
        # -------------------------------------------------- 02
        # setup dpg
        _pyc_debug = settings.PYC_DEBUGGING
        dpg.create_context()
        dpg.configure_app(manual_callback_management=_pyc_debug)
        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        if not internal_dpg.is_viewport_ok():
            raise RuntimeError("Viewport was not created and shown.")

        # -------------------------------------------------- 03
        # setup and layout
        _LOGGER.info(msg="Setup and layout dashboard ...")
        self.setup()
        self.layout()

        # -------------------------------------------------- 04
        # call build and indicate build is done
        _LOGGER.info(msg="Building dashboard ...")
        self.build()
        self.internal.is_run_called = True

        # -------------------------------------------------- 05
        # call gui main code in async
        asyncio.run(
            self.async_main(),
            debug=_pyc_debug,
        )

        # -------------------------------------------------- 06
        # destroy
        dpg.destroy_context()
