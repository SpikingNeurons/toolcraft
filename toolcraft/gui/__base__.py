"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import typing as t
import enum
from tkinter import Widget

import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from .. import error as e
from .. import logger
from .. import util
from .. import marshalling as m
from . import assets

_LOGGER = logger.get_logger()

# noinspection PyUnreachableCode
if False:
    from . import Window
    from .widget import Group


class Color(m.FrozenEnum, enum.Enum):
    DEFAULT = [-1, -1, -1, -1]
    WHITE = [255, 255, 255, 255]
    BLACK = [0, 0, 0, 255]
    GREY = [127, 127, 127, 255]
    GREEN = [0, 255, 0, 255]
    BLUE = [0, 0, 255, 255]
    RED = [255, 0, 0, 255]
    # CUSTOM = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_Color"

    # noinspection PyMethodOverriding
    def __call__(self, r: int, g: int, b: int, a: int) -> "Color":
        """
        This method return fake Color when called with Color.CUSTOM(...)
        """
        if self is self.CUSTOM:
            class _:
                ...
            __ = _()
            __.dpg_value = [r, g, b, a]
            # noinspection PyTypeChecker
            return __
        else:
            e.code.CodingError(
                msgs=[
                    f"You are allowed to pass custom values only with "
                    f"{self.CUSTOM} color."
                ]
            )


@dataclasses.dataclass(frozen=True)
class Callback(m.HashableClass, abc.ABC):
    """
    Note that `Callback.fn` will as call back function.
    But when it comes to callback data we need not worry as the fields
    of this instance will serve as data ;)
    """

    @classmethod
    def yaml_tag(cls) -> str:
        return super().yaml_tag() + ":GuiCallback"

    @abc.abstractmethod
    def fn(
        self,
        sender: "Widget",
        app_data: t.Any,
        user_data: t.Union["Widget", t.List["Widget"]]
    ):
        ...


class WidgetInternal(m.Internal):
    dpg_id: t.Union[int, str]
    parent: t.Union["Dashboard", "Widget"]
    before: t.Optional["Widget"]
    is_build_done: bool

    @property
    def dpg_kwargs(self) -> t.Dict[str, t.Any]:
        _ret = {'parent': self.parent.dpg_id}
        if self.before is not None:
            _ret['before'] = self.before.dpg_id
        return _ret


@dataclasses.dataclass(frozen=True)
class Widget(m.HashableClass, abc.ABC):

    @property
    def dpg_id(self) -> t.Union[int, str]:
        return self.internal.dpg_id

    @property
    def parent(self) -> "Widget":
        return self.internal.parent

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

    @property
    @abc.abstractmethod
    def has_dpg_contextmanager(self) -> bool:
        """
        If the dpg component needs a call to end
        Needed when the component is container and is used in with context
        To figure out which component is container refer to
        >>> import dearpygui.dearpygui as _dpg
        And check which methods decorated with `@contextmanager` are yielding
        """
        ...

    @property
    def allow_children(self) -> bool:
        # This is same as property `has_dpg_contextmanager`
        return self.has_dpg_contextmanager

    @property
    def restricted_parent_types(self) -> t.Optional[t.Tuple["Widget", ...]]:
        return None

    @property
    def dashboard(self) -> "Dashboard":
        """
        This recursively gets to root and gets dashboard ... unnecessarily
          expensive
        todo: can we do set_data and get_data from dpg to access this
          Or is there a global attribute to fetch this info ??
        """
        return self.parent.dashboard

    @property
    @util.CacheResult
    def children(self) -> t.List["Widget"]:
        # if not container raise error
        if not self.allow_children:
            e.code.NotAllowed(
                msgs=[
                    f"This property is not available as this Widget does not "
                    f"support adding children",
                    f"Please check class {self.__class__}"
                ]
            )
        # this will be populated when __set_item__ is called
        return []

    def init_validate(self):

        # call super
        super().init_validate()

        # loop over fields
        for f_name in self.dataclass_field_names:
            # get value
            v = getattr(self, f_name)

            # check if Widget and only allow if Form
            if isinstance(v, Widget):
                if not isinstance(self, Form):
                    e.code.CodingError(
                        msgs=[
                            f"You cannot have fields that are Widget. "
                            f"This is only allowed for widget {Form}"
                        ]
                    )

    def get_value(self) -> t.Any:
        return dpg.get_value(item=self.dpg_id)

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

        # hookup delete
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.delete,
            pre_method=cls.delete_pre_runner,
            post_method=cls.delete_post_runner,
        )

    def delete_pre_runner(self):
        ...

    def delete(self):
        # find index
        _this_id = id(self)
        _index = None
        for _i, _w in enumerate(self.parent.children):
            if _this_id == id(_w):
                _index = _i
                break

        # delete widget
        if _index is None:
            e.code.CodingError(
                msgs=[
                    f"We were expecting the instance to be present in children of "
                    f"parent ..."
                ]
            )
            raise
        else:
            # delete self from parents children
            _widget = self.parent.children.pop(_index)
            # simple assert
            assert id(_widget) == _this_id, "should match"
            # delete the UI counterpart
            dpg.delete_item(item=self.dpg_id, children_only=False, slot=-1)

        # todo: make widget unusable ... figure out

    def delete_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
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

        # if container build children
        if self.has_dpg_contextmanager:
            # push_container_stack
            internal_dpg.push_container_stack(hooked_method_return_value)

            # now as layout is completed and build for this widget is completed,
            # now it is time to render children
            for child in self.children:
                child.build()

            # also pop_container_stack as we do not use with context
            internal_dpg.pop_container_stack()

        # set flag to indicate build is done
        self.internal.is_build_done = True

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

    def add_child(
        self,
        widget: "Widget",
        before: "Widget" = None,
    ):
        # -------------------------------------------------- 01
        # validations
        # -------------------------------------------------- 01.01
        # if not container we cannot add widgets
        if not self.has_dpg_contextmanager:
            e.code.CodingError(
                msgs=[
                    f"Widget {self.__class__} is not of container type. We "
                    f"do not support adding widget as child"
                ]
            )
        # -------------------------------------------------- 01.02
        # make sure that you are not adding Dashboard
        if isinstance(widget, Dashboard):
            e.code.CodingError(
                msgs=[
                    f"Note that you are not allowed to add Dashboard as child "
                    f"to any Widget"
                ]
            )

        # -------------------------------------------------- 02
        # if widget is already built then raise error
        if widget.is_built:
            e.code.NotAllowed(
                msgs=[
                    f"The widget is already built",
                ]
            )

        # -------------------------------------------------- 03
        # if already in children raise error
        _widget_id = id(widget)
        for _c in self.children:
            if id(_c) == _widget_id:
                e.validation.NotAllowed(
                    msgs=[
                        f"Looks like the widget is already "
                        f"added to parent."
                    ]
                )

        # -------------------------------------------------- 04
        # set internals
        widget.internal.parent = self
        widget.internal.before = before

        # -------------------------------------------------- 05
        # we can now store widget to children
        # Note that guid is used as it is for dict key
        self.children.append(widget)

        # -------------------------------------------------- 06
        # if thw parent widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            widget.build()

    def hide(self, children_only: bool = False):
        # todo: needs testing
        if children_only:
            for child in dpg.get_item_children(item=self.dpg_id):
                dpg.configure_item(item=child, show=False)
        else:
            dpg.configure_item(item=self.dpg_id, show=False)

    def show(self, children_only: bool = False):
        # todo: needs testing
        if children_only:
            for child in dpg.get_item_children(item=self.dpg_id):
                dpg.configure_item(item=child, show=True)
        else:
            dpg.configure_item(item=self.dpg_id, show=True)

    def set_theme(self, theme: assets.Theme):
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


@dataclasses.dataclass(frozen=True)
class Form(Widget, abc.ABC):
    """
    Form is a special widget which creates a Group container and add all form fields
    to it as defined by layout() method.

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
    def form_fields_group(self) -> "Group":
        """
        The widget that holds all form fields
        """
        from .widget import Group
        return Group()

    @property
    def has_dpg_contextmanager(self) -> bool:
        return False

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
            # if not Hashable class continue
            # that means Widgets and Callbacks will be clones if default supplied
            if not isinstance(v, m.HashableClass):
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
                self.form_fields_group.add_child(widget=v, before=None)

    def build(self) -> t.Union[int, str]:
        # layout
        self.layout()

        # return
        return self.form_fields_group.dpg_id


@dataclasses.dataclass(frozen=True)
class Dashboard(Widget):
    """
    Dashboard is nothing but specialized Window. While note that
    `widget.Window` will be any window that will be inside the Dashboard.

    Refer:
    >>> dpg.add_window

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
    dash_guid: str
    title: str
    width: int = 1370
    height: int = 1200

    @property
    def name(self) -> str:
        return self.dash_guid

    # noinspection PyTypeChecker,PyPropertyDefinition
    @property
    def parent(self) -> "Widget":
        e.code.CodingError(
            msgs=[
                f"You need not use this property for dashboard"
            ]
        )

    @property
    def has_dpg_contextmanager(self) -> bool:
        return True

    @property
    def dashboard(self) -> "Dashboard":
        return self

    @property
    def windows(self) -> t.List["Window"]:
        """
        Note that windows are only added to Dashboard Widget so this property
        is only available in Dashboard

        Note do not cache this as children can dynamically alter so not
        caching will keep this property sync with any window add to children
        property
        """
        from . import Window
        return [_c for _c in self.children if isinstance(_c, Window)]

    # noinspection PyTypeChecker,PyMethodMayBeStatic
    def copy(self) -> "Dashboard":
        e.code.CodingError(
            msgs=[
                f"this is dashboard and you need not use this method as "
                f"already this instance is eligible to be setup ..."
            ]
        )

    def build_pre_runner(self):
        # setup dpg
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()

        # call super
        return super().build_pre_runner()

    # noinspection PyMethodMayBeStatic,PyMethodOverriding
    def build(self) -> t.Union[int, str]:

        # -------------------------------------------------- 01
        # add window
        _ret = dpg.add_window(
            label=self.title,
            on_close=self.on_close,
            width=self.width, height=self.height,
        )

        # -------------------------------------------------- 02
        # set the things for primary window
        dpg.set_primary_window(window=_ret, value=True)
        # todo: have to figure out theme, font etc.
        # themes.set_theme(theme="Dark Grey")
        # assets.Font.RobotoRegular.set(item_dpg_id=_ret, size=16)
        dpg.bind_item_theme(item=_ret, theme=assets.Theme.DARK.get())

        # -------------------------------------------------- 03
        # return
        return _ret

    def run(self):

        # check if ui was built
        if not self.internal.is_build_done:
            e.code.NotAllowed(
                msgs=[
                    f"looks like you missed to build dashboard "
                    f"`{self.name}`"
                ]
            )

        # dpg related
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def on_close(self, sender, data):
        self.delete()
