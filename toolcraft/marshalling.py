import dataclasses
import inspect
import abc
import yaml
import hashlib
import typing as t
import datetime
import numpy as np
import pyarrow as pa
import pathlib

from . import util, logger, settings
from . import error as e

# to avoid cyclic imports
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from . import storage
    from . import gui


_LOGGER = logger.get_logger()


# Class to keep track of all concrete HashableClass class's used in the
# entire application
# noinspection PyTypeChecker
ALL_TRACKERS = None  # type: t.List[t.Type[YamlRepr]]
YAML_TAG_MAPPING = {}


# use this as default value for kwargs in HashableClass.__call__ to indicate
# that kwarg was not provided
NOT_PROVIDED = '__NOT_PROVIDED__'

# todo: come up with more appropriate file extensions if needed like
#  model.info, dataset.info, file_group.info,
#  model.config, dataset.config ...
# HASH_Suffix.INFO = ".hashinfo"
# HASH_Suffix.CONFIG = ".hashconfig"
# META_Suffix.INFO = ".metainfo"


class _ReadOnlyClass(type):
    def __setattr__(self, key, value):
        e.code.NotAllowed(
            msgs=[
                f"Class {self} is read only.",
                f"You cannot override its attribute {key!r} programmatically.",
                f"Edit it during class definition ..."
            ]
        )


class Internal:
    """
    Need:
      As Hashable dataclass is Frozen we need to have some way of storing
      variables that can be updated and not part of serialization process
    """

    # we set this in __call__ so that with context has access to kwargs
    # passes in __call__ method
    # todo: make this a class so that strings are not used to get members. We
    #  know that typing support is difficult to achieve. But we can override
    #  __getitem__ to throw custom error indicating on call kwargs have changed
    on_call_kwargs: t.Union[t.Dict[str, t.Any]] = None
    progress_bar: logger.ProgressBar = None
    prefetched_on_first_call: bool

    class LITERAL:
        store_key = "INTERNAL"

    @property
    def owner(self) -> "Tracker":
        return self.__owner__

    @property
    @util.CacheResult
    def __variable_names__(self) -> t.List[str]:
        _ret = []
        for _c in self.__class__.__mro__:
            if hasattr(_c, "__annotations__"):
                _ret.extend(
                    list(_c.__annotations__.keys())
                )
        return list(set(_ret))

    def __init__(self, owner: "Tracker"):

        # store_key must not be present as it is not loaded from serialized file
        if hasattr(owner, self.LITERAL.store_key):
            e.code.CodingError(
                msgs=[
                    f"Did you miss to cache the `internal` property?",
                    f"Looks like {self.LITERAL.store_key} is already present",
                    f"We do not expect this to happen."
                ]
            )

        # keep internal instance reference in owner
        owner.__dict__[self.LITERAL.store_key] = self

        # also store owner instance reference
        self.__owner__ = owner

        # if annotations have default values the make them available in
        # container
        for _vn in self.__variable_names__:
            try:
                setattr(
                    self, _vn, getattr(self.__class__, _vn)
                )
            except AttributeError:
                ...

    def __setattr__(self, key: str, value):
        # bypass dunder keys
        if key.startswith('__'):
            return super().__setattr__(key, value)

        # only keys that are annotated can be set
        e.validation.ShouldBeOneOf(
            value=key, values=self.__variable_names__,
            msgs=[
                f"Member `{key}` is not annotated in class "
                f"{self.__class__} so you cannot set it."
            ]
        )

        # if item is allowed to be set only once then do not allow it to be
        # set again
        if key not in self.vars_that_can_be_overwritten():
            if self.has(key):
                if isinstance(value, HashableClass):
                    _str_value = value.yaml()
                else:
                    _str_value = str(value)
                e.code.NotAllowed(
                    msgs=[
                        f"The item `{key}` is already present in the internal "
                        f"object.",
                        f"Please refrain from overwriting it as it is "
                        f"configured to be written only once.",
                        f"You are overwriting it with value `{_str_value}`",
                        f"In case you want to overwrite it then override "
                        f"method `self.vars_that_can_be_overwritten` so "
                        f"that we allow you to overwrite it."
                    ]
                )

        # set attribute
        return super().__setattr__(key, value)

    def __getattr__(self, item):

        # bypass dunder keys
        if item.startswith('__'):
            return super().__getattribute__(item)

        # check if already set
        # We go via __dict__ as using self.has causes recursion
        if item not in self.__dict__.keys():
            e.code.CodingError(
                msgs=[
                    f"You cannot access annotated attribute `{item}` as it is "
                    f"not yet set",
                ]
            )

        # return
        return super().__getattribute__(item)

    # noinspection PyMethodMayBeStatic
    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return ['on_call_kwargs', "progress_bar", "part_iterator_state"]

    def has(self, item: str) -> bool:
        if item not in self.__variable_names__:
            e.code.CodingError(
                msgs=[
                    f"You can only test has(...) for items that are annotated",
                    f"Item `{item}` is not one of "
                    f"{self.__variable_names__}"
                ]
            )
        return item in self.__dict__.keys()


class Tracker:
    """
    Tracker that can track all classes in this system

    todo: for on_enter on_exit on_call we need to explore use of contextlib
      + https://docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
      + this library is builtin and hence justifies usage for same
      + it also has async context support so check it out
    """

    class LITERAL(metaclass=_ReadOnlyClass):

        def __new__(cls, *args, **kwargs):
            e.code.NotAllowed(
                msgs=[
                    f"This class is meant to be used to hold class "
                    f"variables only",
                    f"Do not try to create instance of {cls} ..."
                ]
            )

    @property
    @util.CacheResult
    def internal(self) -> "Internal":
        return Internal(self)

    @property
    def is_called(self) -> bool:
        """
        Detects is hashable is called ... and hence can be used in with
        context or while iterating
        """
        return self.internal.on_call_kwargs is not None

    @property
    @util.CacheResult
    def is_iterable(self) -> bool:
        """
        Indicates weather this class can be iterated or not
        """
        _iterable_length_overridden = \
            self.__class__.iterable_length != Tracker.iterable_length
        _on_iter_overridden = \
            self.__class__.on_iter != Tracker.on_iter
        if _iterable_length_overridden ^ _on_iter_overridden:
            e.code.CodingError(
                msgs=[
                    f"Both property iterable_length and method on_iter must "
                    f"be overridden if you want to support iterating on "
                    f"instances of class {self.__class__}",
                    dict(
                        _iterable_length_overridden=_iterable_length_overridden,
                        _on_iter_overridden=_on_iter_overridden,
                    )
                ]
            )
        return _iterable_length_overridden

    # noinspection PyPropertyDefinition,PyTypeChecker
    @property
    def iterable_length(self) -> int:
        e.code.NotSupported(
            msgs=[
                f"Override this property in class "
                f"{self.__class__} if you want to iterate "
                f"over tracker"
            ]
        )

    # noinspection PyPropertyDefinition,PyTypeChecker
    @property
    def iterable_unit(self) -> str:
        e.code.NotSupported(
            msgs=[
                f"Override this property in class "
                f"{self.__class__} if you want to iterate "
                f"over tracker"
            ]
        )

    @property
    @util.CacheResult
    def dataclass_field_names(self) -> t.List[str]:
        # noinspection PyUnresolvedReferences
        return list(self.__dataclass_fields__.keys())

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

    def __call__(
        self,
        iter_show_progress_bar: bool = None,
        iter_desc: str = None,
        **kwargs,
    ) -> "Tracker":
        """
        We use __call__ with __enter__ and __exit__ as context manager ...

        todo: we can use contextlib library in future as it has support for
          async methods
          https://docs.python.domainunion.de/3/library/contextlib.html

        """

        # prefetch if not done
        # handle expensive things that can reduce load on consecutive calls
        # on same instance
        if not self.internal.has('prefetched_on_first_call'):
            self.prefetch_stuff_before_first_call()

        # set call
        if self.is_called:
            e.code.CodingError(
                msgs=[
                    f"Internal variable on_call_kwargs is already set.",
                    f"Did you miss to call your code from within with context "
                    f"and forgot to exit properly in previous runs??",
                    f"Or else try to call this with for statement ..."
                ]
            )
        else:
            # if iterating is not supported then make sure that iter_* kwargs
            # are None
            if self.is_iterable:
                if iter_show_progress_bar is None:
                    # the default when self is iterable is to show progress bar
                    iter_show_progress_bar = True
                self.internal.on_call_kwargs = {
                    'iter_show_progress_bar': iter_show_progress_bar,
                    'iter_desc': iter_desc,
                    **kwargs
                }
            else:
                if iter_show_progress_bar is not None or iter_desc is not None:
                    e.code.CodingError(
                        msgs=[
                            f"The class {self.__class__} does not override "
                            f"on_iter that is it does not support iterating "
                            f"so please make sure to set iter related "
                            f"__call__ kwargs to None"
                        ]
                    )
                    # skip adding iter related kwargs
                self.internal.on_call_kwargs = kwargs

        # do something once kwargs are available
        self.on_call()

        # return
        return self

    def __enter__(self) -> "Tracker":
        self.on_enter()
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
        self.on_exit()

    def __iter__(self) -> t.Iterable:
        # the with statement here helps users to directly iterate over
        # hashable class without using with statement ... but nonetheless we
        # expect you to call __call__ while looping over
        with self:
            # get iterable
            _iterable = self.on_iter()

            # get some vars
            _show_progress_bar = \
                self.internal.on_call_kwargs['iter_show_progress_bar']
            _iter_desc = self.internal.on_call_kwargs['iter_desc']

            # iterate
            if _show_progress_bar:
                with logger.ProgressBar(
                    total=self.iterable_length,
                    unit=self.iterable_unit,
                    desc=_iter_desc,
                ) as pg:
                    self.internal.progress_bar = pg
                    for _ in _iterable:
                        pg.update(1)
                        yield _
                    self.internal.progress_bar = None
            else:
                self.internal.progress_bar = None
                for _ in _iterable:
                    yield _

    def __del__(self):
        self.on_del()

    def prefetch_stuff_before_first_call(self):
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
        if self.internal.has('prefetched_on_first_call'):
            e.code.CodingError(
                msgs=[
                    f"The method `prefetch_stuff` can be called only once ..."
                ]
            )
        else:
            # set var
            self.internal.prefetched_on_first_call = True

    def on_call(self):
        """
        Override this in case you want to do something when __call__ is called
        """
        # ----------------------------------------------------- 01
        if not self.is_called:
            e.code.CodingError(
                msgs=[
                    f"Internal variable on_call_kwargs is not yet set",
                    f"Did you miss to call your code from within with context",
                    f"Also did you miss to use __call__",
                    f"If iterating over Hashable class make sure that "
                    f"__call__ is called which sets kwargs related to "
                    f"iteration or anything else"
                ]
            )

    def on_enter(self):
        """
        Override this in case you want to do something when __enter__ is called
        """
        if not self.is_called:
            e.code.CodingError(
                msgs=[
                    f"Internal variable on_call_kwargs is not yet set",
                    f"Did you miss to call your code from within with context",
                    f"Also did you miss to use __call__",
                    f"If iterating over Hashable class make sure that "
                    f"__call__ is called which sets kwargs related to "
                    f"iteration or anything else"
                ]
            )

    def on_exit(self):
        """
        Override this in case you want to do something when __exit__ is called
        """
        if not self.is_called:
            e.code.CodingError(
                msgs=[
                    f"Internal variable `on_call_kwargs` is not yet set",
                    f"Did you miss to call your code from within with context",
                    f"Also did you miss to use __call__",
                    f"If iterating over Hashable class make sure that "
                    f"__call__ is called which sets kwargs related to "
                    f"iteration or anything else"
                ]
            )

        # reset on_call_kwargs
        self.internal.on_call_kwargs = None

    # noinspection PyTypeChecker
    def on_iter(self) -> t.Iterable[t.Any]:
        """
        Override this in case you want to do something when __iter__ is called
        """
        e.code.CodingError(
            msgs=[
                f"Looks like you do not support iterating over "
                f"hashable class {self.__class__}",
                f"Considering overriding `on_iter` in class {self.__class__} "
                f"to return an iterator"
            ]
        )

    def on_del(self):
        ...

    @classmethod
    def class_init(cls):
        """
        Alternative to avoid using dunder method __init_subclass__
        """
        ...

    @classmethod
    def available_concrete_sub_classes(cls) -> t.List[
        t.Type["YamlRepr"]
    ]:
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
    def available_sub_classes(cls) -> t.List[
        t.Type["YamlRepr"]
    ]:
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
            item, Dumper=YamlDumper,
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
    def load(
        cls, file_or_text: t.Union[pathlib.Path, str],  **kwargs
    ) -> t.Union[dict, "YamlRepr"]:
        # get text
        _text = file_or_text
        if isinstance(file_or_text, pathlib.Path):
            _text = file_or_text.read_text()

        # load with Loader
        _loader = YamlLoader(stream=_text, extra_kwargs=kwargs)
        try:
            _instance = _loader.get_single_data()
        finally:
            _loader.dispose()

        # check
        if _instance.__class__ != cls:
            e.code.CodingError(
                msgs=[
                    f"We expect yaml str is for correct class ",
                    {
                        "expected": cls,
                        "found": _instance.__class__
                    }
                ]
            )

        # return
        return _instance


class YamlRepr(Tracker):

    """
    This class makes it possible to have YamlRepr for dataclasses.

    NOTE: do nat make this class abstract as FrozenEnum like classes will not
    work
    """

    @classmethod
    def class_init(cls):
        """
        """
        global YAML_TAG_MAPPING

        # call super
        super().class_init()

        # only do for concrete classes
        if not inspect.isabstract(cls):

            # register yaml tag for concrete classes
            yaml.add_representer(cls, cls._yaml_representer, Dumper=YamlDumper)
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
                    e.code.CodingError(
                        msgs=[
                            f"The yaml tag `{_yaml_tag}` is already registered "
                            f"for class `{YAML_TAG_MAPPING[_yaml_tag]}`",
                            f"But you are again trying to use same tag for "
                            f"class `{cls}`.",
                            f"Please check if you have overridden `yaml_tag` "
                            f"method appropriately ... "
                        ]
                    )

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
    def _yaml_representer(
        cls, dumper: YamlDumper, data: "YamlRepr"
    ) -> yaml.Node:
        # get yaml state dict
        _yaml_state = data.as_dict()

        # return representer
        return dumper.represent_mapping(
            cls.yaml_tag(), _yaml_state
        )

    @classmethod
    def _yaml_constructor(
        cls, loader: YamlLoader, node: yaml.Node
    ) -> "YamlRepr":
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
    def from_yaml(
        cls,
        file_or_text: t.Union[pathlib.Path, str],  **kwargs
    ) -> "YamlRepr":
        # return
        return YamlLoader.load(cls, file_or_text=file_or_text, **kwargs)

    def clone(self) -> "YamlRepr":
        return self.from_yaml(self.yaml())

    def as_dict(
        self
    ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        e.code.CodingError(
            msgs=[
                f"We expect you to override this method in class "
                f"{self.__class__}"
            ]
        )
        return {}

    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
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
                e.validation.NotAllowed(
                    msgs=[
                        f"Looks like you are using a dict that is not builtin "
                        f"python dict.",
                        f"Found dict of type {type(item)}!={dict}"
                    ] + _err_msg
                )
        elif isinstance(item, list):
            if item.__class__ != list:
                e.validation.NotAllowed(
                    msgs=[
                        f"Looks like you are using a list that is not builtin "
                        f"python list.",
                        f"Found list of type {type(item)}!={list}"
                    ] + _err_msg
                )
        else:
            e.validation.NotAllowed(
                msgs=[
                    f"We expect item to be a dict or list but instead found "
                    f"item of type {type(item)}"
                ] + _err_msg
            )

        # ------------------------------------------------------------ 04
        # if dict check keys and values
        if isinstance(item, dict):
            # -------------------------------------------------------- 04.01
            # loop over items
            for k, v in item.items():
                # ---------------------------------------------------- 04.02
                # compute current key
                current_key = f">{k}" if key_or_index is None else \
                    f"{key_or_index}>{k}"
                # ---------------------------------------------------- 04.03
                # dict key needs to be str or int
                if not isinstance(k, (str, int)):
                    e.validation.NotAllowed(
                        msgs=[
                            f"We expect the dict to be frozen to have str or "
                            f"int keys",
                            f"Found key `{k}` of type {type(k)}."
                        ] + _err_msg
                    )
                # ---------------------------------------------------- 04.04
                # if nested dict or list try to verify keys and values
                if isinstance(v, (dict, list)):
                    # check the value
                    cls.can_be_frozen(
                        v, current_key, allowed_types)
                # ---------------------------------------------------- 04.05
                # else value needs to be one of supported hashable
                else:
                    e.validation.ShouldBeInstanceOf(
                        value=v,
                        value_types=allowed_types,
                        msgs=[
                            f"Value for key `{k}` in dict cannot be frozen"
                        ] + _err_msg
                    )

        # ------------------------------------------------------------ 05
        # if list check values
        elif isinstance(item, list):
            # -------------------------------------------------------- 05.01
            # loop over items
            for i, v in enumerate(item):
                # ---------------------------------------------------- 05.02
                # compute current key
                current_key = f">{i}" if key_or_index is None else \
                    f"{key_or_index}>{i}"
                # ---------------------------------------------------- 05.03
                # value needs to be hashable
                e.validation.ShouldBeInstanceOf(
                    value=v,
                    value_types=allowed_types + (dict, list),
                    msgs=[
                        f"Value for index `{i}` in list cannot be frozen"
                    ] + _err_msg
                )
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
            e.code.ShouldNeverHappen(msgs=[])

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


class FrozenKeras(YamlRepr):

    class LITERAL(YamlRepr.LITERAL):
        SUPPORTED_KERAS_OBJECTS_TYPE = t.Union[
            "tk.losses.Loss",
            "tk.optimizers.Optimizer",
            "tk.optimizers.schedules.LearningRateSchedule",
        ]
        # noinspection PyUnresolvedReferences
        SUPPORTED_KERAS_OBJECTS = SUPPORTED_KERAS_OBJECTS_TYPE.__args__

    def __init__(self, item: LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE):
        # -------------------------------------------------------- 01
        # validate
        # -------------------------------------------------------- 01.01
        # check item type
        e.validation.ShouldBeInstanceOf(
            value=item,
            value_types=self.LITERAL.SUPPORTED_KERAS_OBJECTS,
            msgs=[
                f"Unrecognized item type that cannot be freezed ..."
            ]
        )
        # -------------------------------------------------------- 01.02
        # check if keras config is serializable as per our code
        _k_config = item.get_config()
        self.can_be_frozen(
            _k_config,
            key_or_index=f"{self.yaml_tag()}::",
            allowed_types=SUPPORTED_HASHABLE_OBJECTS,
        )

        # -------------------------------------------------------- 02
        # save keras related information
        self._k_class = item.__class__
        self._k_config = _k_config
        # delete item so that the graph do not have any information
        del item

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!frozen_keras"

    def get(self) -> LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE:
        # this basically picks up class of keras instance `self._item` and
        # creates instance from config given by `self._item`
        return self._k_class.from_config(self._k_config)

    def as_dict(
        self
    ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        return {
            "module": self._k_class.__module__,
            "class": self._k_class.__name__,
            "config": self._k_config.copy()
        }

    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
    ) -> "FrozenKeras":
        _k_class = util.load_class_from_strs(
            class_name=yaml_state["class"],
            class_module=yaml_state["module"],
        )  # type: t.Type[cls.LITERAL.SUPPORTED_KERAS_OBJECTS_TYPE]
        return cls(item=_k_class.from_config(yaml_state["config"]))


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

    def as_dict(
        self
    ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        # noinspection PyUnresolvedReferences
        return {
            "name": self.name
        }

    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
    ) -> "FrozenEnum":
        return getattr(cls, yaml_state["name"])


# @dataclasses.dataclass(eq=True, frozen=True)
@dataclasses.dataclass(frozen=True)
class HashableClass(YamlRepr, abc.ABC):
    """
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

        todo: If you want to use some grouping we need to figure out group_by
          property .... check FileGroup
        """
        return self.hex_hash

    @property
    def group_by(self) -> t.Optional[t.Union[str, t.List[str]]]:
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
        e.code.CodingError(
            msgs=[
                f"Do you need some grouping?",
                f"Are you using this for plotting or organizing folders?",
                f"Then please override this property or else refrain from "
                f"using this property.",
                f"If you do not want to use grouping please consider "
                f"returning None ..."
                f"Check class {self.__class__} and override its property "
                f"`group_by` if needed",
            ]
        )
        return ""

    @property
    @util.CacheResult
    def hex_hash(self) -> str:
        """
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
        return hashlib.md5(
            f"{self.yaml()}".encode('utf-8')
        ).hexdigest()

    # noinspection PyPropertyDefinition,PyTypeChecker
    @property
    @util.CacheResult
    def results_folder(self) -> "storage.ResultsFolder":
        e.code.NotAllowed(
            msgs=[
                f"Please override `results_folder` property if you want to "
                f"save results or StoreFields for hashable class "
                f"{self.__class__}"
            ]
        )

    # do not cache as dynamic list will be popped out and the reference to
    # spinner will hang on and ... on consecutive calls cached spinners from
    # past runs will get used
    @property
    def spinner(self) -> logger.Spinner:
        _spinner = logger.Spinner.get_last_spinner()
        if _spinner is None:
            e.code.CodingError(
                msgs=[
                    f"Please use this spinner property from within code that "
                    f"is called within spinner loops",
                    f"Looks like the code was never called within "
                    f"spinner loops"
                ]
            )
        return _spinner

    # todo: this was for yaml repr .... but not needed ... so may be we
    #  still need to explore the default __repr__ for dataclass ...
    #  meanwhile __str__ suffice to generate unique text to save on disk ...
    # def __repr__(self) -> str:
    #     return util.dataclass_to_yaml_repr(self)

    def __post_init__(self):

        # --------------------------------------------------------------01
        # do instance related things
        with logger.Spinner(
            title=f"Init "
                    f"{self.__class__.__module__}."
                    f"{self.__class__.__name__}",
            logger=_LOGGER,
        ) as _s:
            # ----------------------------------------------------------01.01
            # todo: add global flag to start and stop validation
            # make sure that everything is light weight so that object creation
            # is fast ...
            _s.text = "validating ..."
            self.init_validate()
            # ----------------------------------------------------------01.02
            # call init logic
            _s.text = "initiating ..."
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
        if settings.DEBUGGING:
            return f"... debugging ... {self.name}"

        # if interactive mode then allow use of __str__
        if settings.INTERACTIVE:
            return f"... interactive ... {self.name}"

        # when not in debug method we do not allow to print this object
        # instead `self.yaml()` should be used
        e.code.CodingError(
            msgs=[
                f"We do not allow to use __str__ or __repr__ of the "
                f"marshalling class.",
                f"Instead use `.yaml()` method."
            ]
        )
        return ""

    def __eq__(self, other):
        # todo: find better ways with marshalling class and when full
        #  serialization is supported
        # Note this helps to ignore `init=True` fields in equality check
        return self.hex_hash == other.hex_hash

    @classmethod
    def class_init(cls):
        """
        Note that the class_init is called from __init_subclass__ and is not
        aware of dataclasses.dataclass related things. SO in order to have
        some HashableClass related class level thing swe need to do in in
        __post_init__ only once per class .... as by then the cls is aware
        that it is dataclass ;)
        """
        # call super
        super().class_init()

        # hook up instance methods
        # Note this we can also so in init_class but better do it here so
        # that we need not wait till instance is created ...
        cls.hook_up_methods()

    @classmethod
    def block_fields_in_subclasses(cls) -> bool:
        """
        Override this if you do not want subclasses to have new fields
        """
        return False

    def as_dict(
        self
    ) -> t.Dict[str, "SUPPORTED_HASHABLE_OBJECTS_TYPE"]:
        _ret = {}
        for f_name in self.dataclass_field_names:
            _ret[f_name] = getattr(self, f_name)
        return _ret

    def init_validate(self):
        """
        Simple dataclass field validation .... make sure that no attributes or
        memory is consumed while doing this
        """
        global SUPPORTED_HASHABLE_OBJECTS

        # --------------------------------------------------------------01
        # loop over field values to validate them
        for f_name in self.dataclass_field_names:
            # ----------------------------------------------------------01.01
            # get value for the field
            v = getattr(self, f_name)
            # ----------------------------------------------------------01.02
            # raise error to inform to use FrozenDict
            if isinstance(v, dict):
                self.can_be_frozen(
                    item=v,
                    key_or_index=f"{f_name}::",
                    allowed_types=SUPPORTED_HASHABLE_OBJECTS,
                )
            # ----------------------------------------------------------01.03
            # raise error to inform to use FrozenKeras
            elif isinstance(v, FrozenKeras.LITERAL.SUPPORTED_KERAS_OBJECTS):
                e.validation.NotAllowed(
                    msgs=[
                        f"Please set the field `{f_name}` where the `keras` "
                        f"object is wrapped with `{FrozenKeras.__name__}` ... "
                        f"check class {self.__class__}"
                    ]
                )
            # ----------------------------------------------------------01.04
            # if list check if values inside are hashable
            elif isinstance(v, list):
                self.can_be_frozen(
                    item=v,
                    key_or_index=f"{f_name}::",
                    allowed_types=SUPPORTED_HASHABLE_OBJECTS,
                )
            # ----------------------------------------------------------01.05
            # else should be one of supported type
            else:
                e.validation.ShouldBeInstanceOf(
                    value=v, value_types=SUPPORTED_HASHABLE_OBJECTS,
                    msgs=[
                        f"Check value of field `{f_name}` for class "
                        f"{self.__class__}"
                    ]
                )

    def init(self):
        # create store fields in advance
        # todo: this we do unnecessarily and folders will be created even if
        #  we do not use the store fields ... this also adds small overhead
        #  while creating instances of HashableClasses instances ...
        #  Ideally if this is connected the respective Tables are read on
        #  first call ... Currently we so this in advance only to avoid
        #  polluting logs .... check if we can handle logging of Table init
        #  in first call smartly so that logs are not polluted
        if self.__class__.results_folder != HashableClass.results_folder:
            self.results_folder.init_store_df_files()

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

    def get_gui_button(
        self,
        button_label: str,
        callable_name: str,
        receiver: "gui.Widget",
        allow_refresh: bool,
        tab_group_name: str = None,
    ) -> "gui.Button":
        """
        todo: support refresh
        """

        # ---------------------------------------------------- 01
        # import
        from . import gui

        # ---------------------------------------------------- 02
        # test callable name
        if not util.rhasattr(self, callable_name):
            e.code.CodingError(
                msgs=[
                    f"Callable `{callable_name}` not available for "
                    f"HashableClass {self.__class__}"
                ]
            )

        # ---------------------------------------------------- 03
        # create callback
        _callback = gui.callback.HashableMethodRunnerCallback(
            hashable=self,
            callable_name=callable_name,
            receiver=receiver,
            allow_refresh=allow_refresh,
            tab_group_name=tab_group_name,
        )

        # ---------------------------------------------------- 04
        # create and return button
        return gui.Button(
            label=button_label, callback=_callback,
        )


SUPPORTED_HASHABLE_OBJECTS_TYPE = t.Union[
    int, float, str, slice, list, dict,
    np.float32, np.int64, np.int32,
    datetime.datetime, None,
    FrozenEnum, FrozenKeras, HashableClass,
    pa.Schema,
]
# noinspection PyUnresolvedReferences
SUPPORTED_HASHABLE_OBJECTS = SUPPORTED_HASHABLE_OBJECTS_TYPE.__args__
