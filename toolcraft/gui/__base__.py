"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import enum
import typing as t

# noinspection PyUnresolvedReferences,PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import dearpygui.dearpygui as dpg
import numpy as np

from .. import error as e
from .. import logger
from .. import marshalling as m
from .. import util
from . import asset

_LOGGER = logger.get_logger()
COLOR_TYPE = t.Tuple[int, int, int, int]
# PLOT_DATA_TYPE = t.Union[t.List[float], t.Tuple[float, ...]]
PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]

# noinspection PyUnresolvedReferences,PyUnreachableCode
if False:
    from . import plot, window


class Tag:
    _container = {}  # type: t.Dict[str, Widget]

    @classmethod
    def add(cls, tag: str, widget: "Widget"):
        if tag in cls._container.keys():
            e.code.NotAllowed(
                msgs=[f"A widget with tag `{tag}` already exists."])
        if widget.is_tagged:
            e.code.NotAllowed(msgs=[
                f"The widget is already tagged with tag {widget.internal.tag} "
                f"so we cannot assign new tag {tag} ..."
            ])
        cls._container[tag] = widget

    @classmethod
    def get_tag(cls, widget: "Widget") -> t.Optional[str]:
        for k, v in cls._container.items():
            if id(widget) == id(v):
                return k
        return None

    @classmethod
    def get_widget(cls, tag: str) -> t.Optional["Widget"]:
        return cls._container.get(tag, None)

    @classmethod
    def exists(cls, tag_or_widget: t.Union[str, "Widget"]) -> bool:
        if isinstance(tag_or_widget, str):
            return tag_or_widget in cls._container.keys()
        elif isinstance(tag_or_widget, Widget):
            return cls.get_tag(widget=tag_or_widget) is not None
        else:
            e.code.ShouldNeverHappen(
                msgs=[f"Unknown type {type(tag_or_widget)}"])
            raise

    @classmethod
    def remove(cls, tag_or_widget: t.Union[str, "Widget"],
               not_exists_ok: bool):
        if isinstance(tag_or_widget, str):
            if tag_or_widget in cls._container.keys():
                del cls._container[tag_or_widget]
            else:
                if not_exists_ok:
                    return
                e.code.NotAllowed(msgs=[
                    "There is no widget tagged with the tag name "
                    f"`{tag_or_widget}` hence there is nothing to remove"
                ])
                raise
        elif isinstance(tag_or_widget, Widget):
            # get tag
            _tag = cls.get_tag(widget=tag_or_widget)
            # if the widget was not tagged then raise error
            if _tag is None:
                if not_exists_ok:
                    return
                e.code.CodingError(
                    msgs=[f"The widget you want to untag was never tagged"])
                raise
            # remove the tagged widget
            del cls._container[_tag]
        else:
            e.code.CodingError(
                msgs=[f"Unknown type {type(tag_or_widget)} ..."])
            raise


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


class DpgInternal(m.Internal):
    dpg_id: t.Union[int, str]
    is_build_done: bool

    def test_if_others_set(self):
        raise NotImplementedError(f"Implement in class {self.__class__}")


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
        return self.dpg_state["hovered"]

    @property
    def is_active(self) -> bool:
        return self.dpg_state["active"]

    @property
    def is_focused(self) -> bool:
        return self.dpg_state["focused"]

    @property
    def is_clicked(self) -> bool:
        return self.dpg_state["clicked"]

    @property
    def is_left_clicked(self) -> bool:
        return self.dpg_state["left_clicked"]

    @property
    def is_right_clicked(self) -> bool:
        return self.dpg_state["right_clicked"]

    @property
    def is_middle_clicked(self) -> bool:
        return self.dpg_state["middle_clicked"]

    @property
    def is_visible(self) -> bool:
        return self.dpg_state["visible"]

    @property
    def is_edited(self) -> bool:
        return self.dpg_state["edited"]

    @property
    def is_activated(self) -> bool:
        return self.dpg_state["activated"]

    @property
    def is_deactivated(self) -> bool:
        return self.dpg_state["deactivated"]

    @property
    def is_deactivated_after_edit(self) -> bool:
        return self.dpg_state["deactivated_after_edit"]

    @property
    def is_toggled_open(self) -> bool:
        return self.dpg_state["toggled_open"]

    @property
    def is_ok(self) -> bool:
        return self.dpg_state["ok"]

    @property
    def is_shown(self) -> bool:
        return self.dpg_config["show"]

    @property
    def is_enabled(self) -> bool:
        return self.dpg_config["enabled"]

    # @property
    # def pos(self) -> t.Tuple[int, int]:
    #     return tuple(self.dpg_state['pos'])

    @property
    def available_content_region(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state["content_region_avail"])

    @property
    def rect_size(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state["rect_size"])

    @property
    def rect_min(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state["rect_min"])

    @property
    def rect_max(self) -> t.Tuple[int, int]:
        return tuple(self.dpg_state["rect_max"])

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
                        e.code.CodingError(msgs=[
                            f"Check field {self.__class__}.{f_name}",
                            f"For {Form} you can have fields that are {Widget}. ",
                            f"But seems like you are adding non widget {Dpg} class "
                            f"{v.__class__} to this class {self.__class__}",
                        ])
                else:
                    e.code.CodingError(msgs=[
                        f"Check field {self.__class__}.{f_name}",
                        f"You cannot have instance of class {v.__class__} as "
                        f"dataclass fields of {self.__class__}.",
                        f"This is only allowed for {Form} where we only allow "
                        f"{Widget}",
                    ])

    def init(self):
        ...

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(msgs=[
                f"Widget is already built and registered with:",
                {
                    "parent": self.internal.parent.__class__,
                },
            ])

    @abc.abstractmethod
    def build(self) -> t.Union[int, str]:
        ...

    def build_post_runner(self, *, hooked_method_return_value: t.Union[int,
                                                                       str]):
        # if None raise error ... we expect int
        if hooked_method_return_value is None:
            e.code.CodingError(msgs=[
                f"We expect build to return int which happens to be dpg_id"
            ])

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


class WidgetInternal(DpgInternal):
    parent: "ContainerWidget"

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + [
            "parent",
        ]

    def test_if_others_set(self):
        if not self.has("parent"):
            e.code.CodingError(msgs=[
                f"Widget {self.__class__} is not a children to any parent",
                f"Please use some container widget and add this Widget",
            ])


@dataclasses.dataclass
class Widget(Dpg, abc.ABC):
    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    def is_tagged(self) -> bool:
        return Tag.exists(tag_or_widget=self)

    @property
    def parent(self) -> "ContainerWidget":
        return self.internal.parent

    @property
    def root(self) -> "window.Window":
        return self.parent.root

    @property
    def restricted_parent_types(self) -> t.Optional[t.Tuple["Widget", ...]]:
        return None

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.widget.{cls.__name__}"

    def get_user_data(self) -> "USER_DATA":
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
            e.code.CodingError(msgs=[
                f"Was expecting class {self.__class__} to have field `user_data`",
                "This is intended to be used by callback mechanism",
            ])

    def get_tag(self) -> str:
        return Tag.get_tag(widget=self)

    def tag_it(self, tag: str):
        Tag.add(tag=tag, widget=self)

    def untag_it(self):
        Tag.remove(tag_or_widget=self, not_exists_ok=False)

    def delete(self):
        # if tagged then untag
        Tag.remove(tag_or_widget=self, not_exists_ok=True)

        # delete the dpg UI counterpart
        dpg.delete_item(item=self.dpg_id, children_only=False, slot=-1)
        # todo: make _widget unusable ... figure out


USER_DATA = t.Dict[str,
                   t.Union[int, float, str, slice, tuple, list, dict, None,
                           m.FrozenEnum, m.HashableClass, Widget, ], ]


@dataclasses.dataclass
class MovableWidget(Widget, abc.ABC):
    @property
    def index_in_parent_children(self) -> int:
        return self.parent.index_in_children(self)

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.movable_widget.{cls.__name__}"

    def move(self,
             parent: "ContainerWidget" = None,
             before: "MovableWidget" = None):
        """
        Move the item in `parent` and put it before `before`
        """
        # ---------------------------------------------- 01
        # check
        # ---------------------------------------------- 01.01
        # either parent or before should be supplied
        if not ((parent is None) ^ (before is None)):
            e.code.CodingError(msgs=[
                "Either supply parent or before",
                "No need to provide both as parent can extracted from before",
                "While if you supply parent that means you want to add to "
                "bottom of its children",
            ])

        # ---------------------------------------------- 02
        # related to kwarg `before`
        if parent is None:
            parent = before.parent
        _before_index = None
        if before is not None:
            # if before is not None check if it is in parent and get its index
            _before_index = parent.index_in_children(before)
            if _before_index is None:
                e.validation.NotAllowed(msgs=[
                    f"We cannot find `before` widget in children of `parent` "
                    f"you want to move in",
                    "Provide `before` from same `parent` you want to move in or "
                    "supply `None`",
                ])

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
            internal_dpg.move_item(
                self.dpg_id,
                parent=parent.dpg_id,
                before=0 if before is None else before.dpg_id,
            )

    def move_up(self) -> bool:
        """
        If already on top returns False
        Else moves up by one index and returns True as it moved up
        """
        _children_list = self.parent.children
        _index = self.parent.index_in_children(self)
        if _index == 0:
            return False
        _children_list.insert(_index - 1, _children_list.pop(_index))
        internal_dpg.move_item_up(self.dpg_id)
        return True

    def move_down(self) -> bool:
        """
        If already at bottom returns False
        Else moves down by one index and returns True as it moved down
        """
        _children_list = self.parent.children
        _index = self.parent.index_in_children(self)
        if _index == len(_children_list) - 1:
            return False
        _children_list.insert(_index + 1, _children_list.pop(_index))
        internal_dpg.move_item_down(self.dpg_id)
        return True

    def delete(self):
        _children_list = self.parent.children
        _widget = self.parent.children.pop(self.index_in_parent_children)
        return super().delete()


@dataclasses.dataclass
class ContainerWidget(Widget, abc.ABC):
    """
    Widget that can hold children
    Example Group, ChildWindow etc.

    todo: add support to restrict which children can be added to container
    """
    @property
    @util.CacheResult
    def children(self) -> t.List[t.Union[MovableWidget]]:
        # this will be populated when __set_item__ is called
        return []

    # noinspection PyMethodOverriding
    def __call__(self, widget: MovableWidget, before: MovableWidget = None):
        self._add_child(widget=widget)
        if before is not None:
            widget.move(before=before)

    def _add_child(self, widget: MovableWidget):

        # -------------------------------------------------- 01
        # validate
        # -------------------------------------------------- 01.01
        # check if supports before
        if not isinstance(widget, MovableWidget):
            e.code.CodingError(msgs=[
                f"{self.__class__} is not {MovableWidget} i.e. it does not "
                f"supports before so you cannot "
                f"add it as children",
                f"Check if it is possible to have {widget.__class__} as a "
                f"property of class {self.__class__} instead",
                f"If not movable widget then you might think of having it as "
                f"property ... instead of using add_child mechanism",
            ])
        # -------------------------------------------------- 01.02
        # if widget is already built then raise error
        # Note that this will also check if parent and root were not set already ;)
        if widget.is_built:
            e.code.NotAllowed(msgs=[
                "The widget you are trying to add is already built",
                "May be you want to `move()` widget instead.",
            ])

        # -------------------------------------------------- 03
        # set internals
        widget.internal.parent = self

        # -------------------------------------------------- 04
        # we can now store widget inside children list
        self.children.append(widget)

        # -------------------------------------------------- 05
        # if thw parent widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            widget.build()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.container_widget.{cls.__name__}"

    def index_in_children(self, child: MovableWidget) -> t.Optional[int]:
        try:
            return self.children.index(child)
        except ValueError:
            return None

    def clone(self) -> "ContainerWidget":
        if bool(self.children):
            e.code.CodingError(msgs=[
                "Cannot clone as you have added some widgets as children for "
                f"the container widget {self.__class__}"
            ])
        # noinspection PyTypeChecker
        return super().clone()

    def build_post_runner(self, *, hooked_method_return_value: t.Union[int,
                                                                       str]):
        # call super
        super().build_post_runner(
            hooked_method_return_value=hooked_method_return_value)

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

    def delete(self):
        self.clear()
        _children_list = self.parent.children
        _widget = self.parent.children.pop(self.index_in_parent_children)
        # super of ContainerWidget is MovableWidget and
        # super of MovableWidget is Widget
        return super(MovableWidget, self).delete()


@dataclasses.dataclass
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
        _form_fields_container = self.form_fields_container
        _form_fields_container.internal.parent = self.parent

        # layout
        self.layout()

        # return
        return _form_fields_container.build()

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

    def get_user_data(self) -> "USER_DATA":
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
            e.code.CodingError(msgs=[
                f"Was expecting class {self.__class__} to have field `user_data`",
                "This is intended to be used by callback mechanism",
            ])

    def as_dict(self) -> t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        for f_name in self.dataclass_field_names:
            _ret[f_name] = getattr(self, f_name)
        return _ret


class PlotSeriesInternal(DpgInternal):
    parent: "plot.YAxis"

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + [
            "parent",
        ]

    def test_if_others_set(self):
        if not self.has("parent"):
            e.code.CodingError(msgs=[
                f"Widget {self.__class__} is not a children to any parent",
                f"Please use some `YAxis` and add this Widget",
            ])


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
        return f"gui.plot.{cls.__name__}"

    def delete(self):
        # noinspection PyUnresolvedReferences
        del self.parent.all_plot_series[self.label]
        return super().delete()


class PlotItemInternal(DpgInternal):
    parent: "plot.Plot"

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + [
            "parent",
        ]

    def test_if_others_set(self):
        if not self.has("parent"):
            e.code.CodingError(msgs=[
                f"Widget {self.__class__} is not a children to any parent",
                f"Please use some `Plot` and add this Widget",
            ])


@dataclasses.dataclass
class PlotItem(Widget, abc.ABC):
    @property
    @util.CacheResult
    def internal(self) -> PlotItemInternal:
        return PlotItemInternal(owner=self)

    @property
    def parent(self) -> "plot.Plot":
        return self.internal.parent

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.plot.{cls.__name__}"

    def delete(self):
        # noinspection PyUnresolvedReferences
        del self.parent.all_plot_items[self.label]
        return super().delete()
