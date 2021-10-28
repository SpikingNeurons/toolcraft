"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import typing as t
import enum
import dearpygui.dearpygui as dpg
# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .. import error as e
from .. import logger
from .. import util
from .. import marshalling as m
from . import asset

_LOGGER = logger.get_logger()
COLOR_TYPE: t.Tuple[int, int, int, int]

# noinspection PyUnresolvedReferences,PyUnreachableCode
if False:
    from . import window


class Enum(m.FrozenEnum):

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


class DpgInternal(m.Internal):
    dpg_id: t.Union[int, str]
    is_build_done: bool


@dataclasses.dataclass
class Dpg(m.YamlRepr, abc.ABC):

    @property
    @util.CacheResult
    def internal(self) -> DpgInternal:
        return DpgInternal(owner=self)

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

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
        internal_dpg.configure_item(self.dpg_id, **{key: value})
        return super().__setattr__(key, value)

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hookup build
        util.HookUp(
            cls=cls,
            silent=True,
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
            if isinstance(v, Dpg):
                if isinstance(self, Form):
                    if not isinstance(v, Widget):
                        e.code.CodingError(
                            msgs=[
                                f"Check field {self.__class__}.{f_name}",
                                f"For {Form} you can have fields that are {Widget}. ",
                                f"But seems like you are adding non widget {Dpg} class "
                                f"{v.__class__} to this class {self.__class__}"
                            ]
                        )
                else:
                    e.code.CodingError(
                        msgs=[
                            f"Check field {self.__class__}.{f_name}",
                            f"You cannot have instance of class {v.__class__} as "
                            f"dataclass fields of {self.__class__}.",
                            f"This is only allowed for {Form} where we only allow "
                            f"{Widget}"
                        ]
                    )

    def init(self):
        ...

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(
                msgs=[
                    f"Widget is already built and registered with:",
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
            e.code.CodingError(
                msgs=[
                    f"We expect build to return int which happens to be dpg_id"
                ]
            )

        # set dpg_id
        self.internal.dpg_id = hooked_method_return_value

        # set flag to indicate build is done
        self.internal.is_build_done = True

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

    def set_theme(self, theme: asset.Theme):
        dpg.set_item_theme(item=self.dpg_id, theme=theme.get())

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


class WidgetInternal(DpgInternal):
    parent: "Container"
    root: "window.Window"

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + [
            "parent", "root"
        ]


@dataclasses.dataclass
class Widget(Dpg, abc.ABC):

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    def is_built(self) -> bool:
        _ret = super().internal.has(item="is_build_done")
        # note that until first build is not called these vars will not be set
        # so we extra check here for rigorous testing
        e.code.AssertError(
            value1=_ret, value2=self.internal.has("parent"),
            msgs=[
                "parent must be set by now as widget is already built"
                if _ret else
                "parent was not expected to be set as build is not yet done"
            ]
        )
        e.code.AssertError(
            value1=_ret, value2=self.internal.has("root"),
            msgs=[
                "root must be set by now as widget is already built"
                if _ret else
                "root was not expected to be set as build is not yet done"
            ]
        )
        return _ret

    @property
    def parent(self) -> "Container":
        return self.internal.parent

    @property
    def root(self) -> "window.Window":
        return self.internal.root

    @property
    def restricted_parent_types(self) -> t.Optional[t.Tuple["Widget", ...]]:
        return None

    @property
    @abc.abstractmethod
    def supports_before(self) -> bool:
        ...

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.widget.{cls.__name__}"

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hookup delete
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.delete,
            pre_method=cls.delete_pre_runner,
            post_method=cls.delete_post_runner,
        )

    def move(self, parent: "Container", before: "Widget" = None):
        """
        Move the item in `parent` and put it before `before`
        """
        # ---------------------------------------------- 01
        # related to kwarg `before`
        _before_index = None
        if before is not None:
            # raise error if before is not supported by this widget
            if 'before' not in self.dataclass_field_names:
                e.code.CodingError(
                    msgs=[
                        f"Widget {self.__class__} does not support `before` field "
                        f"so supply None"
                    ]
                )
            # if before is not None check if it is in parent and get its index
            try:
                _before_index = parent.children.index(before)
            except ValueError:
                e.validation.NotAllowed(
                    msgs=[
                        f"We cannot find `before` widget in children of `parent` "
                        f"you want to move in",
                        "Provide `before` from same `parent` you want to move in or "
                        "supply `None`",
                    ]
                )

        # ---------------------------------------------- 02
        # first pop from self.parent.children
        _src_children = self.parent.children
        _src_children.pop(_src_children.index(self))

        # ---------------------------------------------- 02
        # make the move
        self.internal.parent = parent
        self.internal.root = parent.root
        self.internal.before = before
        parent.children.insert(_before_index, _widget)
        internal_dpg.move_item(
            _widget.dpg_id, parent=parent.dpg_id,
            before=0 if before is None else before.dpg_id)

    def move_up(self) -> bool:
        """
        If already on top returns False
        Else moves up by one index and returns True as it moved up
        """
        _children_list = self.parent.children
        _index = self.parent.children.index(self)
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
        _index = self.parent.children.index(self)
        if _index == len(_children_list)-1:
            return False
        _children_list.insert(_index+1, _children_list.pop(_index))
        internal_dpg.move_item_down(self.dpg_id)
        return True

    def delete_pre_runner(self):
        ...

    def delete(self):
        _children_list = self.parent.children
        _index = self.parent.children.index(self)
        _widget = self.parent.children.pop(_index)
        # delete the dpg UI counterpart
        dpg.delete_item(item=self.dpg_id, children_only=False, slot=-1)
        # todo: make _widget unusable ... figure out

    def delete_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        ...


@dataclasses.dataclass
class Container(Widget, abc.ABC):
    """
    Widget that can hold children
    Example Group, ChildWindow etc.

    todo: add support to restrict which children can be added to container
    """

    @property
    @util.CacheResult
    def children(self) -> t.List["Widget"]:
        # this will be populated when __set_item__ is called
        return []

    def __getitem__(self, item: t.Tuple[t.Union["Widget", t.List["Widget"]], ...]):
        for _item in item:
            if isinstance(_item, Widget):
                self.add_child(widget=_item)
            elif isinstance(_item, list):
                from .widget import Group
                _g = Group(horizontal=True)
                for _i in _item:
                    _g.add_child(widget=_i)
            else:
                e.code.CodingError(
                    msgs=[
                        f"Unsupported item of type {type(item)}"
                    ]
                )
                raise

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.container.{cls.__name__}"

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # now as layout is completed and build for this widget is completed,
        # now it is time to render children
        for child in self.children:
            child.build()

        # call super
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

    def add_child(
        self,
        widget: "Widget",
        before: "Widget" = None,
    ):

        # -------------------------------------------------- 01
        # validate
        # -------------------------------------------------- 01.01
        # if widget is already built then raise error
        # Note that this will also check if parent and root were not set already ;)
        if widget.is_built:
            e.code.NotAllowed(
                msgs=[
                    f"The widget is already built",
                ]
            )
        # -------------------------------------------------- 01.02
        # if before is specified then make sure that parent of before and self is same
        if before is not None:
            if id(before.parent) != id(self):
                e.validation.NotAllowed(
                    msgs=[
                        f"The parent of before is not self and hence cannot be added "
                        f"as child to this parent",
                        f"Try to check if you want to use move() instead."
                    ]
                )

        # -------------------------------------------------- 02
        # if already in children raise error
        _before_index = None
        _widget_id = id(widget)
        if before is not None:
            _before_id = id(before)
            for _i, _c in enumerate(self.children):
                if id(_c) == _widget_id:
                    e.validation.NotAllowed(
                        msgs=[
                            f"Looks like the widget is already "
                            f"added to parent."
                        ]
                    )
                if id(_c) == _before_id:
                    _before_index = _i

        # -------------------------------------------------- 03
        # set internals
        widget.internal.parent = self
        widget.internal.root = self.root

        # -------------------------------------------------- 04
        # we can now store widget inside children list
        # Note that guid is used as it is for dict key
        if _before_index is None:
            self.children.append(widget)
        else:
            self.children.insert(_before_index, widget)

        # -------------------------------------------------- 05
        # if thw parent widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            widget.build()

    def hide(self, children_only: bool = False):
        """
        Refer:
        >>> dpg.hide_item
        """
        if children_only:
            for child in self.children:
                child.hide()
        else:
            internal_dpg.configure_item(self.dpg_id, show=False)


@dataclasses.dataclass
class Form(Widget, abc.ABC):
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

    @property
    @util.CacheResult
    def form_fields_container(self) -> Container:
        """
        The container that holds all form fields.
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
            if isinstance(v, Widget):
                self.form_fields_container.add_child(widget=v, before=None)

    def build(self) -> t.Union[int, str]:
        # layout
        self.layout()

        # return
        return self.form_fields_container.dpg_id


@dataclasses.dataclass
class Callback(m.YamlRepr, abc.ABC):
    """
    Note that `Callback.fn` will as call back function.
    But when it comes to callback data we need not worry as the fields
    of this instance will serve as data ;)
    """

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.callback.{cls.__name__}"

    @abc.abstractmethod
    def fn(
        self,
        sender: Dpg,
        app_data: t.Any,
        user_data: t.Union[Dpg, t.List[Dpg]]
    ):
        ...


class DashboardInternal(m.Internal):
    is_run_called: bool


@dataclasses.dataclass
class Dashboard(m.YamlRepr):
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
    title: str
    width: int = 1370
    height: int = 1200

    @property
    @util.CacheResult
    def internal(self) -> DashboardInternal:
        return DashboardInternal(owner=self)

    @property
    def primary_window(self) -> "window.Window":
        from .window import Window
        return Window(
            label=self.title,
            width=self.width, height=self.height,
        )

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
    def get_total_time(**kwargs) -> float:
        """
        Refer:
        >>> dpg.get_total_time
        """
        # noinspection PyArgumentList
        return internal_dpg.get_total_time(**kwargs)

    def build(self):
        self.primary_window.build()

    def run(self):
        # -------------------------------------------------- 01
        # make sure if was already called
        if self.internal.has("is_run_called"):
            e.code.NotAllowed(
                msgs=[
                    f"You can run only once ..."
                ]
            )
        # -------------------------------------------------- 02
        # setup dpg
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

        # -------------------------------------------------- 03
        # build
        self.build()

        # -------------------------------------------------- 04
        # primary window dpg_id
        _primary_window_dpg_id = self.primary_window.dpg_id
        # set the things for primary window
        dpg.set_primary_window(window=_primary_window_dpg_id, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_dpg_id=_ret, size=16)
        dpg.bind_item_theme(item=_primary_window_dpg_id, theme=asset.Theme.DARK.get())

        # -------------------------------------------------- 05
        # indicate build is done
        self.internal.is_run_called = True

        # dpg related
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
