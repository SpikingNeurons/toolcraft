"""
todo: Plan to set rules here as to how that HashableClass needs to be
  overridden by users .... also do some one time validations here ....
  should be done once entire library is loaded

This will solve many piled up todos in code and reduce overhead

Class validation mostly checks CodingErrors:
  + We might want to move class_validate and class_init code here and execute it
    rarely to check some rules that we will set here.
  + Also note that some class_validation is placed in init_validate as
    dataclass is not yet baked and annotated fields are not seen as
    `dataclass.Field` by class validate. We aim to move that code here too.

todo: add a decorator to dataclass where we can configure class about the
  things that are to be checked for coding errors. Example:
  + if properties/methods are cached
  + if method/property should never be overridden
  + if class should not be sublasses
  + if subclass should not have extra fields
  + etc.
  You can then get this decorator inside init_subclass and run code
  validations in one place ;)
  Challenge is how decorator from subclasses will override decorator on
  parent class.

todo: All LITERAL nested classes and Config class should subclass immediate
  parents nested class
"""
import enum
import types
import dataclasses
import typing as t

from toolcraft import error as e
from toolcraft import util

from .marshalling import YamlRepr, HashableClass, FrozenEnum, Tracker
from .storage import Folder, StorageHashable, FileGroup, NpyFileGroup, \
    ResultsFolder
from .storage.state import Config, Info, StateFile


LITERAL_CLASS_NAME = "LITERAL"


def check_classes_that_should_not_be_overridden():
    _CLASSES_THAT_SHOULD_NOT_BE_OVERRIDDEN = [
        Info
    ]
    for cls in _CLASSES_THAT_SHOULD_NOT_BE_OVERRIDDEN:
        _sub_classes = cls.available_sub_classes()
        if len(_sub_classes) > 1:
            e.code.CodingError(
                msgs=[
                    f"You are not allowed to subclass class {cls}",
                    f"Please check classes: ",
                    _sub_classes[1:]
                ]
            )


def check_things_to_be_cached(
    to_check: dict = None
):
    _THINGS_TO_BE_CACHED = {
        Tracker: ['internal', ],
        HashableClass: [
            'hex_hash', 'results_folder',
        ],
        StorageHashable: [
            'config', 'info', 'path', 'root_dir',
        ],
        Folder: ['items'],
        FileGroup: ['file_keys'],
        ResultsFolder: ['store'],
    }
    if to_check is not None:
        _THINGS_TO_BE_CACHED = to_check
    for sup_cls, things in _THINGS_TO_BE_CACHED.items():
        for cls in sup_cls.available_sub_classes():
            for _t in things:
                # get
                _method_or_prop = getattr(cls, _t)
                # if abstract no sense in checking if cached
                if getattr(_method_or_prop, '__isabstractmethod__', False):
                    continue
                # check if cached
                if not util.is_cached(_method_or_prop):
                    e.code.CodingError(
                        msgs=[
                            f"We expect you to cache property/method `{_t}` "
                            f"using decorator `@util.CacheResult` in "
                            f"class {cls}"
                        ]
                    )


def check_things_not_to_be_cached(
    to_check: dict = None
):
    _THINGS_NOT_TO_BE_CACHED = {
        Tracker: ['is_called', 'iterable_length', 'on_iter', 'on_call',
                  'on_enter', 'on_exit'],
        StateFile: ['is_available'],
    }
    if to_check is not None:
        _THINGS_NOT_TO_BE_CACHED = to_check
    for sup_cls, things in _THINGS_NOT_TO_BE_CACHED.items():
        for cls in sup_cls.available_sub_classes():
            for _t in things:
                # get
                _method_or_prop = getattr(cls, _t)
                # if abstract no sense in checking if cached
                if getattr(_method_or_prop, '__isabstractmethod__', False):
                    continue
                # check if cached
                if util.is_cached(_method_or_prop):
                    e.code.CodingError(
                        msgs=[
                            f"We expect you not to cache property/method "
                            f"`{_t}`. Do not use  decorator "
                            f"`@util.CacheResult` in "
                            f"class {cls} for `{_t}`"
                        ]
                    )


def check_things_not_to_be_overridden(
    to_check: dict = None
):
    _THINGS_NOT_TO_BE_OVERRIDDEN = {
        YamlRepr: ['yaml'],
        HashableClass: ['hex_hash'],
        Folder: ['group_by'],
        NpyFileGroup: ['get_files', ],
        Tracker: ['is_called', 'is_iterable'],
        StorageHashable: ['path'],
        ResultsFolder: ['store'],
    }
    if to_check is not None:
        _THINGS_NOT_TO_BE_OVERRIDDEN = to_check
    for sup_cls, things in _THINGS_NOT_TO_BE_OVERRIDDEN.items():
        for cls in sup_cls.available_sub_classes():
            for _t in things:
                if getattr(cls, _t) != getattr(sup_cls, _t):
                    e.code.CodingError(
                        msgs=[
                            f"Please do not override method/property "
                            f"`{_t}` in class {cls}"
                        ]
                    )


def check_things_to_be_dataclasses():
    _THINGS_TO_BE_DATACLASSES = [
        HashableClass, StateFile
    ]
    for sup_cls in _THINGS_TO_BE_DATACLASSES:
        for cls in sup_cls.available_sub_classes():
            # we expected all subclasses to be decorated with
            # dataclass ...
            _cls_dict_keys = cls.__dict__.keys()
            # noinspection PyProtectedMember
            if not (
                dataclasses._FIELDS in _cls_dict_keys or
                dataclasses._PARAMS in _cls_dict_keys
            ):
                e.code.NotAllowed(
                    msgs=[
                        f"You missed to decorate subclass {cls} of {sup_cls} "
                        f"with `@dataclasses.dataclass` decorator"
                    ]
                )


# noinspection PyPep8Naming
def check_everyone_has_logger():
    """
    todo: Later
    """
    # ------------------------------------------------------01
    # make sure that each module has _LOGGER


# noinspection PyPep8Naming
def check_YamlRepr():
    _yaml_tag_check = {}

    cls: t.Type[YamlRepr]
    for cls in YamlRepr.available_sub_classes():

        # ------------------------------------------------------01
        # make sure LITERAL class is extended properly from the immediate
        # parent which has LITERAL class or else go for super
        # parent i.e. `YamlRepr.LITERAL`
        try:
            # noinspection PyUnresolvedReferences
            _parent_literal_class = cls.__mro__[1].LITERAL
        except AttributeError:
            _parent_literal_class = YamlRepr.LITERAL
        e.validation.ShouldBeSubclassOf(
            value=cls.LITERAL, value_types=(_parent_literal_class, ),
            msgs=[
                f"We expect a nested class of class {cls} with name "
                f"{LITERAL_CLASS_NAME!r} to "
                f"extend the class {_parent_literal_class}"
            ]
        )

        # ------------------------------------------------------02
        # check if all yaml tags are unique
        _yaml_tag = cls.yaml_tag()
        if _yaml_tag not in _yaml_tag_check.keys():
            _yaml_tag_check[_yaml_tag] = cls
        else:
            e.code.CodingError(
                msgs=[
                    f"The same yaml tag `{_yaml_tag}` seems to appear in both "
                    f"classes: ",
                    [
                        cls, _yaml_tag_check[_yaml_tag]
                    ]
                ]
            )


# noinspection PyPep8Naming
def check_HashableClass():
    # some useful vars
    _general_dunders_to_ignore = [
        # python adds it
        '__module__', '__dict__', '__weakref__', '__doc__',

        # dataclass related
        '__annotations__', '__abstractmethods__', '__dataclass_params__',
        '__dataclass_fields__',

        # dataclass adds this default dunders to all dataclasses ... we have
        # no control over this ;(
        '__init__', '__repr__', '__eq__', '__setattr__',
        '__delattr__', '__hash__',

        # we allow this
        '__call__',
    ]

    cls: t.Type[HashableClass]
    for cls in HashableClass.available_sub_classes():

        # ---------------------------------------------------------- 01
        # class should not be local
        if str(cls).find("<locals>") > -1:
            e.validation.NotAllowed(
                msgs=[
                    f"Hashable classes can only be first class classes.",
                    f"Do not define classes locally, declare them at module "
                    f"level.",
                    f"Check class {cls}"
                ]
            )

        # ---------------------------------------------------------- 02
        # check all non dunder attributes
        for _attr_k, _attr_v in util.fetch_non_dunder_attributes(cls):

            # ------------------------------------------------------ 02.01
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

            # ------------------------------------------------------ 02.02
            # no attribute should start with _
            if _attr_k.startswith('_'):
                # if abstract class used this will be present
                # the only field that starts with _ which we allow
                if _attr_k == '_abc_impl':
                    continue
                # anything else raise error
                e.validation.NotAllowed(
                    msgs=[
                        f"Attribute {_attr_k} is not one of {_allowed_types} "
                        f"and it starts with `_`",
                        f"Please check attribute {_attr_k} of class {cls}"
                    ]
                )

            # ------------------------------------------------------ 02.03
            # if special helper classes that stores all LITERALS
            if _attr_k == LITERAL_CLASS_NAME:
                # NOTE: we already check if class LITERAL is correctly
                # subclassed in super method .... so no need to do here
                continue

            # ------------------------------------------------------ 02.04
            # check if _attr_k is in __annotations__ then it is dataclass field
            # Note: dataclasses.fields will not work here as the class still
            #   does not know that it is dataclass
            # todo: this is still not a complete solution as annotations will
            #  also have fields that are t.ClassVar and t.InitVar
            #  ... we will see this later how to deal with ... currently
            #  there is no easy way
            if _attr_k in cls.__annotations__.keys():
                # _ann_value is a typing.ClassVar raise error
                # simple way to see if typing was used as annotation value
                if hasattr(_attr_v, '__origin__'):
                    if _attr_v.__origin__ == t.ClassVar:
                        e.code.CodingError(
                            msgs=[
                                f"We do not allow class variable {_attr_k} "
                                f"... check class {cls}"
                            ]
                        )
                # if `dataclasses.InitVar` raise error
                if isinstance(_attr_v, dataclasses.InitVar):
                    e.code.CodingError(
                        msgs=[
                            f"We co not allow using dataclass.InitVar.",
                            f"Please check annotated field {_attr_k} in "
                            f"class {cls}"
                        ]
                    )
                # if a vail dataclass field continue
                continue

            # ------------------------------------------------------ 02.05
            # if we reached here we do not understand the class attribute so
            # raise error
            e.code.NotAllowed(
                msgs=[
                    f"Found an attribute `{_attr_k}` with: ",
                    dict(
                        type=f"{type(_attr_v)}",
                        value=f"{_attr_v}",
                    ),
                    f"Problem with attribute {_attr_k} of class {cls}",
                    f"It is neither one of {_allowed_types}, nor is it "
                    f"defined as dataclass field.",
                    f"Note that if you are directly assigning the annotated "
                    f"field it will not return dataclass field so please "
                    f"assign it with "
                    f"`dataclass.field(default=...)` or "
                    f"`dataclass.field(default_factory=...)`",
                ]
            )

        # ---------------------------------------------------------- 03
        # do not override dunder methods
        if cls != HashableClass:
            for k in cls.__dict__.keys():
                if k.startswith("__") and k.endswith("__"):
                    if k not in _general_dunders_to_ignore:
                        e.code.CodingError(
                            msgs=[
                                f"You are not allowed to override dunder "
                                f"methods in any subclass of {HashableClass}",
                                f"Please check class {cls} and avoid defining "
                                f"dunder method `{k}` inside it"
                            ]
                        )

        # ---------------------------------------------------------- 04
        # if block_fields_in_subclasses then check there are no new fields in
        # subclass
        # todo: we know that this cause recursion but we will fix it only if
        #  things are slow ... but for now ignore
        if cls.block_fields_in_subclasses():
            # fields that are allowed
            cls_fields = [
                f.name for f in dataclasses.fields(cls)
            ]
            # sort
            cls_fields.sort()
            # now get all available subclasses of cls
            sub_cls: HashableClass
            for sub_cls in cls.available_sub_classes():
                # ignore if cls
                if sub_cls == cls:
                    continue
                # get fields in subclass
                sub_cls_fields = [
                    f.name for f in dataclasses.fields(sub_cls)
                ]
                # sort
                sub_cls_fields.sort()
                # compare
                if cls_fields != sub_cls_fields:
                    e.code.CodingError(
                        msgs=[
                            f"You are not allowed to add any new fields in "
                            f"dataclass {sub_cls} as it is restricted by class "
                            f"{cls}",
                            {
                                "fields restricted to": cls_fields,
                                "found": sub_cls_fields
                            }
                        ]
                    )

        # ---------------------------------------------------------- xx
        # todo: find a way to check if super() calls are made

        # ---------------------------------------------------------- xx
        # todo: find a way to check if util.CacheResult decorator is added
        #  wherever necessary ... this will reduce work of init_validate

        # ---------------------------------------------------------- xx
        # todo: check things that needs to be overridden

        # ---------------------------------------------------------- xx
        # todo: check things that need not to be overridden


# noinspection PyPep8Naming
def check_Config():

    cls: t.Type[Config]
    for cls in Config.available_sub_classes():
        # ---------------------------------------------------------- 01
        # all fields that are newly added in subclass should have default
        # values
        ...


# noinspection PyPep8Naming
def check_FrozenEnum():

    cls: t.Type[FrozenEnum]
    for cls in FrozenEnum.available_sub_classes():

        # check if the subclassing class also extends enum.Enum
        # NOTE: the if condition is to bypass when FrozenEnum class is
        # getting created. It is not yet created so we cannot detect it here
        if cls.__mro__[1] != YamlRepr:
            if not issubclass(cls, enum.Enum):
                e.code.CodingError(
                    msgs=[
                        f"While subclassing `FrozenEnum` make sure "
                        f"that you it also extends `enum.Enum`",
                        f"Check class {cls}"
                    ]
                )


def main():
    check_classes_that_should_not_be_overridden()
    check_things_to_be_cached()
    check_things_not_to_be_cached()
    check_things_not_to_be_overridden()
    check_things_to_be_dataclasses()
    check_everyone_has_logger()

    check_YamlRepr()
    check_HashableClass()
    check_Config()
    check_FrozenEnum()


if __name__ == '__main__':
    main()
