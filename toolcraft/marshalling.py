import abc
import dataclasses
import datetime
import hashlib
import sys
import inspect
import time
import types
import pathlib
import contextvars
import enum
import traceback
import typing as t
import rich
import asyncio
from rich import progress
from rich import spinner
from rich import columns
import numpy as np
import pyarrow as pa
import yaml

from . import error as e
from . import logger, settings, util


# to avoid cyclic imports
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from . import gui, storage
    from . import richy

T = t.TypeVar('T', bound='Tracker')
_LOGGER = logger.get_logger()
_LITERAL_CLASS_NAME = 'LITERAL'
_RULE_CHECKER = "__rule_checker__"

_RULE_CHECKERS_TO_BE_CHECKED = {}  # type: t.Dict[int, RuleChecker]


CUSTOM_KERAS_CLASSES_MAP = {
    "loss": dict()
}

# Class to keep track of all concrete HashableClass class's used in the
# entire application
# noinspection PyTypeChecker
ALL_TRACKERS = None  # type: t.List[t.Type[YamlRepr]]
YAML_TAG_MAPPING = {}

# use this as default value for kwargs in HashableClass.__call__ to indicate
# that kwarg was not provided
NOT_PROVIDED = "__NOT_PROVIDED__"

# todo: come up with more appropriate file extensions if needed like
#  model.info, dataset.info, file_group.info,
#  model.config, dataset.config ...
# HASH_Suffix.INFO = ".hashinfo"
# HASH_Suffix.CONFIG = ".hashconfig"
# META_Suffix.INFO = ".metainfo"


class _ReadOnlyClass(type):
    def __setattr__(self, key, value):
        raise e.code.NotAllowed(msgs=[
            f"Class {self} is read only.",
            f"You cannot override its attribute {key!r} programmatically.",
            f"Edit it during class definition ...",
        ])


class UseMethodInForm:
    """
    A decorator for HashableCLass methods that can then be used in forms like
    HashableMethodsRunnerForm and DoubleSplitForm
    """

    def __init__(
        self, label_fmt: str = None, call_as_async: bool = False
    ):
        """

        Args:
            label_fmt: label for button ... if str is property we will
              call it to get label
            call_as_async: can call method in async task ...
        """
        self.label_fmt = label_fmt
        self.call_as_async = call_as_async

    @staticmethod
    async def async_call(_fn: t.Callable):
        from .gui import widget

        try:

            # loop infinitely
            while widget.does_exist:

                # dont update if not visible
                # todo: can we await on bool flags ???
                if not widget.is_visible:
                    await asyncio.sleep(0.2)
                    continue

                # update widget
                widget.set_value(f"{int(widget.get_value())+1:03d}")

                # change update rate based on some value
                if self.some_value == "first hashable ...":
                    await asyncio.sleep(1)
                    if int(widget.get_value()) == 10:
                        break
                else:
                    await asyncio.sleep(0.1)
                    if int(widget.get_value()) == 50:
                        break

        except Exception as _e:
            if widget.does_exist:
                raise _e
            else:
                ...

    @staticmethod
    def make_async_caller_fn(_fn: t.Callable) -> t.Callable:

        async def _async_fn(_self, grp_widget: gui.widget.Group):

            # todo: remove later just for sanity check
            # noinspection PyUnresolvedReferences
            assert id(_self) == id(_fn.__self__), "was expecting this to be same"

        def _new_fn(_self):
            _grp = gui.widget.Group(horizontal=True)
            with _grp:
                gui.widget.Text(default_value="count")
                _txt = gui.widget.Text(default_value="000")
                gui.Engine.gui_task_add(fn=self.txt_update_fn, fn_kwargs=dict(widget=_txt))
            return _grp

        return _new_fn

    def __call__(self, fn: t.Callable):
        """
        todo: add signature test to confirm that Widget or any of its subclass
          is returned by fn
        todo: currently fn cannot have any kwargs but eventually read the kwargs and
          build a form do that parametrized widget running is possible ...
          a bit complex but possible
        """
        # make new fn
        if self.call_as_async:
            _new_fn = self.make_async_caller_fn(fn)
        else:
            _new_fn = fn

        # set vars
        self.fn = _new_fn

        # store self inside fn
        # also check `cls.get_from_hashable_fn` which will help get access
        # to this instance
        setattr(fn, f"_{self.__class__.__name__}", self)

        # return fn as this is decorator
        return self.fn

    @classmethod
    def get_from_hashable_fn(
        cls, hashable: "HashableClass", fn_name: str
    ) -> "UseMethodInForm":
        try:
            _fn = getattr(hashable.__class__, fn_name)
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"Function with name {fn_name} is not present in class "
                    f"{hashable.__class__}"
                ]
            )
        try:
            return getattr(_fn, f"_{cls.__name__}")
        except AttributeError:
            raise e.code.CodingError(
                msgs=[
                    f"The function {_fn} was not decorated with {UseMethodInForm}"
                ]
            )

    def get_button_widget(
        self,
        hashable: "HashableClass",
        receiver: "gui.widget.ContainerWidget",
        allow_refresh: bool,
        group_tag: str = None,
    ) -> "gui.widget.Button":
        from . import gui

        # ---------------------------------------------------- 01
        # test callable name
        _callable_name = self.fn.__name__
        if not util.rhasattr(hashable, _callable_name):
            raise e.code.CodingError(msgs=[
                f"Callable `{_callable_name}` not available for "
                f"HashableClass {hashable.__class__}"
            ])

        # ---------------------------------------------------- 02
        # make label for button
        if isinstance(getattr(hashable.__class__, self.label_fmt, None), property):
            _button_label = getattr(hashable, self.label_fmt)
        elif self.label_fmt is None:
            _button_label = f"{hashable.__class__.__name__}.{hashable.hex_hash} " \
                            f"({_callable_name})"
        elif isinstance(self.label_fmt, str):
            _button_label = self.label_fmt
        else:
            raise e.code.CodingError(
                msgs=[f"unknown type {type(self.label_fmt)}"]
            )

        # ---------------------------------------------------- 03
        # create callback
        _callback = gui.callback.HashableMethodRunnerCallback(
            hashable=hashable,
            callable_name=_callable_name,
            receiver=receiver,
            allow_refresh=allow_refresh,
            group_tag=group_tag,
        )

        # ---------------------------------------------------- 04
        # create and return button
        return gui.widget.Button(
            label=_button_label,
            callback=_callback,
        )


class Internal:
    """
    Need:
      As Hashable dataclass is Frozen we need to have some way of storing
      variables that can be updated and not part of serialization process
    """

    prefetched_on_first_call: bool
    in_with_context: bool = False
    is_called: bool = False
    richy_panel: "richy.StatusPanel" = None

    class LITERAL:
        store_key = "INTERNAL"

    @property
    def owner(self) -> "Tracker":
        return self.__owner__

    @property
    @util.CacheResult
    def __field_names__(self) -> t.List[str]:
        _ret = []
        for _c in self.__class__.__mro__:
            if hasattr(_c, "__annotations__"):
                _ret.extend(list(_c.__annotations__.keys()))
        return list(set(_ret))

    def __init__(self, owner: "Tracker"):

        # store_key must not be present as it is not loaded from serialized file
        if hasattr(owner, self.LITERAL.store_key):
            raise e.code.CodingError(msgs=[
                f"Did you miss to cache the `internal` property?",
                f"Looks like {self.LITERAL.store_key} is already present",
                f"We do not expect this to happen.",
            ])

        # keep internal instance reference in owner
        owner.__dict__[self.LITERAL.store_key] = self

        # also store owner instance reference
        self.__owner__ = owner

        # dynamic container to track locked fields
        self.__locked_fields__ = []  # type: t.List[str]

        # if annotations have default values then make them available in
        # container
        for _n in self.__field_names__:
            try:
                _v = getattr(self.__class__, _n)
                # if list or dict then acts like factory to make new object per instance
                if _v == list:
                    _v = list()
                    self.__dict__[_n] = _v
                    continue
                if _v == dict:
                    _v = dict()
                    self.__dict__[_n] = _v
                    continue
                # todo test _v for immutability ... the same _v across multiple internals can cause issues
                #    right now we are setting as it is without testing for immutability
                #    except for list and dict which we are making immutable by small hack
                setattr(self, _n, _v)
            except AttributeError:
                ...

    def __setattr__(self, key: str, value):
        # bypass dunder keys
        if key.startswith("__"):
            return super().__setattr__(key, value)

        # only keys that are annotated can be set
        e.validation.ShouldBeOneOf(
            value=key,
            values=self.__field_names__,
            msgs=[
                f"Member `{key}` is not annotated in class "
                f"{self.__class__} so you cannot set it."
            ],
        ).raise_if_failed()

        # if item is allowed to be set only once then do not allow it to be
        # set again
        if key not in self.vars_that_can_be_overwritten():
            if self.has(key):
                if isinstance(value, HashableClass):
                    _str_value = value.yaml()
                else:
                    _str_value = str(value)
                raise e.code.NotAllowed(msgs=[
                    f"The item `{key}` is already present in the internal "
                    f"object.",
                    f"Please refrain from overwriting it as it is "
                    f"configured to be written only once.",
                    f"You are overwriting it with value `{_str_value}`",
                    f"In case you want to overwrite it then override "
                    f"method `self.vars_that_can_be_overwritten` so "
                    f"that we allow you to overwrite it.",
                ])

        # if item is locked do not allow to overwrite it
        if key in self.__locked_fields__:
            raise e.code.CodingError(
                msgs=[f"Internal field `{key}` is locked so you cannot update it"]
            )

        # set attribute
        return super().__setattr__(key, value)

    def __getattr__(self, item):

        # bypass dunder keys
        if item.startswith("__"):
            return super().__getattribute__(item)

        # check if already set
        # We go via __dict__ as using self.has causes recursion
        if item not in self.__dict__.keys():
            raise e.code.CodingError(msgs=[
                f"You cannot access annotated attribute `{item}` as it is "
                f"not yet set",
            ])

        # return
        return super().__getattribute__(item)

    # noinspection PyMethodMayBeStatic
    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return ["in_with_context", "is_called", "richy_panel"]

    def has(self, item: str) -> bool:
        if item not in self.__field_names__:
            raise e.code.CodingError(msgs=[
                f"You can only test has(...) for fields that are annotated",
                f"Item `{item}` is not one of "
                f"{self.__field_names__}",
            ])
        return item in self.__dict__.keys()

    def lock_field(self, item: str):
        if item not in self.__field_names__:
            raise e.code.CodingError(msgs=[
                f"You can only lock fields that are annotated",
                f"Item `{item}` is not one of "
                f"{self.__field_names__}",
            ])
        if item in self.__locked_fields__:
            raise e.code.NotAllowed(
                msgs=[f"Field `{item}` is already locked"]
            )
        self.__locked_fields__.append(item)

    def unlock_field(self, item: str):
        if item not in self.__field_names__:
            raise e.code.CodingError(msgs=[
                f"You can only unlock fields that are annotated",
                f"Item `{item}` is not one of "
                f"{self.__field_names__}",
            ])
        if item not in self.__locked_fields__:
            raise e.code.NotAllowed(
                msgs=[f"Field `{item}` was not locked to unlock"]
            )
        self.__locked_fields__.remove(item)


class RuleChecker:

    """
    Note that this decorator must be applied on class after @dataclasses.dataclass ...

    todo: do not be tempted to do load time analysis of dataclass as it is tough from
      our experience
      + We do not want to dataclass related checks as it is out of scope for
        __init_subclass__ method, and we cannot grab that class when completely loaded
      + The only need for us related to dataclasses is to check if the child classes are
        also decorated with dataclass or not ... for that we should only so static code
        analysis to detect decorator ...

    todo: code analysis takes lot of time
      + provide a switch to disable code check (This is now DONE :))
        (it is now easy because of current decorator mechanism)
      + skip some modules like gui while checking ... or bypass some checks for them
        this can speed up checks
    """

    def __init__(
        self, *,
        class_can_be_overridden: bool = True,
        things_to_be_cached: t.List[str] = None,
        things_not_to_be_cached: t.List[str] = None,
        things_not_to_be_overridden: t.List[str] = None,
        restrict_dataclass_fields_to: t.List[str] = None,
    ):
        self.class_can_be_overridden = class_can_be_overridden
        self.things_to_be_cached = \
            [] if things_to_be_cached is None else things_to_be_cached
        self.things_not_to_be_cached = \
            [] if things_not_to_be_cached is None else things_not_to_be_cached
        self.things_not_to_be_overridden = \
            [] if things_not_to_be_overridden is None else things_not_to_be_overridden
        # todo: the child classes do not get this setting from parent class
        #   test with job.Runner ... child classes of Runner do not obey this
        #   restriction ... also test other init kwargs above even they might not
        #   be propagating information downstream
        self.restrict_dataclass_fields_to = restrict_dataclass_fields_to
        # noinspection PyTypeChecker
        self.parent = None  # type: RuleChecker
        # noinspection PyTypeChecker
        self.decorated_class = None  # type: t.Type[Tracker]

    def __call__(
        self, checker,
        # todo: returning this causes issue with Typing as it starts thinking
        #  everything is Tracker ... find a way to figure out typing protocol that
        #  understand in context to class on which we decorated this
        # self, tracker: t.Type["Tracker"],
        rule_checker_set_from_init_subclass: bool = False,
    ):
        # todo: returning this causes issue with Typing as it starts thinking
        #  everything is Tracker ... find a way to figure out typing protocol that
        #  understand in context to class on which we decorated this
        # ) -> t.Type["Tracker"]:
        """
        This just keeps reference for class that is decorated
        """
        # ---------------------------------------------------------------- 01
        # there will never be a decorated class
        if self.decorated_class is not None:
            raise e.code.CodingError(
                msgs=[
                    f"This is suppose to be None as __call__ will be called only "
                    f"once per instance of RuleChecker ..."
                ]
            )
        # set it now here
        self.decorated_class = checker
        # ---------------------------------------------------------------- 02
        # if super parent then there will be no call to __init_subclass__ so
        # we have to handle things i.e. add fake RuleChecker so that anyway
        # that will delete below and new rule checker will be added
        try:
            # A way to detect if Tracker is not fully loaded it will raise NameError
            # By any chance if it matches then also we raise NameError so that
            # exception handling takes over
            if checker == Checker:
                raise NameError
        except NameError:
            setattr(self.decorated_class, _RULE_CHECKER, self)
            _RULE_CHECKERS_TO_BE_CHECKED[id(self)] = self
        # ---------------------------------------------------------------- 03
        # if you are initiating from __init_subclass__
        if rule_checker_set_from_init_subclass:
            # set the RuleChecker to decorated_class  ...
            # in case the class has true decorator
            # then that decorator code will delete this decorator in next code ...
            # or else this decorator will be used to check code
            if _RULE_CHECKER not in self.decorated_class.__dict__.keys():
                # keep the reference of rule checker in decorated class
                # note this is mapping proxy, so we use setattr
                setattr(self.decorated_class, _RULE_CHECKER, self)
                _RULE_CHECKERS_TO_BE_CHECKED[id(self)] = self
            else:
                raise e.code.CodingError(
                    msgs=[
                        f"We assume you are calling from __init_subclass__ "
                        f"so we expect that {_RULE_CHECKER} will not be setup yet as "
                        f"you will be creating fresh RuleChecker instance"
                    ]
                )
        # ---------------------------------------------------------------- 04
        # if this is true decorator used on top of class
        else:
            # remove the rule checker added by __init_subclass__ and instead have self
            if _RULE_CHECKER in self.decorated_class.__dict__.keys():
                # do for rule checkers
                del _RULE_CHECKERS_TO_BE_CHECKED[
                    id(self.decorated_class.__dict__[_RULE_CHECKER])]
                _RULE_CHECKERS_TO_BE_CHECKED[id(self)] = self
                # note this is mapping proxy, so we use delattr and setattr
                delattr(self.decorated_class, _RULE_CHECKER)
                setattr(self.decorated_class, _RULE_CHECKER, self)
            else:
                raise e.code.CodingError(
                    msgs=[
                        f"You are not calling this code from __init_subclass__ and we "
                        f"assume this is actual decorator applied on class",
                        f"So we expect that {_RULE_CHECKER} will be set by now as we "
                        f"will delete it first and then add this RuleChecker on "
                        f"top of it",
                        f"Check class {checker}"
                    ]
                )
        # ---------------------------------------------------------------- 05
        # return
        return checker

    def check(self):
        """
        This will happen when all classes are loaded
        """
        # ---------------------------------------------------------- 01
        # expect parent to be None as this is called only once per RuleCHecker
        if self.parent is not None:
            raise e.code.CodingError(
                msgs=[
                    f"We expect this parent to None as this is called only once "
                    f"per RuleChecker"
                ]
            )
        # set parent rule checker ... expect for super parent Tracker
        if self.decorated_class not in [Checker, Tracker]:
            if self.decorated_class.__mro__[1] != Checker:
                self.parent = getattr(self.decorated_class.__mro__[1], _RULE_CHECKER)

        # ---------------------------------------------------------- 02
        # test if current decorator settings agree with parent
        # and also merge some settings
        self.agree_with_parent_and_merge_settings()

        # ---------------------------------------------------------- 03
        # check for dataclass decorator
        self.check_if_decorated_with_dataclass()

        # ---------------------------------------------------------- 04
        # check_things_to_be_cached
        self.check_things_to_be_cached()

        # ---------------------------------------------------------- 05
        # check_things_not_to_be_cached
        self.check_things_not_to_be_cached()

        # ---------------------------------------------------------- 06
        # check_things_not_to_be_overridden
        self.check_things_not_to_be_overridden()

        # ---------------------------------------------------------- 07
        # check_related_to_class_Tracker
        self.check_related_to_class_Tracker()

        # ---------------------------------------------------------- 08
        # check_related_to_class_HashableClass
        self.check_related_to_class_HashableClass()

        # ---------------------------------------------------------- 09
        # check_related_to_class_FrozenEnum
        self.check_related_to_class_FrozenEnum()

        # ---------------------------------------------------------- xx
        # todo: based on return type of properties and instance methods without
        #  argument warn users to cache results

        # ---------------------------------------------------------- xx
        # todo: find a way to check if super() calls are made in properties and methods
        #   see inspect.getsource to read code string

        # ---------------------------------------------------------- xx
        # todo: test that RuleChecker is the first decorator on the class
        #  i.e. dataclass needs to be above RuleChecker
        #   see inspect.getsource to read code string

        # ---------------------------------------------------------- xx
        # todo: check that @property decorator is applied above @util.CacheResult
        #   see inspect.getsource to read code string

        # ---------------------------------------------------------- xx
        # todo: check should_add_raise_explicitly_class_field ...
        #  check toolcraft._bulk_code_refactor._script.py

        # ---------------------------------------------------------- xx
        # todo: check add_raise_before_exceptions_to_be_raised_explicitly ...
        #  check toolcraft._bulk_code_refactor._script.py

        # ---------------------------------------------------------- xx
        # todo: check add_raise_if_expected_after_some_exceptions ...
        #  check toolcraft._bulk_code_refactor._script.py

    # noinspection PyPep8Naming
    def check_related_to_class_FrozenEnum(self):
        # ---------------------------------------------------------- 01
        # things to skip
        # ---------------------------------------------------------- 01.01
        # if FrozenEnum then it is parent class so ignore
        if self.decorated_class == FrozenEnum:
            return
        # ---------------------------------------------------------- 01.02
        # nothing to do if not a subclass of FrozenEnum
        if not issubclass(self.decorated_class, FrozenEnum):
            return
        # ---------------------------------------------------------- 01.03
        # If subclass but have no annotated fields then that means we want to subclass
        # it later while this class should be treated as subclass ...
        # We do this as we cannot declare it as abstract class as the behaviour does
        # not work when we want enums ...
        if not bool(getattr(self.decorated_class, '__annotations__', {})):
            return

        # ---------------------------------------------------------- 02
        # check if the subclassing class also extends enum.Enum
        if not issubclass(self.decorated_class, enum.Enum):
            raise e.code.CodingError(
                msgs=[
                    f"While subclassing `FrozenEnum` make sure "
                    f"that it also extends `enum.Enum`",
                    f"Check class {self.decorated_class}"
                ]
            )

    # noinspection PyPep8Naming
    def check_related_to_class_HashableClass(self):
        # ---------------------------------------------------------- 01
        # if HashableClass ignore
        if self.decorated_class == HashableClass:
            return
        # nothing to do if not a subclass of YamlRepr
        if not issubclass(self.decorated_class, HashableClass):
            return
        # cls to consider
        _hashable_cls = self.decorated_class
        # fetch attributes that are annotated
        # Note: dataclasses.fields will not work here as the class still
        #   does not know that it is dataclass
        _annotated_attr_keys = []
        for _c in _hashable_cls.__mro__:
            if hasattr(_c, '__annotations__'):
                _annotated_attr_keys += list(_c.__annotations__.keys())

        # ---------------------------------------------------------- 02
        # class should not be local
        if str(_hashable_cls).find("<locals>") > -1:
            raise e.validation.NotAllowed(
                msgs=[
                    f"Hashable classes can only be first class classes.",
                    f"Do not define classes locally, declare them at module "
                    f"level.",
                    f"Check class {_hashable_cls}"
                ]
            )

        # ---------------------------------------------------------- 03
        # check all non dunder attributes
        for _attr_k, _attr_v in util.fetch_non_dunder_attributes(_hashable_cls):

            # ------------------------------------------------------ 03.01
            # if _attr_v is property, function or a method ... no need to check
            # anything and we can continue
            _allowed_types = (
                property,
                types.FunctionType,
                types.MethodType,
                util.HookUp,
            )
            # noinspection PyTypeChecker
            if isinstance(_attr_v, _allowed_types):
                continue

            # ------------------------------------------------------ 03.02
            # no attribute should start with _
            if _attr_k.startswith('_'):
                # if abstract class used this will be present
                # the only field that starts with _ which we allow
                if _attr_k == '_abc_impl':
                    continue
                # anything else raise error
                raise e.validation.NotAllowed(
                    msgs=[
                        f"Attribute {_attr_k} is not one of {_allowed_types} "
                        f"and it starts with `_`",
                        f"Please check attribute {_attr_k} of class {_hashable_cls}"
                    ]
                )

            # ------------------------------------------------------ 03.03
            # if special helper classes that stores all LITERALS
            if _attr_k == _LITERAL_CLASS_NAME:
                # NOTE: we already check if class LITERAL is correctly
                # subclassed in super method .... so no need to do here
                continue

            # ------------------------------------------------------ 03.04
            # avoid using ClassVar and InitVar
            if _attr_k in _annotated_attr_keys:
                # _attr_v is a typing.ClassVar raise error
                # simple way to see if typing was used as annotation value
                if hasattr(_attr_v, '__origin__'):
                    if _attr_v.__origin__ == t.ClassVar:
                        raise e.code.CodingError(
                            msgs=[
                                f"We do not allow class variable {_attr_k} "
                                f"... check class {_hashable_cls}"
                            ]
                        )
                # if `dataclasses.InitVar` raise error
                if isinstance(_attr_v, dataclasses.InitVar):
                    raise e.code.CodingError(
                        msgs=[
                            f"We co not allow using dataclass.InitVar.",
                            f"Please check annotated field {_attr_k} in "
                            f"class {_hashable_cls}"
                        ]
                    )
                # if a valid dataclass field continue
                continue

            # ------------------------------------------------------ 03.05
            # if we reached here we do not understand the class attribute so
            # raise error
            # print(cls.__annotations__.keys(), "::::::::::::::::::", cls)
            raise e.code.NotAllowed(
                msgs=[
                    f"Found an attribute `{_attr_k}` with: ",
                    dict(
                        type=f"{type(_attr_v)}",
                        value=f"{_attr_v}",
                    ),
                    f"Problem with attribute {_attr_k} of class {_hashable_cls}",
                    f"It is neither one of {_allowed_types}, nor is it "
                    f"defined as dataclass field.",
                    f"Note that if you are directly assigning the annotated "
                    f"field it will not return dataclass field so please "
                    f"assign it with "
                    f"`dataclass.field(default=...)` or "
                    f"`dataclass.field(default_factory=...)`",
                ]
            )

        # ---------------------------------------------------------- 05
        # if not None then that means we want to restrict dataclass fields
        _restrict_dataclass_fields_to = self.restrict_dataclass_fields_to
        if _restrict_dataclass_fields_to is not None:
            if bool(_restrict_dataclass_fields_to):
                for _attr_k in _annotated_attr_keys:
                    e.validation.ShouldBeOneOf(
                        value=_attr_k, values=_restrict_dataclass_fields_to,
                        msgs=[
                            f"Please use only allowed dataclass fields for class "
                            f"{_hashable_cls}..."
                        ]
                    ).raise_if_failed()
            else:
                # empty list was supplied that means you dont want to use any fields
                if bool(_annotated_attr_keys):
                    raise e.code.CodingError(
                        msgs=[
                            f"Please do not specify ant dataclass fields for class "
                            f"{_hashable_cls}",
                            f"We found below fields defined",
                            _annotated_attr_keys,
                        ]
                    )

        # ---------------------------------------------------------- 05
        # do not override dunder methods
        _general_dunders_to_ignore = [
            # python adds it
            '__module__', '__dict__', '__weakref__', '__doc__', '__match_args__',

            # dataclass related
            '__annotations__', '__abstractmethods__', '__dataclass_params__',
            '__dataclass_fields__',

            # dataclass adds this default dunders to all dataclasses ... we have
            # no control over this ;(
            '__init__', '__repr__', '__eq__', '__setattr__',
            '__delattr__', '__hash__',

            # we allow this
            '__call__',

            # this is used by RuleChecker
            _RULE_CHECKER,
        ]
        if _hashable_cls != HashableClass:
            for k in _hashable_cls.__dict__.keys():
                if k.startswith("__") and k.endswith("__"):
                    if k not in _general_dunders_to_ignore:
                        raise e.code.CodingError(
                            msgs=[
                                f"You are not allowed to override dunder "
                                f"methods in any subclass of {HashableClass}",
                                f"Please check class {_hashable_cls} and avoid defining "
                                f"dunder method `{k}` inside it"
                            ]
                        )

    # noinspection PyPep8Naming
    def check_related_to_class_Tracker(self):
        # ---------------------------------------------------------- 01
        # nothing to do if Tracker i.e. super parent
        if self.parent is None:
            return

        # ---------------------------------------------------------- 02
        # test if LITERAL is extended properly
        _parent_literal_class = self.parent.decorated_class.LITERAL
        e.validation.ShouldBeSubclassOf(
            value=self.decorated_class.LITERAL, value_types=(_parent_literal_class, ),
            msgs=[
                f"We expect a nested class of class {self.decorated_class} with name "
                f"`{_LITERAL_CLASS_NAME}` to "
                f"extend the class {_parent_literal_class}"
            ]
        ).raise_if_failed()

    def check_things_not_to_be_overridden(self):
        # ---------------------------------------------------------- 01
        # nothing to do if Tracker i.e. super parent
        if self.parent is None:
            return

        # ---------------------------------------------------------- 02
        for _t in self.parent.things_not_to_be_overridden:
            try:
                if getattr(self.decorated_class, _t) != \
                        getattr(self.parent.decorated_class, _t):
                    raise e.code.CodingError(
                        msgs=[
                            f"Please do not override method/property "
                            f"`{_t}` in class {self.decorated_class}"
                        ]
                    )
            except AttributeError:
                raise e.code.CodingError(
                    msgs=[
                        f"Property/method with name `{_t}` does not belong to class "
                        f"{self.decorated_class} or any of its parent class",
                        f"Please check if you provided wrong string ..."
                    ]
                )

    def check_things_not_to_be_cached(self):
        for _t in self.things_not_to_be_cached:
            # get
            try:
                _method_or_prop = getattr(self.decorated_class, _t)
            except AttributeError:
                raise e.code.CodingError(
                    msgs=[
                        f"Property/method with name `{_t}` does not belong to class "
                        f"{self.decorated_class} or any of its parent class",
                        f"Please check if you provided wrong string ..."
                    ]
                )
            # if abstract no sense in checking if cached
            if getattr(_method_or_prop, '__isabstractmethod__', False):
                continue
            # check if cached
            if util.is_cached(_method_or_prop):
                raise e.code.CodingError(
                    msgs=[
                        f"We expect you not to cache property/method "
                        f"`{_t}`. Do not use  decorator "
                        f"`@util.CacheResult` in "
                        f"class {self.decorated_class} for `{_t}`"
                    ]
                )

    def check_things_to_be_cached(self):
        for _t in self.things_to_be_cached:
            # get
            try:
                _method_or_prop = getattr(self.decorated_class, _t)
            except AttributeError:
                raise e.code.CodingError(
                    msgs=[
                        f"Property/method with name `{_t}` does not belong to class "
                        f"{self.decorated_class} or any of its parent class",
                        f"Please check if you provided wrong string ..."
                    ]
                )
            # if abstract no sense in checking if cached
            if getattr(_method_or_prop, '__isabstractmethod__', False):
                continue
            # check if cached
            if not util.is_cached(_method_or_prop):
                raise e.code.CodingError(
                    msgs=[
                        f"If defined we expect you to cache property/method `{_t}` "
                        f"using decorator `@util.CacheResult` in "
                        f"class {self.decorated_class}"
                    ]
                )

    def check_if_decorated_with_dataclass(self):
        """
        do not be tempted to do load time analysis of dataclass as it is tough from
        our experience
          + We do not want to dataclass related checks as it is out of scope for
            __init_subclass__ method, and we cannot grab that class when completely loaded
          + The only need for us related to dataclasses is to check if the child classes are
            also decorated with dataclass or not ... for that we should only so static code
            analysis to detect decorator ...

        Here we do very simple static code analysis ... if parent class
        has @dataclass decorator we expect the same from this class
        """
        # ---------------------------------------------------------- 01
        # nothing to do if Tracker i.e. super parent
        if self.parent is None:
            return

        # ---------------------------------------------------------- 02
        # first get current classes and detect if it has dataclass decorator
        # if there is dataclass decorator no need to investigate more
        _current_class = self.decorated_class
        # noinspection PyProtectedMember,PyUnresolvedReferences
        if dataclasses._FIELDS in _current_class.__dict__.keys() and \
                dataclasses._PARAMS in _current_class.__dict__.keys():
            return

        # ---------------------------------------------------------- 03
        # now that current class has no @dataclass decorator test for parent class
        # note we do not use self.parent.decorated_class as it might skip
        # immediate parent class
        _parent_class = _current_class.__mro__[1]
        # noinspection PyProtectedMember,PyUnresolvedReferences
        if dataclasses._FIELDS in _current_class.__dict__.keys() and \
                dataclasses._PARAMS in _current_class.__dict__.keys():
            raise e.code.CodingError(
                msgs=[
                    f"Parent class {_parent_class} of class {_current_class} is a "
                    f"dataclass ... so please make sure to decorate accordingly ..."
                ]
            )

    def agree_with_parent_and_merge_settings(self):
        """
        test if current decorator settings agree with parent
        and also merge some settings
        """
        # ---------------------------------------------------------- 01
        # nothing to do if Tracker i.e. super parent
        if self.parent is None:
            return

        # ---------------------------------------------------------- 02
        # class_can_be_overridden
        if not self.parent.class_can_be_overridden:
            raise e.code.CodingError(
                msgs=[
                    f"Parent class {self.parent.decorated_class} is configured to "
                    f"not be overridden. So please refrain from doing it ..."
                ]
            )

        # ---------------------------------------------------------- 03
        # merge things_to_be_cached
        for _t in self.things_to_be_cached:
            if _t in self.parent.things_to_be_cached:
                raise e.code.CodingError(
                    msgs=[
                        f"You have already configured `{_t}` in RuleChecker of parent class "
                        f"{self.parent.decorated_class} ..."
                    ]
                )
        self.things_to_be_cached += self.parent.things_to_be_cached

        # ---------------------------------------------------------- 04
        # merge things_to_be_cached
        for _t in self.things_not_to_be_cached:
            if _t in self.parent.things_not_to_be_cached:
                raise e.code.CodingError(
                    msgs=[
                        f"You have already `{_t}` in parent class "
                        f"{self.parent.decorated_class} as well as this class "
                        f"{self.decorated_class} ..."
                    ]
                )
        self.things_not_to_be_cached += self.parent.things_not_to_be_cached

        # ---------------------------------------------------------- 05
        # merge things_to_be_cached
        for _t in self.things_not_to_be_overridden:
            if _t in self.parent.things_not_to_be_overridden:
                raise e.code.CodingError(
                    msgs=[
                        f"You have already configured `{_t}` in parent class "
                        f"{self.parent.decorated_class} ..."
                    ]
                )
        self.things_not_to_be_overridden += self.parent.things_not_to_be_overridden


class Checker:

    class LITERAL(metaclass=_ReadOnlyClass):
        def __new__(cls, *args, **kwargs):
            raise e.code.NotAllowed(msgs=[
                f"This class is meant to be used to hold class "
                f"variables only",
                f"Do not try to create instance of {cls} ...",
            ])

    @classmethod
    def __init_subclass__(cls, **kwargs):
        # declare
        global ALL_TRACKERS

        # if None set it with SmartList
        if ALL_TRACKERS is None:
            ALL_TRACKERS = []

        # add to list
        ALL_TRACKERS.append(cls)

        # call super
        super().__init_subclass__(**kwargs)

        # call class_init
        cls.class_init()

        # add rule checker
        # note that this makes sure that decorator is applied to all classes that
        # do not have it ... while if you have used actual decorator then we will
        # remove this decorator and add true decorator as it might have new rules
        # to check
        RuleChecker()(checker=cls, rule_checker_set_from_init_subclass=True)

    @classmethod
    def class_init(cls):
        raise e.code.NotSupported(
            msgs=[f"Please override this class method in class {cls} ..."]
        )


@RuleChecker(
    things_to_be_cached=['internal'],
    things_not_to_be_cached=[
        'is_called', 'on_call', 'on_enter', 'on_exit', 'richy_panel',
    ],
    things_not_to_be_overridden=['is_called', 'richy_panel', ]
)
class Tracker(Checker):
    """
    Tracker that can track all classes in this system

    todo: for on_enter on_exit on_call we need to explore use of contextlib
      + https://docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
      + this library is builtin and hence justifies usage for same
      + it also has async context support so check it out
    """

    @property
    @util.CacheResult
    def internal(self) -> Internal:
        return Internal(self)

    @property
    def in_with_context(self) -> bool:
        return self.internal.in_with_context

    @property
    def is_called(self) -> bool:
        """
        Detects is hashable is called ... and hence can be used in with
        context or while iterating
        """
        return self.internal.is_called

    @property
    @util.CacheResult
    def dataclass_field_names(self) -> t.List[str]:
        # noinspection PyUnresolvedReferences
        return list(self.__dataclass_fields__.keys())

    @property
    def richy_panel(self) -> "richy.StatusPanel":
        """
        should be made available only when is_called and in_with_context
        """
        if self.is_called and self.in_with_context:
            return self.internal.richy_panel
        else:
            raise e.code.CodingError(
                msgs=[f"The self of type {self.__class__} is not in with context and is not called ...",
                      "So we do not have access to richy_panel ..."]
            )
            # from . import richy
            # return richy.StatusPanel(
            #     title=f"{self.__module__}.{self.__class__.__name__}",
            #     sub_title=self if isinstance(self, HashableClass) else None,
            #     tc_log=logger.get_logger(self.__module__)
            # )

    def __call__(self: T, richy_panel: "richy.StatusPanel") -> T:
        """
        We use __call__ with __enter__ and __exit__ as context manager ...

        todo: we can use contextlib library in future as it has support for
          async methods
          https://docs.python.domainunion.de/3/library/contextlib.html

        """

        # set call
        if self.is_called:
            raise e.code.CodingError(msgs=[
                f"This instance is already called ...",
                f"Did you miss to call your code from within with context "
                f"and forgot to exit properly in previous runs??",
                f"Or else try to call this with for statement ...",
            ])

        # set to indicate that this is called
        self.internal.is_called = True

        # richy panel should be in with context
        # note that we cannot enter exits with __enter__ and __exit__ here as we dont knwo when to exit
        # so the user must enter in with context of richy panel and pass it here
        if not richy_panel.is_in_with_context:
            raise e.code.CodingError(
                msgs=["Please make sure to pass richy panel from with context"]
            )

        # previous richy_panel should not exist
        if self.internal.richy_panel is not None:
            raise e.code.CodingError(
                msgs=["Previous richy_panel still exists ... did you miss to __exit__ properly"]
            )

        # set internal richy_panel
        self.internal.richy_panel = richy_panel

        # prefetch if not done
        # handle expensive things that can reduce load on consecutive calls
        # on same instance
        if not self.internal.has("prefetched_on_first_call"):
            self.prefetch_stuff_before_first_call()

        # do something once kwargs are available
        self.on_call()

        # return
        return self

    def __enter__(self: T) -> T:

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

    def __del__(self):
        self.on_del()

    @classmethod
    def class_init(cls):
        """
        Alternative to avoid using dunder method __init_subclass__

        Note that the class_init is called from __init_subclass__ and is not
        aware of dataclasses.dataclass related things. SO in order to have
        some HashableClass related class level thing swe need to do in in
        __post_init__ only once per class .... as by then the cls is aware
        that it is dataclass ;)
        """

        # hook up instance methods
        # Note this we can also do in init_class but better do it here so
        # that we need not wait till instance is created ...
        cls.hook_up_methods()

    @classmethod
    def hook_up_methods(cls):
        """
        todo: The hook up methods create clutter in class definition while
          browsing code in pycharm via structure pane
          Solution 1: Have a HookUp class
            We can easily have hook up class with three methods pre_runner,
              runner and post_runner. Then this class be added as class
              variable where we can use property pattern and get the owner
              of property. In __call__ we can then call three methods in
              sequence.
            But disadvantage is we will get some vars displayed as fields in
              pycharm structure. Remember we want fields to stand out. Also
              class validate needs to allow those vars (although this is
              solvable)
          Solution 2: Have a property which return HookUp class
            Disadvantage is we need to make sure that this property is
            cached.
            But we can have a class method to be used with class validate
            where we can store names of properties that need to be cached.

        todo: also allow pre runner to return hooked_method_return_value so
          that it can pe consumed in hooked up method. This I assume can only
          be possible via when we use one of the solution in above to do

        """
        ...

    def prefetch_stuff_before_first_call(self, call_only_once: bool = True):
        """
        Handle expensive things that can reduce load on consecutive calls
        on same instance.

        Prefetch in advance i.e. on first call to avoid pollution of logs
        This happens only once first time and things will be mostly cached
        You can also add any more code for performing prefetch
        Currently we do things like (mostly for foster data)
        + prefetch foster_data properties like shape dtype trace key ptx ...
        + cache memmaps in `foster_data.all_npy_mem_maps_cache`
        + call foster_data and open up

        WARNING: Never have prefetch stuff depend on kwargs passed during
        on_call

        """
        if self.internal.has("prefetched_on_first_call"):
            if call_only_once:
                raise e.code.CodingError(msgs=[
                    f"The method `prefetch_stuff` can be called only once ..."
                ])
        else:
            # set var
            self.internal.prefetched_on_first_call = True

    def on_call(self):
        """
        Override this in case you want to do something when __call__ is called
        """
        # ----------------------------------------------------- 01
        if not self.is_called:
            raise e.code.CodingError(msgs=[
                f"Internal variable on_call_kwargs is not yet set",
                f"Did you miss to call your code from within with context",
                f"Also did you miss to use __call__",
                f"If iterating over Hashable class make sure that "
                f"__call__ is called which sets kwargs related to "
                f"iteration or anything else",
            ])

    def on_enter(self):
        """
        Override this in case you want to do something when __enter__ is called
        """
        if not self.is_called:
            raise e.code.CodingError(msgs=[
                f"Internal variable on_call_kwargs is not yet set",
                f"Did you miss to call your code from within with context",
                f"Also did you miss to use __call__",
                f"If iterating over Hashable class make sure that "
                f"__call__ is called which sets kwargs related to "
                f"iteration or anything else",
            ])
        self.internal.in_with_context = True

    def on_exit(self, exc_type, exc_val, exc_tb):
        """
        Override this in case you want to do something when __exit__ is called
        """
        # reset
        self.internal.is_called = False
        self.internal.in_with_context = False
        self.internal.richy_panel = None

    def on_del(self):
        ...

    @classmethod
    def available_concrete_sub_classes(cls) -> t.List[t.Type["YamlRepr"]]:
        """
        Return a subset of AvailableHashableClasses that are subclass of
        incoming argument hashable_type.

        Can be used to track specific Hashables like Provider, Dataset,
        Model etc.
        """
        # declare
        global ALL_TRACKERS

        # container
        _ret = []

        # loop over all concrete hashable classes
        for h in ALL_TRACKERS:
            # if subclass and not abstract
            if issubclass(h, cls):
                if not inspect.isabstract(h):
                    # append to container
                    _ret.append(h)

        # return
        return _ret

    @classmethod
    def available_sub_classes(cls) -> t.List[t.Type["YamlRepr"]]:
        """
        Return a subset of AvailableHashableClasses that are subclass of
        incoming argument hashable_type.

        Can be used to track specific Hashables like Provider, Dataset,
        Model etc.
        """
        # declare
        global ALL_TRACKERS

        # container
        _ret = []

        # loop over all concrete hashable classes
        for h in ALL_TRACKERS:
            # if subclass
            if issubclass(h, cls):
                # append to container
                _ret.append(h)

        # return
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
    def load(cls, file_or_text: t.Union["storage.Path", str],
             **kwargs) -> t.Union[dict, "YamlRepr"]:
        from . import storage
        # get text
        _text = file_or_text
        if isinstance(file_or_text, storage.Path):
            _text = file_or_text.read_text()

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
            if isinstance(file_or_text, pathlib.Path):
                _msgs["file_or_text"] = file_or_text.as_posix()
            raise e.code.CodingError(msgs=[
                f"We expect yaml str is for correct class ",
                _msgs,
            ])

        # return
        return _instance


@RuleChecker(
    things_not_to_be_overridden=['yaml'],
)
class YamlRepr(Tracker):
    """
    This class makes it possible to have YamlRepr for dataclasses.

    NOTE: do nat make this class abstract as FrozenEnum like classes will not
    work

    todo: read about Yaml syntax here https://www.redhat.com/sysadmin/yaml-beginners

    todo: add support for https://rich.readthedocs.io/en/stable/protocol.html
      + __rich_console__
      + __rich__
      + __rich_measure__
    """

    @classmethod
    def class_init(cls):
        """ """
        global YAML_TAG_MAPPING

        # only do for concrete classes
        if not inspect.isabstract(cls):

            # register yaml tag for concrete classes
            yaml.add_representer(cls, cls._yaml_representer, Dumper=YamlDumper)
            # noinspection PyTypeChecker
            yaml.add_constructor(cls.yaml_tag(), cls._yaml_constructor)

            # save the map for tags and see if there is repetition
            _yaml_tag = cls.yaml_tag()

            if _yaml_tag not in YAML_TAG_MAPPING.keys():
                YAML_TAG_MAPPING[_yaml_tag] = cls
            else:
                if cls.__name__.startswith("__"):
                    # this is to handle special local classes that we do not
                    # intend to have any special tags
                    del YAML_TAG_MAPPING[_yaml_tag]
                    YAML_TAG_MAPPING[_yaml_tag] = cls
                else:
                    raise e.code.CodingError(msgs=[
                        f"The yaml tag `{_yaml_tag}` is already registered "
                        f"for class `{YAML_TAG_MAPPING[_yaml_tag]}`",
                        f"But you are again trying to use same tag for "
                        f"class `{cls}`.",
                        f"Please check if you have overridden `yaml_tag` "
                        f"method appropriately ... ",
                    ])

        # call super
        super().class_init()

    @classmethod
    def yaml_tag(cls) -> str:

        # this is to handle special local classes that we do not
        # intend to have any special tags
        # this will also grab <locals> keyword
        if cls.__name__.startswith("__"):
            return str(cls)

        # return
        return f"!{cls.__module__}:{cls.__name__}"

    @classmethod
    def _yaml_representer(cls, dumper: YamlDumper,
                          data: "YamlRepr") -> yaml.Node:
        # get yaml state dict
        _yaml_state = data.as_dict()

        # return representer
        return dumper.represent_mapping(cls.yaml_tag(), _yaml_state)

    @classmethod
    def _yaml_constructor(cls, loader: YamlLoader,
                          node: yaml.Node) -> "YamlRepr":
        """
        From the SO discussion here
        https://stackoverflow.com/questions/43812020/what-does-deep-true-do-in-pyyaml-loader-construct-mapping

        If you dump a data structure that has the same object/mapping/sequence
        attached at multiple positions you'll get anchors and aliases in your
        YAML and then you need deep=True to be able to load those. If you dump
        data that at some point has an object that "underneath" itself has a
        self reference, you will get anchors and aliases as well, but you'll
        need deep=True and the two-step process provided by yield to be able
        to load that YAML. So I always make constructors for non-scalars (the
        potential (self)-recursive ones) with yield and deep=True although not
        needed by some YAML docs.

        """
        state = loader.construct_mapping(node, deep=True)
        return cls.from_dict(state, **loader.extra_kwargs)

    # never override and never cache ... in some rare cases we update frozen
    # hashables ... so we need this yaml ... but note that hex_has is cached
    # and we need make it sure that any mutations are temporary
    # Note on (sort_keys=False):
    #     sort_keys=False makes sure that we can use insertion order feature
    #     provided by python 3.7+ ... also pyyaml is now supporting it
    def yaml(self) -> str:
        return YamlDumper.dump(self)

    @classmethod
    def from_yaml(cls, file_or_text: t.Union["storage.Path", str],
                  **kwargs) -> "YamlRepr":
        # return
        return YamlLoader.load(cls, file_or_text=file_or_text, **kwargs)

    @staticmethod
    def get_class(
        file_or_text: t.Union["storage.Path", str]
    ) -> t.Type["YamlRepr"]:
        from . import storage
        _text = file_or_text
        if isinstance(file_or_text, storage.Path):
            _text = file_or_text.read_text()
        _tag = _text.split("\n")[0]
        try:
            return YAML_TAG_MAPPING[_tag]
        except KeyError:
            raise e.code.CodingError(
                msgs=[
                    "Cannot detect hashable class from provided `file_or_text` ...",
                    "Cannot process tag at the start ... check:", _text,
                ]
            )

    def clone(self) -> "YamlRepr":
        return self.from_yaml(self.yaml())

    def as_dict(self) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        raise e.code.CodingError(msgs=[
            f"We expect you to override `as_dict()` method in class "
            f"{self.__class__}"
        ])

    @classmethod
    def from_dict(
        cls, yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"], **kwargs
    ) -> "YamlRepr":
        # noinspection PyArgumentList
        return cls(**yaml_state)

    @classmethod
    def can_be_frozen(
        cls,
        item: t.Union[dict, list],
        key_or_index: str,
        allowed_types: t.Tuple[t.Type],
    ):

        # ------------------------------------------------------------ 01
        # compile err message using key_or_index argument
        _err_msg = [f"Check `{key_or_index}`"]

        # ------------------------------------------------------------ 02
        # check if item is dict or list
        if isinstance(item, dict):
            if item.__class__ != dict:
                raise e.validation.NotAllowed(msgs=[
                    f"Looks like you are using a dict that is not builtin "
                    f"python dict.",
                    f"Found dict of type {type(item)}!={dict}",
                ] + _err_msg)
        elif isinstance(item, list):
            if item.__class__ != list:
                raise e.validation.NotAllowed(msgs=[
                    f"Looks like you are using a list that is not builtin "
                    f"python list.",
                    f"Found list of type {type(item)}!={list}",
                ] + _err_msg)
        else:
            raise e.validation.NotAllowed(msgs=[
                f"We expect item to be a dict or list but instead found "
                f"item of type {type(item)}"
            ] + _err_msg)

        # ------------------------------------------------------------ 04
        # if dict check keys and values
        if isinstance(item, dict):
            # -------------------------------------------------------- 04.01
            # loop over items
            for k, v in item.items():
                # ---------------------------------------------------- 04.02
                # compute current key
                current_key = f">{k}" if key_or_index is None else f"{key_or_index}>{k}"
                # ---------------------------------------------------- 04.03
                # dict key needs to be str or int
                if not isinstance(k, (str, int)):
                    raise e.validation.NotAllowed(msgs=[
                        f"We expect the dict to be frozen to have str or "
                        f"int keys",
                        f"Found key `{k}` of type {type(k)}.",
                    ] + _err_msg)
                # ---------------------------------------------------- 04.04
                # if nested dict or list try to verify keys and values
                if isinstance(v, (dict, list)):
                    # check the value
                    cls.can_be_frozen(v, current_key, allowed_types)
                # ---------------------------------------------------- 04.05
                # else value needs to be one of supported hashable
                else:
                    e.validation.ShouldBeInstanceOf(
                        value=v,
                        value_types=allowed_types,
                        msgs=[f"Value for key `{k}` in dict cannot be frozen"]
                        + _err_msg,
                    ).raise_if_failed()

        # ------------------------------------------------------------ 05
        # if list check values
        elif isinstance(item, list):
            # -------------------------------------------------------- 05.01
            # loop over items
            for i, v in enumerate(item):
                # ---------------------------------------------------- 05.02
                # compute current key
                current_key = f">{i}" if key_or_index is None else f"{key_or_index}>{i}"
                # ---------------------------------------------------- 05.03
                # value needs to be hashable
                e.validation.ShouldBeInstanceOf(
                    value=v,
                    value_types=allowed_types + (dict, list),
                    msgs=[f"Value for index `{i}` in list cannot be frozen"] +
                    _err_msg,
                ).raise_if_failed()
                # ---------------------------------------------------- 05.04
                # if nested dict or list try to verify keys and values
                if isinstance(v, (dict, list)):
                    cls.can_be_frozen(
                        item=v,
                        key_or_index=current_key,
                        allowed_types=allowed_types,
                    )

        # ------------------------------------------------------------ 06
        # else not possible
        else:
            raise e.code.ShouldNeverHappen(msgs=[])


#
# class _FrozenDict:
#     @property
#     def allowed_types(self) -> t.Tuple[t.Type]:
#         return SUPPORTED_HASHABLE_OBJECTS
#
#     @property
#     def allowed_nesting(self) -> bool:
#         return True
#
#     def __init__(
#         self,
#         item: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
#     ):
#         self._item = {}
#         self.update_internal_dict(item=item)
#
#     def update_internal_dict(
#         self,
#         item: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
#     ):
#         item = item.copy()
#         # ------------------------------------------------------------ 01
#         # validation
#         self.can_be_frozen(
#             item=item,
#             key_or_index=f"{self.yaml_tag()}::",
#             allowed_types=self.allowed_types,
#             allowed_nesting=self.allowed_nesting,
#         )
#         # ------------------------------------------------------------ 02
#         # save reference
#         self._item.update(item)
#
#     @classmethod
#     def yaml_tag(cls) -> str:
#         return f"!frozen_dict"
#
#     def get(self) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
#         _ret = {}
#         for k, v in self._item.items():
#             if isinstance(v, YamlRepr):
#                 v = v.as_dict()
#             _ret[k] = v
#         return _ret
#
#     def as_dict(
#         self
#     ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
#         return self.get()
#
#     @classmethod
#     def from_dict(
#         cls,
#         yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
#         **kwargs
#     ) -> "FrozenDict":
#         return cls(item=yaml_state)

#
# class FrozenKeras(YamlRepr):
#
#     class LITERAL(YamlRepr.LITERAL):
#         SUPPORTED_KERAS_OBJECTS_TYPE = t.Union[
#             tk.losses.Loss,
#             tk.optimizers.Optimizer,
#             tk.optimizers.schedules.LearningRateSchedule,
#         ]
#         # noinspection PyUnresolvedReferences
#         SUPPORTED_KERAS_OBJECTS = SUPPORTED_KERAS_OBJECTS_TYPE.__args__
#
#     def __init__(self, item: LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE):
#         # -------------------------------------------------------- 01
#         # validate
#         # -------------------------------------------------------- 01.01
#         # check item type
#         e.validation.ShouldBeInstanceOf(
#             value=item,
#             value_types=self.LITERAL.SUPPORTED_KERAS_OBJECTS,
#             msgs=[
#                 f"Unrecognized item type that cannot be freezed ..."
#             ]
#         ).raise_if_failed()
#         # -------------------------------------------------------- 01.02
#         # check if keras config is serializable as per our code
#         _k_config = item.get_config()
#         self.can_be_frozen(
#             _k_config,
#             key_or_index=f"{self.yaml_tag()}::",
#             allowed_types=SUPPORTED_HASHABLE_OBJECTS,
#         )
#
#         # -------------------------------------------------------- 02
#         # save keras related information
#         self._k_class = item.__class__
#         self._k_config = _k_config
#         # delete item so that the graph do not have any information
#         del item
#
#     @classmethod
#     def yaml_tag(cls) -> str:
#         return f"!frozen_keras"
#
#     def get(self) -> LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE:
#         # this basically picks up class of keras instance `self._item` and
#         # creates instance from config given by `self._item`
#         return self._k_class.from_config(self._k_config)
#
#     def as_dict(
#         self
#     ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
#         return {
#             "module": self._k_class.__module__,
#             "class": self._k_class.__name__,
#             "config": self._k_config.copy()
#         }
#
#     @classmethod
#     def from_dict(
#         cls,
#         yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
#         **kwargs
#     ) -> "FrozenKeras":
#         _k_class = util.load_class_from_strs(
#             class_name=yaml_state["class"],
#             class_module=yaml_state["module"],
#         )  # type: t.Type[cls.LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE]
#         return cls(item=_k_class.from_config(yaml_state["config"]))

# todo: Have a FrozenEnum and FrozenSlice which is built on top of python
#  builtins ... and does not need to be a subclass as in FrozenEnum below

# todo: also want to implement this ...
# class FrozenSlice(YamlRepr):
#     ...

# todo: is it possible to override yaml behaviour for builtins like Enum and
#  slice .... TO BE EXPLORED ...
#  currently this looks ugly with the tag like
#    !!python/object/apply:builtins.slice


class FrozenEnum(YamlRepr):
    """
    todo: we need to replace with something that can override yaml behaviour
      for builtins
    """

    def as_dict(self) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        # noinspection PyUnresolvedReferences
        return {"name": self.name}

    @classmethod
    def from_dict(cls, yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
                  **kwargs) -> "FrozenEnum":
        return getattr(cls, yaml_state["name"])


# @dataclasses.dataclass(eq=True, frozen=True)
@dataclasses.dataclass(frozen=True)
@RuleChecker(
    things_to_be_cached=['hex_hash', 'rich_panel'],
    things_not_to_be_overridden=['hex_hash'],
    # todo: any method or property that returns storage.FileSystem,
    #  Table FileGroup, Folder must be cached
    #  Will need to look at each property and methods return type and based on that
    #  augment list things_to_be_cached
)
class HashableClass(YamlRepr, abc.ABC):
    """
    todo: add rich rendering
      https://rich.readthedocs.io/en/stable/protocol.html#
      Figure out usage for:
      __rich__
      __rich_console__
      __rich_measure__

    todo: we will make this frozen ... after that we can use __hash__ i.e.
      generated by dataclasses ... and hence get rid of `hex_hash`
      also __eq__ will be autogenerated

    todo: even if things are frozen we still have mutable values used by our
      hashable classes like dict and keras objects .... how to use only
      immutable objects is the task for future
      e.g.
       + frozenset for dicts and
       + keras objects get_config .... get dict and then make it immutable

    todo: We can have a class method to be used with class validate where we
      can store names of properties that need to be cached.
    """
    @property
    def name(self) -> str:
        """
        A convenient short name that can be used with class name to identify
        hashable class with some simple name that can be used to name the
        file or folder.

        By default we use hex_hash but you can also make a readable string
        from field values if possible so that there is unique for all
        possible instances (Example check PreparedData names. Note that
        `hex_hash` will anyways be unique for a instance.
        """
        return self.hex_hash

    @property
    def group_by(self) -> t.List[str]:
        """
        As self.name is hex_hash or else a name which is unique to all
        instances of that class we need some convenient name that can be used
        for grouping.

        This property can return str or list of str. In case of list of str
        nested folders will be created.

        This is a meta property to allow grouping over unique
        HashableClass names.

        Example use cases:
          + grouping plots
          + group files under one Folder while storage

        If None is returned then grouping is not used

        """
        # default is not to use grouping
        return []

    @property
    @util.CacheResult
    def rich_panel(self) -> rich.console.Group:
        """
        Basically we want small flash cards which can have different multiple
        `progress.Progress` with their own spinners. Plus we want link that can open up
        new window on console and display dataclass info.

        We can have basically a UI inside console per HashableClass with
        interactions ...
        todo: may be we can explore adding console rendered for toolcraft.gui
          too complex for now and out of scope

        todo: Build customized Progress with console.Group specific to HashableClass...
          Note that rich is more powerful you can have mini panel cards and show
            spinners and progress bars inside it ...
          Note that if class can be iterated it will use `Tracker.rich_progress`
            property ...
          We can show things like
          + status for multiple phases (rich.status.Status)
             + init, validate, create, some storage properties if any
          + progress bar for some phases
          + hashable_info (a link which will open a panel ans show hashable info)

        todo: read
          + customizing progress bar
            https://rich.readthedocs.io/en/stable/progress.html?highlight=spinner#customizing
          + multiple Progress
            https://rich.readthedocs.io/en/stable/progress.html?highlight=spinner#multiple-progress
          + Render groups
            https://rich.readthedocs.io/en/stable/group.html
          + Explore more
        """
        return rich.console.Group()

    @property
    def mini_hex_hash(self) -> str:
        _hex_hash = self.hex_hash
        _hex_hash = _hex_hash[len(_hex_hash)-12:]
        return _hex_hash

    @property
    @util.CacheResult
    def hex_hash(self) -> str:
        """
        We will use GUID popular in csharp instead of hex hash
        + every hashable class and its method will have a GUID to track it down
          anywhere in distributed platform
        + https://www.c-sharpcorner.com/article/what-is-guid-in-c-sharp/

        NOTE: Never override this property ... In case you need to override
        it always rely on name property which we intend to be unique across
        instances

        todo: Finally use DNS to achieve encryption of hashes and bookkeeping
          of files with user credentials
          https://github.com/rthalley/dnspython (pro feature)

        Note we cache this as the underlying yaml repr will not change ....
        expect for Config class but nonetheless we fo not allow hex_hash on
        Config instances .... hex_hash is only meaningful for hashable
        classes that never change

        """
        # todo .... should we use __hash__ method which must return int ???
        # todo: make the dataclass frozen=True and eq=True
        #   so that dataclass based hash can be generated
        # todo: find dataclass based alternative (explore dataclass generated
        #  __repr__ and __hash__ dunder methods)
        # return
        return hashlib.md5(f"{self.yaml()}".encode("utf-8")).hexdigest()

    # noinspection PyPropertyDefinition,PyTypeChecker
    # @property
    # @util.CacheResult
    # def stores(self) -> t.Dict[str, "storage.dec.StoreFolder"]:
    #     raise e.code.NotAllowed(msgs=[
    #         f"Please override `stores` property if you want to "
    #         f"save results @storage.dec.XYZ decorators for hashable class "
    #         f"{self.__class__}"
    #     ])

    # todo: this was for yaml repr .... but not needed ... so may be we
    #  still need to explore the default __repr__ for dataclass ...
    #  meanwhile __str__ suffice to generate unique text to save on disk ...
    # def __repr__(self) -> str:
    #     return util.dataclass_to_yaml_repr(self)

    def __post_init__(self):
        # ---------------------------------------------------------- 01
        # this is a very wierd way of doing rule check as we cannot detect when the
        # class subclassing is over
        # What we do here is when first time instance is created we check for classes
        # that are already loaded and per form rule check and delete them ...
        # as because in that case class is fully loaded and dataclass decorator
        # is also applied
        # [NOTE] MAKE SURE THAT THIS CODE IS NEVER CALLED FROM CLASS LEVEL METHODS
        # Also we are aware that this can be done some parent class instance method
        # but as of now we cannot have __init__ method there as many classes that are
        # subclassed are dataclasses
        # Note that this happens only once as we always keep on cleaning the dict
        # todo: note that rule check will not trigger when instance of YamlRepr are created ...
        #    only when first instance of HashableClass is created will the rule check happen ...
        #    We can move this logic to Tracker.__init__ but that also will not solve problem as any subclass of it
        #    when converted to dataclass cannot clall __init__ you need to override __post_init__ to call
        #    Tracker.__init__ ...
        #    Temporary workaround is to create fake HashableClass instance once all modules are loaded in your library
        if settings.DO_RULE_CHECK:
            from . import richy
            _rc_keys = list(_RULE_CHECKERS_TO_BE_CHECKED.keys())
            # _modules = [_.decorated_class for _ in _RULE_CHECKERS_TO_BE_CHECKED.values()]
            if bool(_rc_keys):
                for _rc_k in richy.Progress.simple_track(
                    _rc_keys,
                    description=f"Rule Check ({len(_rc_keys)} classes) ...",
                    title="Rule Check", tc_log=_LOGGER, console=None,
                ):
                    _RULE_CHECKERS_TO_BE_CHECKED[_rc_k].check()
                    del _RULE_CHECKERS_TO_BE_CHECKED[_rc_k]

        # ---------------------------------------------------------- 02
        # dict field if any will be transformed
        for f in self.dataclass_field_names:
            _dict = getattr(self, f)
            if isinstance(_dict, dict):
                # make changes to hyper_fields ...
                # it is possible as dict is mutable
                _copy_dict = {}
                # makes sures that the items are sorted
                _sorted_keys = list(_dict.keys())
                _sorted_keys.sort()
                for k in _sorted_keys:
                    v = _dict[k]
                    _copy_dict[k] = v
                _dict.clear()
                _dict.update(_copy_dict)
        # ---------------------------------------------------------- 03
        # todo: add global flag to start and stop validation
        # make sure that everything is light weight so that object creation
        # is fast ...
        self.init_validate()
        # ---------------------------------------------------------- 04
        # call init logic
        self.init()

    def __str__(self) -> str:
        """
        We can have self.name to be returned here but will check later.

        Earlier we used to return yaml representation but now we have method
        `self.yaml()` to do the same.

        We will henceforth raise error here.
        """
        # In debug method this will return something meaningful as debugger
        # keeps accessing this method to get str representation of any object
        if settings.PYC_DEBUGGING:
            return f"... debugging ... {self.name}"

        # if interactive mode then allow use of __str__
        if settings.INTERACTIVE:
            return f"... interactive ... {self.name}"

        # when not in debug method we do not allow to print this object
        # instead `self.yaml()` should be used
        raise e.code.CodingError(msgs=[
            f"We do not allow to use __str__ or __repr__ of the "
            f"marshalling class.",
            f"Instead use `.yaml()` method.",
        ])

    # todo: avoid these dunder methods as dataclass adds its own __eq__ and then you need to
    #   add eq=False in all child class dataclass decorators
    #   https://stackoverflow.com/questions/61430552/dataclass-not-inheriting-eq-method-from-its-parent
    # todo: explore dunder method override options of dataclass.dataclass constructor and how it plays
    #   with frozen and other option's
    # def __ne__(self, other):
    #     print(self.hex_hash, other.hex_hash, "ne ...........................")
    #     return not self.__eq__(other)
    # def __eq__(self, other):
    #     # Note this helps to ignore `init=True` fields in equality check
    #     print(self.hex_hash, other.hex_hash, "eq ...........................")
    #     return self.hex_hash == other.hex_hash

    def as_dict(self) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        _field_names = self.dataclass_field_names
        if settings.TF_KERAS_WORKS:
            # Handle serialization for keras loss, optimizer and layer
            from keras.api._v2 import keras as tk
            for f_name in _field_names:
                _v = getattr(self, f_name)
                if isinstance(_v, tk.losses.Loss):
                    _v = tk.losses.serialize(_v)
                    _v['__keras_instance__'] = "loss"
                if isinstance(_v, tk.layers.Layer):
                    _v = tk.layers.serialize(_v)
                    _v['__keras_instance__'] = "layer"
                if isinstance(_v, tk.optimizers.Optimizer):
                    _v = tk.optimizers.serialize(_v)
                    _v['__keras_instance__'] = "optimizer"
                # this need not be handled as it is automatically handled by optimizer
                # if isinstance(_v, tk.optimizers.schedules.LearningRateSchedule):
                #     _v = tk.optimizers.schedules.serialize(_v)
                #     _v['__keras_instance__'] = "learning_rate_schedule"
                _ret[f_name] = _v
        else:
            for f_name in _field_names:
                _ret[f_name] = getattr(self, f_name)

        return _ret

    @classmethod
    def from_dict(
        cls, yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"], **kwargs
    ) -> "HashableClass":
        if settings.TF_KERAS_WORKS:
            # Handle deserialization for keras loss, optimizer and layer
            # noinspection PyUnresolvedReferences,PyProtectedMember
            from keras.api._v2 import keras as tk
            for _n in yaml_state.keys():
                _v = yaml_state[_n]
                if isinstance(_v, dict) and '__keras_instance__' in _v.keys():
                    _keras_instance_type = _v['__keras_instance__']
                    del _v['__keras_instance__']
                    if _keras_instance_type == "loss":
                        yaml_state[_n] = tk.losses.deserialize(_v, custom_objects=CUSTOM_KERAS_CLASSES_MAP['loss'])
                    elif _keras_instance_type == "layer":
                        yaml_state[_n] = tk.layers.deserialize(_v)
                    elif _keras_instance_type == "optimizer":
                        yaml_state[_n] = tk.optimizers.deserialize(_v)
                    else:
                        raise e.code.CodingError(
                            msgs=[
                                f"Unknown keras instance type {_keras_instance_type!r}"
                            ]
                        )
        # noinspection PyTypeChecker
        return super().from_dict(yaml_state=yaml_state, **kwargs)

    def init_validate(self):
        """
        Simple dataclass field validation .... make sure that no attributes or
        memory is consumed while doing this
        """
        global SUPPORTED_HASHABLE_OBJECTS

        # --------------------------------------------------------------01
        # loop over serialized version of field values to validate them
        for f_name, v in self.as_dict().items():
            # ----------------------------------------------------------01.01
            # raise error to inform to use FrozenDict
            if isinstance(v, dict):
                self.can_be_frozen(
                    item=v,
                    key_or_index=f"{f_name}::",
                    allowed_types=SUPPORTED_HASHABLE_OBJECTS,
                )
            # ----------------------------------------------------------01.02
            # if list check if values inside are hashable
            elif isinstance(v, list):
                self.can_be_frozen(
                    item=v,
                    key_or_index=f"{f_name}::",
                    allowed_types=SUPPORTED_HASHABLE_OBJECTS,
                )
            # ----------------------------------------------------------01.03
            # else should be one of supported type
            else:
                e.validation.ShouldBeInstanceOf(
                    value=v,
                    value_types=SUPPORTED_HASHABLE_OBJECTS,
                    msgs=[
                        f"Check value of field `{f_name}` for class "
                        f"{self.__class__}"
                    ],
                ).raise_if_failed()

    def init(self):
        ...

    @UseMethodInForm(label_fmt="Info")
    def info_widget(self) -> "gui.widget.Text":
        # import
        from . import gui
        # make
        # noinspection PyUnresolvedReferences
        _ret_widget = gui.widget.Text(
            default_value=f"Hex Hash: {self.hex_hash}\n\n{self.yaml()}"
        )
        # return
        return _ret_widget

    def check_for_storage_hashable(self, field_key: str = ""):
        """
        raises error if instance of StorageHashable or any of its fields is
        instance of StorageHashable.

        This will avoid any accidental file/folder creations and IO tracking
        """
        from . import storage
        e.validation.ShouldNotBeInstanceOf(
            value=self, value_types=(storage.StorageHashable, ),
            msgs=[
                f"Do not use {storage.StorageHashable} for field_key `{field_key}`",
                f"This check indicates that the hashable class is not supposed for storage on network/disk "
                f"and we want to use it as pure HashableClass ...",
                f"This will avoid any accidental file/folder creations and IO tracking ..."
            ]
        ).raise_if_failed()
        for _f in self.dataclass_field_names:
            _v = getattr(self, _f)
            if isinstance(_v, HashableClass):
                _v.check_for_storage_hashable(field_key=f"{field_key}.{_f}")


if settings.TF_KERAS_WORKS:
    # noinspection PyUnresolvedReferences,PyProtectedMember
    from keras.api._v2 import keras as tk
    from keras.optimizers.optimizer_experimental import \
        optimizer as optimizer_experimental
    SUPPORTED_HASHABLE_OBJECTS_TYPE = t.Union[
        int, float, str, slice, list, dict,
        np.float32, np.int64, np.int32,
        datetime.datetime, None, FrozenEnum,
        HashableClass, pa.Schema,
        tk.losses.Loss, tk.layers.Layer,
        tk.optimizers.Optimizer, optimizer_experimental.Optimizer,
    ]
else:
    SUPPORTED_HASHABLE_OBJECTS_TYPE = t.Union[int, float, str, slice, list, dict,
                                              np.float32, np.int64, np.int32,
                                              datetime.datetime, None, FrozenEnum,
                                              HashableClass, pa.Schema, ]
# noinspection PyUnresolvedReferences
SUPPORTED_HASHABLE_OBJECTS = SUPPORTED_HASHABLE_OBJECTS_TYPE.__args__
