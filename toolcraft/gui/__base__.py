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


class Color(m.FrozenEnum, enum.Enum):
    DEFAULT = enum.auto()
    WHITE = enum.auto()
    BLACK = enum.auto()
    CUSTOM = enum.auto()
    GREY = enum.auto()
    GREEN = enum.auto()
    BLUE = enum.auto()
    RED = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_color"

    @property
    def dpg_value(self) -> t.List[int]:
        if self is self.DEFAULT:
            return [-1, -1, -1, -1]
        elif self is self.WHITE:
            return [255, 255, 255, 255]
        elif self is self.BLACK:
            return [0, 0, 0, 255]
        elif self is self.RED:
            return [255, 0, 0, 255]
        elif self is self.GREEN:
            return [0, 255, 0, 255]
        elif self is self.BLUE:
            return [0, 0, 255, 255]
        elif self is self.GREY:
            return [127, 127, 127, 255]
        elif self is self.CUSTOM:
            e.code.CodingError(
                msgs=[
                    f"Seems like you are using custom color in that case "
                    f"please pass [r, g, b, a] kwargs i.e. Color.CUSTOM(...)"
                ]
            )
        else:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )

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
    guid: str
    dpg_id: int
    parent: t.Union["Dashboard", "Widget"]
    before: t.Optional["Widget"]
    is_build_done: bool

    @property
    def name(self) -> str:
        return f"{self.parent.name}.{self.guid}"

    @property
    def dpg_kwargs(self) -> t.Dict[str, t.Any]:
        _ret = {'parent': self.parent.dpg_id}
        if self.before is not None:
            _ret['before'] = self.before.dpg_id
        return _ret


@dataclasses.dataclass(frozen=True)
class Widget(m.HashableClass, abc.ABC):

    @property
    def guid(self) -> str:
        return self.internal.guid

    @property
    def dpg_id(self) -> int:
        return self.internal.dpg_id

    @property
    def name(self) -> str:
        _internal = self.internal
        return f"{_internal.parent.name}.{_internal.guid}"

    @property
    def parent(self) -> "Widget":
        if isinstance(self.internal.parent, str):
            raise Exception(self.internal.parent)
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
    def is_container(self) -> bool:
        """
        If the dpg component needs a call to end
        Needed when the component is container and is used in with context
        To figure out which component is container refer to
        >>> import dearpygui.dearpygui as _dpg
        And check which methods decorated with `@contextmanager` are yielding
        """
        ...

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
    def children(self) -> t.Dict[str, "Widget"]:
        # if not container raise error
        if not self.is_container:
            e.code.NotAllowed(
                msgs=[
                    f"This property is not available for Widgets that do not "
                    f"support containers",
                    f"Please check class {self.__class__}"
                ]
            )
        # this will be populated when add_child is called
        return {}

    def init(self):
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
            # bind field if Widget or Callback
            if isinstance(v, (Widget, Callback)):
                self.duplicate_field(field_name=f_name, value=v)

    def get_value(self) -> t.Any:
        return dpg.get_value(item=self.dpg_id)

    def duplicate_field(
        self,
        field_name: str,
        value: t.Union["Widget", Callback]
    ):
        """
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
        # ------------------------------------------------------ 01
        # get field and its default value
        # noinspection PyUnresolvedReferences
        _field = self.__dataclass_fields__[field_name]
        _default_value = _field.default

        # ------------------------------------------------------ 02
        # if value and _default_value are same that means we still have
        # not tricked dataclass and this is the first time things are
        # called so update __dict__ here
        # Note that the below code can also handle
        # _default_value == dataclasses.MISSING
        if id(_default_value) == id(value):
            # this makes a shallow i.e. one level copy
            # we assume that subsequent nested fields can make their own copies
            _dict = {}
            for f_name in value.dataclass_field_names:
                v = getattr(value, f_name)
                _dict[f_name] = v
            value = value.__class__(**_dict)
            # hack to override field value
            self.__dict__[field_name] = value

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
        # delete self from parents children
        del self.parent.children[self.guid]
        # delete the UI counterpart
        dpg.delete_item(item=self.dpg_id, children_only=False, slot=-1)

    def delete_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        ...

    def layout(self):
        """
        Here we decide how to layout all children of this Widget which are
        class fields.

        Note that any widgets that are added dynamically apart from widget
        class fields with add_child later will just build newly added
        components below the last child widget. This can be controlled via
        `parent` and `before` argument anyways/

        Default behaviour is to just build all fields that are Widgets one
        after other. You can of course override this to do more cosmetic
        changes to UI

        Note that we cannot simply loop over children dict because
        + if add_child was called before build() then there will be some
          items in dict
        + the widgets that are fields of this class are not yet added to
          children
        + before calling layout we keep a copy of items that are added in
          children dict and clear the dict. So dict will be empty here
        """
        # ----------------------------------------------------- 01
        # make sure that children dict is empty
        # this is needed because layout will decide the order of children and
        # about rendering them
        if bool(self.children):
            e.code.CodingError(
                msgs=[
                    f"Note that children dict is not empty",
                    "If you have performed add_child before build the code "
                    "before call to layout should back them up and clear "
                    "children dict"
                ]
            )

        # ----------------------------------------------------- 02
        # if there is a widget which is field of this widget then add it
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if isinstance(v, Widget):
                self.add_child(guid=f_name, widget=v, before=None)

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(
                msgs=[
                    f"Widget is already built and registered with:",
                    {
                        'parent': self.internal.parent.name,
                        'guid': self.guid
                    },
                ]
            )

        # ---------------------------------------------------- 02
        # layout ... only done for widgets that are containers
        if self.is_container:
            # ------------------------------------------------ 02.01
            # backup children dict before clearing it
            # this is needed because in some cases there will be add_child
            # performed before build, but we need to give preference to layout
            # method and then again append the backed up elements
            _backup_children = {
                k: v for k, v in self.children.items()
            }
            # ------------------------------------------------ 02.02
            # clear the children dict
            self.children.clear()
            # ------------------------------------------------ 02.03
            # call layout it will add some widgets if any
            self.layout()
            # ------------------------------------------------ 02.04
            # update children with backup
            for k, v in _backup_children.items():
                if k in self.children.keys():
                    e.code.CodingError(
                        msgs=[
                            f"The `layout()` method has added child with guid "
                            f"`{k}` which was already added before `build()` "
                            f"was called"
                        ]
                    )
                self.children[k] = v

    @abc.abstractmethod
    def build(self) -> int:
        ...

    def build_post_runner(
        self, *, hooked_method_return_value: int
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
        if self.is_container:
            # push_container_stack
            internal_dpg.push_container_stack(hooked_method_return_value)

            # now as layout is completed and build for this widget is completed,
            # now it is time to render children
            for child in self.children.values():
                child.build()

            # also pop_container_stack as we do not use with context
            internal_dpg.pop_container_stack()

        # set flag to indicate build is done
        self.internal.is_build_done = True

    def add_child(
        self,
        guid: str,
        widget: "Widget",
        before: "Widget" = None,
    ):
        # -------------------------------------------------- 01
        # validations
        # -------------------------------------------------- 01.01
        # if not container we cannot add widgets
        if not self.is_container:
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
                    f"The widget is already built with:",
                    {
                        'parent': widget.parent.name,
                        'guid': widget.guid
                    },
                    f"You are now attempting to build it again with",
                    {
                        'parent': self.name,
                        'guid': guid
                    }
                ]
            )

        # -------------------------------------------------- 02
        # if guid in children raise error
        if guid in self.children.keys():
            e.validation.NotAllowed(
                msgs=[
                    f"Looks like the widget with guid `{guid}` is already "
                    f"added to parent."
                ]
            )

        # -------------------------------------------------- 04
        # If widget is already assigned to some parent then raise error
        # Note that this is not similar to being is_built ... this simple
        # does mean that you cannot share widgets in multiple places i.e. it
        # must have only one parent and will be unique with peer children of
        # that parent
        if widget.internal.has('guid'):
            e.code.CodingError(
                msgs=[
                    f"Seems like widget was already assigned to some parent "
                    f"and has guid `{widget.guid}`",
                    f"Your attempt to add to some new parent with guid "
                    f"`{guid}` is not possible.",
                ]
            )

        # -------------------------------------------------- 05
        # set internals
        widget.internal.guid = guid
        widget.internal.parent = self
        widget.internal.before = before

        # -------------------------------------------------- 06
        # we can now store widget to children
        # Note that guid is used as it is for dict key
        self.children[guid] = widget

        # -------------------------------------------------- 07
        # if this widget is already built we need to build this widget here
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

    def guid_dom(self) -> t.Tuple[str, t.Union[None, t.Dict]]:
        if not self.is_container:
            return self.guid, None

        _ret = {}
        for _w in self.children.values():
            _name, _children = _w.guid_dom()
            _ret[_name] = _children

        return self.guid, _ret

    def set_theme(self, theme: assets.Theme):
        dpg.set_item_theme(item=self.dpg_id, theme=theme.dpg_id)

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
class Binder:
    """
    Can bind to parent that is already built
    """
    guid: str
    parent: Widget
    before: Widget = None

    def __post_init__(self):
        if not self.parent.is_built:
            e.validation.NotAllowed(
                msgs=[
                    f"The parent is not built so we cannot create binder "
                    f"instance ...",
                    f"Make sure to supply parent that is built"
                ]
            )
        if not self.parent.is_container:
            e.validation.NotAllowed(
                msgs=[
                    f"We expect parent to be of container type so that "
                    f"new widget can be bind ..."
                ]
            )
        if self.guid in self.parent.children.keys():
            e.validation.NotAllowed(
                msgs=[
                    f"You cannot have widget with guid `{self.guid}` to be "
                    f"bind with this parent"
                ]
            )

    def __call__(self, widget: Widget):
        # bind
        self.parent.add_child(
            guid=self.guid, widget=widget, before=self.before,
        )


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
    def is_container(self) -> bool:
        return True

    @property
    def dashboard(self) -> "Dashboard":
        return self

    @property
    def windows(self) -> t.Dict[str, "Window"]:
        """
        Note that windows are only added to Dashboard Widget so this property
        is only available in Dashboard

        Note do not cache this as children can dynamically alter so not
        caching will keep this property sync with any window add to children
        property
        """
        from . import Window
        return {
            k: v
            for k, v in self.children.items() if isinstance(v, Window)
        }

    # noinspection PyTypeChecker,PyMethodMayBeStatic
    def copy(self) -> "Dashboard":
        e.code.CodingError(
            msgs=[
                f"this is dashboard and you need not use this method as "
                f"already this instance is eligible to be setup ..."
            ]
        )

    # noinspection PyMethodMayBeStatic,PyMethodOverriding
    def build(self) -> int:

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
        dpg.set_item_theme(item=_ret, theme=assets.Theme.Dark.dpg_id)

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

        # setup and start
        dpg.setup_viewport()
        dpg.start_dearpygui()

    def on_close(self, sender, data):
        self.delete()
