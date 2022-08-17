"""
Module to hold simple utilities that can be built with minimal dependencies.
# todo: Cut down on dependencies ...
"""
import typing as t
import re
from collections import defaultdict
import pyarrow as pa
import numpy as np
import pickle
import inspect
import abc
import gc
import types
import datetime
import pathlib
import traceback
import time
import functools
import zipfile
import dataclasses
import collections
import importlib
import pandas as pd
import stat
import atexit
import multiprocessing as mp
import socket
import sys
import contextlib
_now = datetime.datetime.now


from . import logger
from . import error as e

# noinspection PyUnreachableCode
if False:
    from . import storage as s

_LOGGER = logger.get_logger()

# to see what this octave values do try below code
# import stat
# stat.filemode(0o444)
_FILE_READ_MODE = 0o0444
_FILE_WRITE_MODE = 0o0666
_FILE_EXE_MODE = 0o0777

# note keep this as dunder style
CACHE_KEY = "CACHE"


# noinspection PyUnresolvedReferences,PyMethodParameters,PyArgumentList
class MultipleInheritanceNamedTupleMeta(t.NamedTupleMeta):
    # noinspection SpellCheckingInspection
    def __new__(mcls, typename, bases, ns):
        if t.NamedTuple in bases:
            base = super().__new__(mcls, '_base_' + typename, bases, ns)
            bases = (
                base,
                *(b for b in bases if not isinstance(b, t.NamedTuple))
            )
        return super(t.NamedTupleMeta, mcls).__new__(
            mcls, typename, bases, ns)


class OurNamedTuple(metaclass=MultipleInheritanceNamedTupleMeta):

    AVAILABLE_TUPLES = []  # type: t.List[t.Type[OurNamedTuple]]

    def __init_subclass__(cls, **kwargs):
        # save reference
        cls.AVAILABLE_TUPLES.append(cls)

        # call super
        return super().__init_subclass__(**kwargs)

    @classmethod
    def available_sub_classes(cls) -> t.List[t.Type["OurNamedTuple"]]:
        return [
            c for c in cls.AVAILABLE_TUPLES
            if issubclass(c, cls)
        ]

    def check_equal(self, other):
        # if class is different return false
        if self.__class__ != other.__class__:
            return False

        # loop over named tuple fields
        # noinspection PyUnresolvedReferences
        for f_name in self._fields:
            # get field value
            sv = getattr(self, f_name)
            ov = getattr(other, f_name)

            # check if type same
            if type(sv) != type(ov):
                return False

            # if dict
            if isinstance(sv, dict):
                # check if keys are same
                sv_ks = list(sv.keys())
                ov_ks = list(ov.keys())
                sv_ks.sort()
                ov_ks.sort()
                if sv_ks != ov_ks:
                    return False
                # check values in the dict
                for kk in sv_ks:
                    if not isinstance(
                        sv[kk], np.ndarray
                    ) or not isinstance(
                        sv[kk], np.ndarray
                    ):
                        raise e.code.CodingError(
                            msgs=[
                                f"The named tuple "
                                f"{self.__class__} can only hold "
                                f"numpy arrays or dict of numpy arrays",
                                f"Check key {kk} in the dict of field {f_name} "
                                f"of named tuple {self.__class__}"
                            ]
                        )
                    if not np.array_equal(sv[kk], ov[kk]):
                        return False
            # else if numpy array
            elif isinstance(sv, np.ndarray):
                if not np.array_equal(sv, ov):
                    return False
            # else
            else:
                raise e.code.CodingError(
                    msgs=[
                        f"The named tuple {self.__class__} can only hold "
                        f"numpy arrays or dict of numpy arrays ... "
                        f"check field {f_name}",
                        {
                            "self type": type(sv),
                            "other type": type(ov),
                        }
                    ]
                )

        # if all is well return True
        return True


class _SmartListDict:
    """
    We can also use this to limit the number of items added to this list or dict
    """

    def __init__(
        self,
        allow_nested_dict_or_list: bool,
        supplied_items: t.Optional[t.Union[list, dict]] = None,
        use_specific_class: t.Type = None,
        allowed_types: t.Tuple[t.Type] = t.Any,
    ):
        # ---------------------------------------------------------- 01
        # set vars
        self.allow_nested_dict_or_list = allow_nested_dict_or_list
        self.allowed_types = allowed_types
        self.use_specific_class = use_specific_class
        if use_specific_class is not None:
            if allowed_types != t.Any:
                raise e.code.NotAllowed(
                    msgs=[
                        f"If you are using specific class then do not provide "
                        f"value for `allowed_types`"
                    ]
                )

        # ---------------------------------------------------------- 02
        # bake container
        if isinstance(self, SmartList):
            _items = []
            if bool(supplied_items):
                # check type
                if not isinstance(supplied_items, list):
                    raise e.code.NotAllowed(
                        msgs=[
                            f"We expect supplied items to be a list but found "
                            f"{type(supplied_items)}"
                        ]
                    )
                # populate
                for v in supplied_items:
                    _items.append(self._make_it_smart(v))
        elif isinstance(self, SmartDict):
            _items = {}
            if bool(supplied_items):
                # check type
                if not isinstance(supplied_items, dict):
                    raise e.code.NotAllowed(
                        msgs=[
                            f"We expect supplied items to be a dict but found "
                            f"{type(supplied_items)}"
                        ]
                    )
                # populate
                for k, v in supplied_items.items():
                    if not isinstance(k, str):
                        raise e.code.NotAllowed(
                            msgs=[
                                f"We expect dict key to be str but found type "
                                f"{type(k)}"
                            ]
                        )
                    _items[k] = self._make_it_smart(v)
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unsupported type {type(self)}"])
        # store it
        self._items = _items  # type: t.Union[list, dict]

    def __getstate__(self):
        # useful for yaml.dump
        return self._items

    def __len__(self) -> int:
        return len(self._items)

    def _make_it_smart(
        self, item: t.Union[list, dict, t.Any]
    ) -> t.Union["SmartList", "SmartDict", t.Any]:
        if isinstance(item, list):
            if self.allow_nested_dict_or_list:
                return SmartList(
                    allow_nested_dict_or_list=True,
                    supplied_items=item,
                    use_specific_class=self.use_specific_class,
                    allowed_types=self.allowed_types,
                )
            else:
                raise e.code.NotAllowed(
                    msgs=[
                        f"You have configured SmartList to not have nested "
                        f"elements .. so we raise error"
                    ]
                )
        elif isinstance(item, dict):
            if self.allow_nested_dict_or_list:
                return SmartDict(
                    allow_nested_dict_or_list=True,
                    supplied_items=item,
                    use_specific_class=self.use_specific_class,
                    allowed_types=self.allowed_types,
                )
            else:
                raise e.code.NotAllowed(
                    msgs=[
                        f"You have configured SmartDict to not have nested "
                        f"elements .. so we raise error"
                    ]
                )
        else:
            # if specific class is used check if item has specific type
            if self.use_specific_class is not None:
                if self.use_specific_class != item.__class__:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"You have restricted to use items with specific "
                            f"class {self.use_specific_class}, but the item "
                            f"you are using has class {item.__class__}"
                        ]
                    )
            # if there is restriction on allowed types then check
            if self.allowed_types != t.Any:
                e.validation.ShouldBeInstanceOf(
                    value=item,
                    value_types=self.allowed_types,
                    msgs=[
                        f"You have restricted allowed types in "
                        f"SmartList/SmartDict",
                        f"Only allowed types are: ",
                        self.allowed_types,
                    ]
                ).raise_if_failed()
            return item


# noinspection SpellCheckingInspection
class SmartList(_SmartListDict):

    def append(self, obj: t.Any) -> None:
        # append
        self._items.append(self._make_it_smart(obj))


# noinspection SpellCheckingInspection
# todo: need to explore how addidct can be supported .... this will allow to
#  have dicts with typing support while addict takes care of making it
#  dictionaries .... Currently the __setitem__ causes some problem ...
#  will explore later ...
#  Example as below:
#  class A(SmartDict):
#      a: int
#  a = A()
#  a.a = 33  # typing will work here ;)
#  print(a)  # prints: {'a': 33}
# class SmartDict(addict.Dict):
class SmartDict(_SmartListDict):
    """
    todo: refer addict and see if we can support it here
    """

    def __setitem__(self, key: t.Union[int, str], value):

        # ---------------------------------------------------------- 01
        # check if key is str
        e.validation.ShouldBeInstanceOf(
            value=key, value_types=(int, str, ),
            msgs=[
                f"We expect key to be always a str or int.",
                f"Found unsupported type {type(key)}"
            ]
        ).raise_if_failed()

        # ---------------------------------------------------------- 02
        # check if key present
        e.validation.ShouldNotBeOneOf(
            value=key, values=tuple(self._items.keys()),
            msgs=[
                f"Item {key!r} is already present in "
                f"SmartDict and you "
                f"cannot overwrite it...",
                f"If you want to overwrite we recommend to delete then add it."
            ]
        ).raise_if_failed()

        # ---------------------------------------------------------- 03
        # set item
        self._items[key] = self._make_it_smart(value)

    def __iter__(self):
        raise e.code.CodingError(
            msgs=[
                "We so not allow to iterate over smart dict ..."
            ]
        )

    def __getitem__(self, item):

        # does key exist
        if item not in self._items.keys():
            raise e.code.CodingError(
                msgs=[f"We cannot find the requested item {item!r} in the SmartDict."]
            )

        # return
        return self._items[item]

    def __delitem__(self, key):

        # if key does not exist do not delete
        e.validation.ShouldBeOneOf(
            value=key, values=tuple(self._items.keys()),
            msgs=[
                f"We cannot delete the item `{key}` as it is not present in "
                f"the SmartDict."
            ]
        ).raise_if_failed()

        # delete ... this will also propagate to __del__ of item so that you
        # can manage __del__ of what is contained
        del self._items[key]

    def get(self, index: int) -> t.Any:
        if index >= len(self._items):
            raise e.validation.NotAllowed(
                msgs=["The index exceeds the number of items availbale in smart dict"]
            )
        if index < 0:
            index = len(self._items) + index
        for _i, _ in enumerate(self._items.keys()):
            if _i == index:
                return self._items[_]

    def keys(self) -> t.Generator[t.Union[int, str], None, None]:
        """
        yield so that it remains fast
        """
        for _ in self._items.keys():
            yield _

    def values(self) -> t.Generator[t.Any, None, None]:
        """
        yield so that it remains fast
        """
        for _ in self._items.values():
            yield _

    def items(self) -> t.Generator[t.Tuple[t.Union[int, str], t.Any], None, None]:
        """
        yield so that it remains fast
        """
        for _k, _v in self._items.items():
            yield _k, _v

    def insert_before(self, key: t.Union[int, str], key_values: t.Dict[t.Union[int, str], t.Any]):
        # backup
        _items = self._items

        # validate if key present
        if key not in _items.keys():
            raise e.validation.NotAllowed(
                msgs=[f"we cannot find key {key} in the smart dict"]
            )

        # wipe internal container
        self._items = {}

        # add the items back
        for _k, _v in _items.items():
            # if key matches
            if _k == key:
                for __k, __v in key_values.items():
                    # this will also validate what you add before
                    self[__k] = __v
            # we use fast add to dict as this was already validated
            self._items[_k] = _v

    def insert_after(self, key: t.Union[int, str], key_values: t.Dict[t.Union[int, str], t.Any]):
        # backup
        _items = self._items

        # validate if key present
        if key not in _items.keys():
            raise e.validation.NotAllowed(
                msgs=[f"we cannot find key {key} in the smart dict"]
            )

        # wipe internal container
        self._items = {}

        # add the items back
        for _k, _v in _items.items():
            # we use fast add to dict as this was already validated
            self._items[_k] = _v
            # if key matches
            if _k == key:
                for __k, __v in key_values.items():
                    # this will also validate what you add before
                    self[__k] = __v

    def before(self, key: t.Union[int, str]) -> t.Optional[t.Tuple[t.Union[int, str], t.Any]]:
        """
        Returns key and value for before if found else returns None
        """
        # before
        _before = None

        # validate if key present
        if key not in self._items.keys():
            raise e.validation.NotAllowed(
                msgs=[f"we cannot find key {key} in the smart dict"]
            )

        # search
        for _k, _v in self._items.items():
            # if match break
            if key == _k:
                break
            # set _before
            _before = _k, _v

        # return
        return _before

    def after(self, key: t.Union[int, str]) -> t.Optional[t.Tuple[t.Union[int, str], t.Any]]:
        """
        Returns key and value for after if found else returns None
        """
        # before
        _after = None

        # validate if key present
        if key not in self._items.keys():
            raise e.validation.NotAllowed(
                msgs=[f"we cannot find key {key} in the smart dict"]
            )

        # search
        _matched = False
        for _k, _v in self._items.items():
            # set _after if wwas matched
            if _matched:
                _after = _k, _v
                break
            # if matched
            _matched = key == _k

        # return
        return _after


class WatchDogTimer:
    def __init__(
        self,
        watch_for_minutes: int = 0,
        watch_for_seconds: int = 0,
    ):
        self.wait_for = datetime.timedelta(
            seconds=watch_for_minutes * 60 + watch_for_seconds
        )
        self.start = _now()
        self.last_refresh = _now()

    def time_out(self) -> t.Tuple[bool, int, int]:
        _time_delta = _now() - self.last_refresh
        _time_elapsed = _now() - self.start
        _minutes = _time_elapsed.seconds // 60
        _seconds = _time_elapsed.seconds % 60
        if _time_delta > self.wait_for:
            self.last_refresh = _now()
            return True, _minutes, _seconds
        return False, _minutes, _seconds


# noinspection SpellCheckingInspection
class ParallelProcessing:
    """
    https://medium.com/@bfortuner/python-
    multithreading-vs-multiprocessing-73072ce5600b
    """
    ...


# noinspection SpellCheckingInspection
class ParallelThreading:
    """
    https://medium.com/@bfortuner/python-
    multithreading-vs-multiprocessing-73072ce5600b
    """
    ...


class Compare:
    """
    todo: Explore filecmp python module to compare files and folders
    >>> import filecmp
    """
    ...


class StringFmt:
    @classmethod
    def centered_text(
        cls, msg: str = None, total_len: int = 80, fill_char: str = "*"
    ):
        if msg is None:
            msg = ""
        else:
            msg = msg.strip()
            msg = f" {msg} "
        _msg_len = len(msg)
        _left_len = (total_len - _msg_len) // 2
        _right_len = total_len - _msg_len - _left_len
        return f"{fill_char * _left_len}{msg}{fill_char * _right_len}"


def ddict():
    "refer: https://stackoverflow.com/questions/20428636/how-to-convert-defaultdict-to-dict"
    return defaultdict(ddict)


def ddict2dict(d):
    "refer: https://stackoverflow.com/questions/20428636/how-to-convert-defaultdict-to-dict"
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = ddict2dict(v)
    return dict(d)


def camel_case_split(in_str: str) -> t.List[str]:
    """
    Refer
    https://stackoverflow.com/questions/2277352/split-a-string-at-uppercase-letters
    """
    return re.findall('[a-zA-Z][^A-Z]*', in_str)


def rsetattr(obj, attr, val):
    """
    Inspired from
    https://stackoverflow.com/questions/31174295/
    """
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    """
    Inspired from
    https://stackoverflow.com/questions/31174295/
    """
    def _getattr(_obj, _attr):
        return getattr(_obj, _attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def rhasattr(obj, attr):
    _nested_attrs = attr.split(".")
    _curr_obj = obj
    for _a in _nested_attrs[:-1]:
        if hasattr(_curr_obj, _a):
            _curr_obj = getattr(_curr_obj, _a)
        else:
            return False
    return hasattr(_curr_obj, _nested_attrs[-1])


def load_class_from_strs(
    class_name: str, class_module: str
) -> t.Type:
    """
    Given class name and module name as string import the class

    Args:
        class_name: class name
        class_module: module name

    Returns:
        class type

    """
    return getattr(
        importlib.import_module(class_module), class_name
    )


def get_slice_length(_slice: slice, _max_len: int) -> int:
    return len(
        range(
            *_slice.indices(_max_len)
        )
    )


def get_sorted_ordered_dict(
    _dict: dict
) -> t.OrderedDict:
    """
    Creates ordered dict and store values with keys sorted .... provides
    strong guarantee for serialization.
    """
    # container to store data
    _ret = collections.OrderedDict()
    # sort keys for strong guarantee during serialization
    _sorted_keys = list(_dict.keys())
    _sorted_keys.sort()
    # loop over in sorted manner
    for k in _sorted_keys:
        v = _dict[k]
        # note that nested dict if any will become ordered dict
        if isinstance(v, dict):
            v = get_sorted_ordered_dict(v)
        # store in ordered dict
        _ret[k] = v
    # return
    return _ret


def singleton(class_):
    """
    Pros
      Decorators are additive in a way that is often more intuitive than
      multiple inheritance.
    Cons
      While objects created using MyClass() would be true singleton objects,
      MyClass itself is a function, not a class, so you cannot call class
      methods from it. Also for m = MyClass(); n = MyClass(); o = type(n)();
      then m == n && m != o && n != o

    https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    """
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


# noinspection PyPep8Naming
def WipeCacheResult(decorated_fn_name: str, obj_or_module_name):
    # check decorated_fn_name and obj
    ...

    # if obj_or_module_name is str then we assume that decorated function is
    # at module level and not a class method
    if isinstance(obj_or_module_name, str):
        _cache_store_handler_dict = __import__(obj_or_module_name).__dict__
    else:
        _cache_store_handler_dict = obj_or_module_name.__dict__

    # check if CACHE_KEY present
    if CACHE_KEY not in _cache_store_handler_dict.keys():
        raise e.code.CodingError(
            msgs=[
                f"We expect CACHE container from which we want to wipe cache"
            ]
        )

    # get the cached container
    _cache_dict = _cache_store_handler_dict[CACHE_KEY]

    # get the cached key
    _cache_key = decorated_fn_name

    # raise error if cache key not present
    if _cache_key not in _cache_dict.keys():
        raise e.code.CodingError(
            msgs=[
                f"There is no element {_cache_key} cached so we cannot wipe it"
            ]
        )

    # wipe contents
    del _cache_dict[_cache_key]


# noinspection PyPep8Naming
def CacheResult(*dec_args, **dec_kwargs):
    """
    *** NOTE ***

    Note making this as class based decorator is challenging.

    Also making use of descriptor pattern is also challenging as it becomes
    difficult to have properties that are cached. Also note that recursive
    cached method or properties are tedious to cache.

    Hence many open-source library like that from authors of cookiecutter
    tend to use function decorators
    """
    # ---------------------------------------------------------------- 01
    # check if decorator is used appropriately
    # ---------------------------------------------------------------- 01.01
    # kwargs must not be supplied
    if len(dec_kwargs) != 0:
        raise e.code.NotAllowed(
            msgs=[
                f"Do not pass keyword args to CacheResult related decorators ",
                f"Just use it without braces ...",
                f"KwArgs detected {dec_kwargs}"
            ]
        )
    # ---------------------------------------------------------------- 01.02
    # do not use curly braces for decorator
    if len(dec_args) == 0:
        raise e.code.NotAllowed(
            msgs=[
                f"Do not use curly braces for  CacheResult related decorators ",
            ]
        )
    # ---------------------------------------------------------------- 01.03
    # do not pass args to decorator
    if len(dec_args) > 1:
        raise e.code.NotAllowed(
            msgs=[
                f"Do not pass args to decorator CacheResult related "
                f"decorators ",
                f"Just use it without braces ...",
                f"Args detected:",
                dec_args
            ]
        )
    # ---------------------------------------------------------------- 01.04
    # this should be always the case when used decorator with curly braces
    # the thing that i decorated should be a function
    if len(dec_args) == 1:
        e.validation.ShouldBeFunction(
            value=dec_args[0],
            msgs=[
                f"We expect you to use CacheResult related decorators on "
                f"function, instead you have decorated it over {dec_args[0]}"
            ]
        ).raise_if_failed()
    else:
        raise e.code.ShouldNeverHappen(
            msgs=[
                f"Should never happen"
            ]
        )
    # ---------------------------------------------------------------- 01.05
    # the dec function should not be local function
    # but note that it is okay if it is method of local class ...
    #   as in that case it will be "<...>.<locals>.SomeClassName.method"
    if dec_args[0].__qualname__.split(".")[-2] == "<locals>":
        raise e.validation.NotAllowed(
            msgs=[
                f"We do not allow to use CacheResult decorator to be used "
                f"with local functions ... only instance methods and first "
                f"class functions are supported",
                f"Please check {dec_args[0]}"
            ]
        )

    # ---------------------------------------------------------------- 02
    # if all is well then the decorated function is as follows
    _dec_func = dec_args[0]
    # and the cache key is
    _cache_key = _dec_func.__name__
    # hack to detect if method ... note that if local function this will be
    # True but anyways we block that in 01.05 ;)
    _is_method = _dec_func.__qualname__.endswith(f".{_dec_func.__name__}")

    # ---------------------------------------------------------------- 03
    # define wrapper function
    # todo: if used with property replace property with value at runtime for
    #  faster access
    # todo: check if the method on which CacheResult is used is made property
    #  by property decorator
    @functools.wraps(_dec_func)
    def _wrap_func(*args, **kwargs):
        # ------------------------------------------------------------ 03.01
        # some validations
        # kwargs should not be provided
        if bool(kwargs):
            raise e.code.NotAllowed(
                msgs=[
                    f"Please so not supply kwargs while using caching",
                    f"Found kwargs",
                    kwargs
                ]
            )
        # check args provided
        if _is_method:
            if len(args) != 1:
                raise e.code.ShouldNeverHappen(
                    msgs=[
                        f"We detected above that this is method so we expect "
                        f"one arg which is self to be available ..."
                    ]
                )
        else:
            if len(args) != 0:
                raise e.code.NotAllowed(
                    msgs=[
                        f"Please do not supply args to function decorated "
                        f"with CacheResult",
                        f"Found args", args,
                    ]
                )
        # if one arg is provided it will be self (i.e the dec function is
        # defined within class)
        if _is_method:
            # todo: check if args[0] is python object i.e. the decorated
            #  function will cache things inside this instance ...
            ...

        # ------------------------------------------------------------ 03.02
        # get dict in which we will add cache container
        if _is_method:
            _cache_store_handler_dict = args[0].__dict__
        else:
            _cache_store_handler_dict = __import__(
                _dec_func.__module__
            ).__dict__
        # add cache container if not present
        if CACHE_KEY in _cache_store_handler_dict.keys():
            _cache_store = _cache_store_handler_dict[
                CACHE_KEY
            ]  # type: dict
        else:
            _cache_store = {}
            _cache_store_handler_dict[CACHE_KEY] = _cache_store

        # ------------------------------------------------------------ 03.03
        # if _cache_key not present set it by return value of _dec_fn
        # NOTE: as smart dict for cache cannot be freezed we use
        # `_cache_store._dict` so that we can bypass freeze checks ;)
        # noinspection PyProtectedMember
        if _cache_key not in _cache_store.keys():
            # compute as key not present with results
            _res = _dec_func(*args, **kwargs)

            # add the results to dict
            # Note that we did not use `_cache_store._dict` as the cache dict
            # will never be freezed ... so writing to it will always be allowed
            _cache_store[_cache_key] = _res

        # return
        # noinspection PyProtectedMember
        return _cache_store[_cache_key]

    # ---------------------------------------------------------------- 04
    # add a tag to detect if decorator was used
    _wrap_func._pk_cached = True

    # ---------------------------------------------------------------- 05
    # return wrapped function
    return _wrap_func


def is_cached(property_or_fn) -> bool:
    if inspect.ismethod(property_or_fn) or inspect.isfunction(property_or_fn):
        return hasattr(property_or_fn, '_pk_cached')
    elif isinstance(property_or_fn, property):
        return hasattr(property_or_fn.fget, '_pk_cached')
    elif isinstance(property_or_fn, HookUp):
        return hasattr(property_or_fn.method, '_pk_cached')
    else:
        raise e.code.ShouldNeverHappen(
            msgs=[
                f"unknown type {type(property_or_fn)}"
            ]
        )


def break_list_in_chunks(
    list_of_items: t.List[t.Any], num_of_chunks: int
) -> t.List[t.List[t.Any]]:
    # Create a function called "chunks" with two arguments, l and n:
    def chunk_it(ll, n):
        _total_len = len(ll)
        _len_of_chunk = _total_len // n
        _remain_len = _total_len % n
        _chunk_lens = [
            _len_of_chunk + 1 if i < _remain_len else _len_of_chunk
            for i in range(n)]

        cnt = 0
        for cl in _chunk_lens:
            yield ll[cnt: cnt + cl]
            cnt += cl

    return list(chunk_it(list_of_items, num_of_chunks))


# def compute_weights_from_labels(_labels: np.ndarray) -> np.ndarray:
#     _unique_labels = np.sort(np.unique(_labels))
#     _unique_labels_weight = sklearn.utils.compute_class_weight(
#         'balanced', _unique_labels, _labels)
#     _dict_weights = dict(zip(_unique_labels, _unique_labels_weight))
#     return np.asarray(
#         [_dict_weights[l] for l in _labels],
#         dtype=np.float32
#     )


def fetch_non_dunder_attributes(cls):
    return [
        (a, getattr(cls, a)) for a in dir(cls)
        if not (a.startswith("__") and a.endswith("__"))
    ]


def return_argument_as_it_is(t):
    return t


def get_object_memory_usage(obj) -> int:
    """sum size of object & members."""
    # print(".......... DEBUG .........")
    # noinspection PyPep8Naming
    BLACKLIST = (type, types.ModuleType, types.FunctionType)
    e.validation.ShouldNotBeOneOf(
        value=obj, values=BLACKLIST,
        msgs=[
            f"Object of type {type(obj)} is not allowed ..."
        ]
    ).raise_if_failed()
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            # noinspection PyTypeChecker
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                # todo: debug in future
                # if isinstance(obj, dict):
                #     print(obj.keys())
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = gc.get_referents(*need_referents)
    return size


def _generate_descriptors_for_group_tasks(
    _items: t.Dict[str, t.Any]
) -> t.Dict[str, str]:

    _num_items = len(_items)
    _max_key_len = max([len(_) for _ in _items.keys()])
    _descriptors = {
        _: f"{i+1:0{len(str(_num_items))}d}/{_num_items} > {_}"
        for i, _ in enumerate(_items.keys())
    }
    _max_desc_len = max([len(_) for _ in _descriptors.values()])
    _descriptors = {
        k: v.ljust(_max_desc_len, ' ')
        for k, v in _descriptors.items()
    }
    return _descriptors


def pathlib_rmtree(
    path: pathlib.Path,
    recursive: bool,
    force: bool,
) -> bool:
    """
    Deletes folder

    Args:
        path:
          path of dir
        recursive:
          if True recursively deletes the dir or else only delete
          files in dir
        force:
          some files like *.info and datasets are made read only and locked
          so that they cannot be deleted by program ... this flag will force
          delete them

    Returns:
        True if success else raises error

    """
    if not path.is_dir():
        raise e.code.NotAllowed(
            msgs=[
                f"We need a directory.",
                f"Please check path {path}"
            ]
        )
    for f in path.iterdir():
        if f.is_dir():
            if recursive:
                pathlib_rmtree(f, recursive, force)
            else:
                raise e.code.NotAllowed(
                    msgs=[
                        f"You have opted for non recursive folder delete "
                        f"hence cannot delete sub folder ..."
                    ]
                )
            # f.rmdir()
        if f.is_file():
            try:
                f.unlink()
            except PermissionError:
                if force:
                    io_make_path_editable(f)
                    f.unlink()
                else:
                    raise e.code.CodingError(
                        msgs=[
                            f"You do not have permission to delete file "
                            f"`{f}`",
                            f"Make sure you get permissions on files to delete "
                            f"before deleting them."
                        ]
                    )
    path.rmdir()
    return True


def save_pickle(py_obj, file_path: pathlib.Path):
    # raise error if needed
    e.io.FileMustNotBeOnDiskOrNetwork(
        path=file_path, msgs=[]
    ).raise_if_failed()
    # save
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open(mode='wb') as _f:
        pickle.dump(py_obj, _f)


def read_pickle(file_path: pathlib.Path):
    # raise error if needed
    e.io.FileMustBeOnDiskOrNetwork(
        path=file_path, msgs=[]
    ).raise_if_failed()
    # save
    with file_path.open(mode='rb') as _f:
        return pickle.load(_f)


def print_file_mod(file: pathlib.Path):
    print(stat.filemode(file.stat().st_mode))


def extract_files_in_memory(
    archive_file_path: pathlib.Path,
    members: t.Union[t.List[str], None] = None,
) -> t.Dict:

    archive = zipfile.ZipFile(archive_file_path, 'r')
    if members is None:
        _ms = archive.namelist()
    else:
        _ms = members

    return {
        k: archive.read(k) for k in _ms
    }


def extract_file(
    archive_file_path: pathlib.Path,
    extract_dir: pathlib.Path,
    members: t.Union[t.List[str], None] = None,
):
    # print(
    #     f"\n"
    #     f"Extracting file {archive_file_path} to {extract_dir}"
    # )

    archive = zipfile.ZipFile(archive_file_path, 'r')
    if members is None:
        _ms = archive.namelist()
    else:
        _ms = members

    for _zip_info in _ms:
        # print(f"\t ~~ extracting member: {_zip_info}")
        # noinspection PyTypeChecker
        archive.extract(_zip_info, extract_dir)
    archive.close()


def io_move():
    """
    todo: os.replace looks like is the fastest
    """
    ...


def io_make_path_read_only(path: pathlib.Path):
    if path.is_file() or path.is_dir():
        path.chmod(_FILE_READ_MODE)
    else:
        raise e.code.NotAllowed(
            msgs=[
                f"Path {path} is not a file/dir or does not exist ..."
            ]
        )


def io_make_path_editable(path: pathlib.Path):
    if path.is_file() or path.is_dir():
        path.chmod(_FILE_WRITE_MODE)
    else:
        raise e.code.NotAllowed(
            msgs=[
                f"Path {path} is not a file/dir or does not exist ..."
            ]
        )


def io_path_delete(path: pathlib.Path, force: bool):
    if path.is_file():
        try:
            # todo check if we can make files that cannot be deleted and then
            #  only can be deleted from here
            path.unlink()
        except PermissionError:
            if force:
                # in case of permission error try to make it editable before
                # deleting
                io_make_path_editable(path)
                path.unlink()
            else:
                raise e.code.CodingError(
                    msgs=[
                        f"You do not have permission to delete file "
                        f"`{path}`",
                        f"Make sure you get permissions on files to delete "
                        f"before deleting them."
                    ]
                )
    elif path.is_dir():
        pathlib_rmtree(path, recursive=True, force=force)
    else:
        raise e.code.NotAllowed(
            msgs=[
                f"Path {path} is not a file/path or does not exist ..."
            ]
        )


def io_is_dir_empty(_dir: pathlib.Path) -> bool:
    # checks
    if not _dir.exists():
        raise e.code.NotAllowed(
            msgs=[
                f"Directory {_dir} does not exist on the disk"
            ]
        )
    if not _dir.is_dir():
        raise e.code.NotAllowed(
            msgs=[
                f"Path {_dir} is not a directory"
            ]
        )

    # logic
    _is_empty = True
    for _ in _dir.iterdir():
        _is_empty = False
        break

    # return
    return _is_empty


def find_free_port():
    """
    Inspired from
    https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    """
    with contextlib.closing(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ) as _socket:
        _socket.bind(('', 0))
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return _socket.getsockname()[1]


def npy_load(file: "s.Path", memmap: bool = False) -> np.ndarray:
    if memmap:
        # todo: doesn't support s.Path make it compatible and also see if npy_save methods
        #  also work although they allow s.Path
        # noinspection PyTypeChecker
        _ret = np.load(file.local_path, mmap_mode="r", allow_pickle=False, fix_imports=False)
    else:
        with file.open(mode='rb') as f:
            _ret = np.load(f, allow_pickle=False, fix_imports=False)
            f.close()
    return _ret


def npy_array_save(file: "s.Path", npy_array: np.ndarray):
    # only supported type is np.ndarray
    e.validation.ShouldBeInstanceOf(
        value=npy_array,
        value_types=(np.ndarray,),
        msgs=[
            f"Only numpy arrays are allowed to be saved"
        ]
    ).raise_if_failed()

    # if npy_array is structured raise error
    if npy_array.dtype.names is not None:
        raise e.code.NotAllowed(
            msgs=[
                f"The data type of numpy array is not a "
                f"builtin, found {npy_array.dtype}",
                f"We cannot save numpy record."
            ]
        )

    # save numpy record file
    with file.open(mode='wb') as f:
        np.save(f, npy_array, allow_pickle=False, fix_imports=False)
        f.close()


def npy_record_save(
    file: "s.Path", npy_record_dict: t.Dict[str, np.ndarray]
):
    """
    todo: migrate to `np.core.records.fromarrays` if needed
     ... maybe do not do this as we get more elaborate errors in our
         implementation
    There is already a method that does the same job:
      r = np.core.records.fromarrays([x1,x2,x3],names='a,b,c')
    """
    # ---------------------------------------------------------------01
    # do some validations
    e.validation.ShouldBeInstanceOf(
        value=npy_record_dict, value_types=(dict,),
        msgs=[
            f"Was expecting dictionary of numpy arrays"
        ]
    ).raise_if_failed()
    _len = None
    for k, v in npy_record_dict.items():
        # key should be str
        if not isinstance(k, str):
            raise e.code.NotAllowed(
                msgs=[
                    f"The dictionary keys should be str found type {type(k)}"
                ]
            )
        # only supported type is np.ndarray
        if not isinstance(v, np.ndarray):
            raise e.code.NotAllowed(
                msgs=[
                    f"Only numpy arrays are allowed to be saved within "
                    f"numpy record",
                    f"Found unsupported type {type(v)}"
                ]
            )

        # check if builtin i.e. not a numpy record
        if v.dtype.isbuiltin == 0:
            raise e.code.NotAllowed(
                msgs=[
                    f"The data type of numpy array for key {k!r} is not a "
                    f"builtin, found {v.dtype}",
                    f"We cannot save numpy record within numpy record"
                ]
            )

        # get len of first element
        if _len is None:
            _len = v.shape[0]

        # check if len is same for all elements
        if v.shape[0] != _len:
            raise e.code.NotAllowed(
                msgs=[
                    f"While creating numpy struct all arrays must have "
                    f"same length.",
                    f"Found invalid shape {v.shape} for item {k}"
                ]
            )

    # ---------------------------------------------------------------02
    # sort the keys
    _sorted_keys = list(npy_record_dict.keys())
    _sorted_keys.sort()

    # create numpy record buffer
    npy_record = np.zeros(
        _len,
        dtype=[
            (k, npy_record_dict[k].dtype, npy_record_dict[k].shape[1:])
            for k in _sorted_keys
        ],
    )

    # ---------------------------------------------------------------03
    # fill up the elements
    for k in _sorted_keys:
        npy_record[k] = npy_record_dict[k]

    # ---------------------------------------------------------------04
    # save numpy record file
    with file.open(mode='wb') as f:
        np.save(f, npy_record, allow_pickle=False, fix_imports=False)
        f.close()


class HookUp:
    """
    A class which will replace the hooked up method.

    todo: Check contextlib
      + https://docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
      + looks like this library will more use cases and we need to explore it

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

    Check try_hook_instance_method below for usage.
    We have a special protocol for method, pre_method and post_method.
    Can we define it via some protocol.

    Note:
        todo: can we enforce method signature check
        + method and pre_method should have same input arguments
        + pre_method should return nothing
        + method and post_method should have same return arguments
        + post_method should have same input keyword argument
          hooked_method_return_value with type as return argument of post_method
          i.e. also same as method return argument

    """
    def __init__(
        self,
        *,
        cls: t.Type,
        method: t.Callable,
        pre_method: t.Optional[t.Callable] = None,
        post_method: t.Optional[t.Callable] = None,
    ):
        # if method is HookUp instance that means the parent class of cls has
        # already hooked itself up and there is no overridden method in this
        # subclass for the same method ... so we need to define new hookup
        # and grab post and pre runners specific to this class
        # So if HookUp we grab method from it and create a new hook up here
        # Note: the HookUp class from parent becomes useless and is replaced
        #   by new HookUp for child class
        # Note: the args pre_method and post_method are the latest one i.e. from
        #   child class ... so no need for `method.pre_method` and `method.post_method`
        if isinstance(method, HookUp):
            # noinspection PyUnresolvedReferences
            method = method.method

        # save variables in self
        self.cls = cls
        self.method = method
        self.pre_method = pre_method
        self.post_method = post_method

        # assign self i.e. HookUp instance in cls
        # Note we do not do `cls.method = self` as that overrides parents HookUp
        # cls.__dict__[method.__name__] = self
        setattr(cls, method.__name__, self)

    def __repr__(self):
        return f"HookUp for {self.cls.__module__}.{self.cls.__name__}: (" \
               f"{self.pre_method.__qualname__}, " \
               f"{self.method.__qualname__}, " \
               f"{self.post_method.__qualname__}" \
               f")"

    def __get__(self, method_self, method_self_type):
        """
        This makes use of description pattern ... now we have access to method's
        self so that we can use it in __call__
        """
        self.method_self = method_self
        return self

    def __eq__(self, other):
        """
        Two hookups are same if method they represent is same ...

        Why this behaviour:
          HookUp instance replaces method but a child class can have
          different pre and post runners but not the different method in that
          we create new HookUp instance and borrow method from parent HookUp.
          So although the hookup instances are different both child and parent
          share same method. So this is justified in this context.

        Useful in rules.py
          We can check if method is overridden or not even if we use ne hookup
          for child class that does not override method
        """
        return self.method == other.method

    def __call__(self, *args, **kwargs):

        # -----------------------------------------------------------01
        # although might not be necessary ... we enforce
        if bool(args):
            raise e.code.CodingError(
                msgs=[
                    f"Please avoid methods that use args ... while using "
                    f"hook up ..."
                ]
            )
        # get default kwargs if not supplied ...
        # so that pre- and post-method gets the default kwargs
        for _k, _p in inspect.signature(self.method).parameters.items():
            if _k not in kwargs.keys():
                # noinspection PyUnresolvedReferences,PyProtectedMember
                if _p.default != inspect._empty:
                    kwargs[_k] = _p.default

        # -----------------------------------------------------------02
        # bake title
        # _kwargs_str = []
        # for k, v in kwargs.items():
        #     if isinstance(v, list):
        #         if len(v) == 1 or len(v) == 2:
        #             v = f"{v}"
        #         else:
        #             v = f"[{v[0]}, ..., {v[-1]}]"
        #     _kwargs_str.append(
        #         f"{k}={v}"
        #     )
        # _kwargs_str = ", ".join(_kwargs_str)
        if bool(kwargs):
            _kwargs_str = "..."
        else:
            _kwargs_str = ""
        # todo: with gui build {self.method_self.name} poses problem find a
        #  way to avoid logs while building GUI
        # _title = f"<{self.method_self.name}> {self.cls.__name__}." \
        _title = f"{self.cls.__name__}." \
                 f"{self.method.__name__}" \
                 f"({_kwargs_str})"
        # _title = logger.replace_with_emoji(_title)

        # -----------------------------------------------------------03
        # call business logic
        # -----------------------------------------------------------03.01
        # call pre_method is provided
        if self.pre_method is not None:
            _pre_ret = self.pre_method(self.method_self, **kwargs)
            # pre_method should not return anything
            if _pre_ret is not None:
                raise e.code.CodingError(
                    msgs=[
                        f"{HookUp} protocol enforces the "
                        f"pre_method {self.pre_method} of method "
                        f"{self.method} to "
                        f"not return anything ...",
                        f"Found return value {_pre_ret}"
                    ]
                )
        # -----------------------------------------------------------03.03
        # call actual method
        _ret = self.method(self.method_self, **kwargs)
        # -----------------------------------------------------------03.04
        # if post_method not provided return what we have
        if self.post_method is not None:
            # call post_method as it is provided
            # spinner.info(msg=f"pre: {pre_method}")
            # spinner.info(msg=f"{method}")
            # spinner.info(msg=f"post: {post_method}")
            _post_ret = self.post_method(
                self.method_self, hooked_method_return_value=_ret, **kwargs)
            # post_method should not return anything
            if _post_ret is not None:
                raise e.code.CodingError(
                    msgs=[
                        f"{HookUp} protocol enforces the "
                        f"post_method {self.post_method} of method"
                        f" {self.method} to "
                        f"not return anything ...",
                        f"Found return value {_post_ret}"
                    ]
                )

        # -----------------------------------------------------------04
        # return the return value of method
        return _ret


def import_from_str(
    module: str, name: str
) -> t.Any:
    try:
        return getattr(
            __import__(module, fromlist=[name]), name
        )
    except ModuleNotFoundError:
        raise e.code.CodingError(
            msgs=[
                f"Module {module!r} cannot be imported ..."
            ]
        )
    except ImportError:
        raise e.code.CodingError(
            msgs=[
                f"Cannot find name {name!r} in module {module!r} ..."
            ]
        )


def try_hook_instance_method():
    @dataclasses.dataclass
    class A(abc.ABC):

        def __init_subclass__(cls, **kwargs):
            HookUp(
                cls=cls,
                silent=True,
                method=cls.g,
                pre_method=cls.g_pre,
                post_method=cls.g_post,
            )

        # noinspection PyMethodMayBeStatic
        def g_pre(self):
            print("g_pre")

        @abc.abstractmethod
        def g(self) -> int:
            ...

        # noinspection PyMethodMayBeStatic
        def g_post(self, hooked_method_return_value) -> int:
            print("g_post")
            return hooked_method_return_value

    @dataclasses.dataclass
    class B(A):
        c: int

        def g(self) -> int:
            print("g", self.c)
            return 22

    b = B(44)
    print(b.g())


def compute_class_weights(
    _labels: np.ndarray
) -> t.Tuple[np.ndarray, np.ndarray]:
    ...
    # _unique_labels = np.sort(np.unique(_labels))
    # _unique_labels_weight = sklearn.utils.compute_class_
    #
    # weight(
    #     'balanced', _unique_labels, _labels)
    # return _unique_labels, _unique_labels_weight


def shuffle_arrays(
    arrays: t.List[np.ndarray],
    set_seed: int = -1,
):
    """
    Refer to: https://stackoverflow.com/questions/4601373

    Shuffles arrays in-place, in the same order, along axis=0

    Parameters:
    -----------
    arrays : List of NumPy arrays.
    set_seed : Seed value if int >= 0, else seed is random.
    """
    assert all(len(arr) == len(arrays[0]) for arr in arrays)
    seed = np.random.randint(0, 2**(32 - 1) - 1) if set_seed < 0 else set_seed

    for arr in arrays:
        rstate = np.random.RandomState(seed)
        rstate.shuffle(arr)
    # reset the state
    np.random.seed(None)


def np_to_lnp(data: np.ndarray) -> t.List:
    """
    Convert any n-dim array to nested list of lists of 1D array
    """

    def _make_list(_data):
        if _data.ndim == 1:
            return _data
        else:
            return [_make_list(_) for _ in _data]

    return _make_list(_data=data)


def np_to_pa(data: np.ndarray) -> pa.Array:
    """
    Unit test code

    a = np.zeros((2, 3, 4, 5), dtype=np.uint8)
    pa_a = util.np_to_pa(a)
    _a = util.pa_to_np(pa_a)
    print(a.shape, a.dtype)
    print(_a.shape, _a.dtype)
    """
    return pa.array(np_to_lnp(data=data))


def pa_to_np(
    data: t.Union[pa.Array, pa.ChunkedArray, pa.ListArray]
) -> np.ndarray:
    """
    Unit test code

    a = np.zeros((2, 3, 4, 5), dtype=np.uint8)
    pa_a = util.np_to_pa(a)
    _a = util.pa_to_np(pa_a)
    print(a.shape, a.dtype)
    print(_a.shape, _a.dtype)
    """
    if isinstance(data, pa.Array):
        data = data.to_numpy(zero_copy_only=False)
    elif isinstance(data, pa.ChunkedArray):
        data = data.to_numpy()
    elif isinstance(data, pa.ListArray):
        return np.asarray(data)
    else:
        raise e.code.CodingError(
            msgs=[
                f"Expected {pa.Array} or {pa.ChunkedArray} but found "
                f"{type(data)}"
            ]
        )

    def _make_list(_data):
        if _data.dtype != object:
            return _data
        else:
            return [_make_list(_) for _ in _data]

    # noinspection PyTypeChecker
    return np.asarray(_make_list(_data=data))


def one_hot_to_simple_labels(oh_label: pd.Series) -> pd.Series:
    _label_oh = np.vstack(oh_label)
    _label = np.argmax(_label_oh, axis=1)
    return pd.Series(_label)
    # return prefix_str + pd.Series(_label).astype(str).str.zfill(3)

#
# def parse_tensor_for_pandas_column(t: tf.Tensor):
#     e.validation.ShouldBeInstanceOf(
#         value=t, value_types=(tf.Tensor,),
#         msgs=[
#             f"We expect you to pass a tensor instead found {type(t)}"
#         ]
#     ).raise_if_failed()
#
#     npy_value = t.numpy()
#
#     if isinstance(npy_value, np.ndarray):
#
#         if npy_value.ndim == 2 or npy_value.ndim == 1:
#             return [v for v in npy_value]
#         else:
#             raise e.code.NotAllowed(
#                 msgs=[
#                     f"The tensors numpy() value has ndim=={npy_value.ndim}",
#                     f"Only allowed dimension is ndim==2",
#                 ]
#             )
#     elif isinstance(npy_value, np.uint8):
#         # this will be then a single
#         return npy_value
#     else:
#
#         raise e.code.NotAllowed(
#             msgs=[
#                 f"The tensor numpy() is unsupported.",
#                 f"The type is {type(npy_value)} and value is {npy_value}"
#             ]
#         )


_changer_methods = set(
    "__setitem__ __setslice__ __delitem__ update append extend add insert "
    "pop popitem remove setdefault __iadd__".split()
)


def _proxy_decorator(func, callback):
    def wrapper(*args, **kw):
        _res = func(*args, **kw)
        callback()
        return _res
    wrapper.__name__ = func.__name__
    return wrapper


def notifying_list_dict_class_factory(cls, callback):
    """
    Inspired from
    https://stackoverflow.com/questions/9871169
    """
    new_dct = cls.__dict__.copy()
    for key, value in new_dct.items():
        if key in _changer_methods:
            new_dct[key] = _proxy_decorator(
                value, callback
            )
    return type("proxy_" + cls.__name__, (cls,), new_dct)


class WaitAndUpdate:
    """
    Simple class to wait and update
    todo: figure out use of threading.Event
      https://stackoverflow.com/questions/29082268/python-time-sleep-vs-event-wait
      Also check an implementation from tich library for Progress
      >>> import rich.progress
      >>> rich.progress.Progress.track
      >>> rich.progress._TrackThread
    """
    def __init__(self, period: float):
        self.period = period
        self._time = _now()

    def can_update(self) -> bool:
        _current_time = _now()
        _elapsed_secs = (_current_time - self._time).total_seconds()
        if _elapsed_secs > self.period:
            self._time = _current_time
            return True
        else:
            return False


# noinspection PyProtectedMember
@dataclasses.dataclass
class Process:
    """
    todo: update to grpc.io in future ... needs lot of thinking ....
        https://grpc.io/docs/tutorials/basic/python/
        https://www.semantics3.com/blog/a-simplified-guide-to-grpc-in-
        python-6c4e25f0c506/
        We are using multiprocessing.Process for now as it is simple but we
        lose the logging part for validation callback ....
        But nonetheless we might not use console in future for logging and
        hence UI client can log the info from different processes :)

    todo:
        Also explore if async-io of python can be used alongside grpc-io
        https://docs.python.org/3/library/asyncio-eventloop.html#event-loop
        The event loop is the core of every asyncio application.
        - Event loops run asynchronous tasks and
        - Callbacks, perform network IO operations, and run subprocesses.
    """

    class SIGNAL:
        _start = "_start"
        _started = "_started"
        _close = "_close"
        _closed = "_closed"
        _kill = "+kill"
        _killed = "_killed"
        _exception = "_exception"
        _exception_ack = "_exception_ack"

    name: str
    _child_connector: "mp.connection.Connection" = dataclasses.field(init=False)
    _error_log_file: pathlib.Path = dataclasses.field(init=False)

    _RUNNING_PROCESSES = []

    @property
    @CacheResult
    def supported_signals(self) -> t.List[str]:
        # fetch signal names
        _ret_list = [
            s for s in self.SIGNAL.__dict__.keys() if not s.startswith("_")
        ]
        # if not overriden this should be empty
        if self.SIGNAL == Process.SIGNAL:
            if bool(_ret_list):
                raise e.code.CodingError(
                    msgs=[
                        f"Class {Process.SIGNAL} is not overriden in"
                        f" {self.__class__} so we expect that there is no "
                        f"signal to use."
                    ]
                )
        # return
        return _ret_list

    @property
    @CacheResult
    def _pipe(self) -> mp.Pipe:
        return mp.Pipe(duplex=True)

    @property
    @CacheResult
    def _main_connector(self) -> "mp.connection.Connection":
        return self._pipe[0]

    @property
    @CacheResult
    def _process(self) -> mp.Process:

        return mp.Process(
            name=self.name,
            target=self._process_fn_wrap,
            # kwargs={
            #     "self": _mock_process
            # },
            daemon=False,  # we will handle killing
        )

    def __post_init__(self):
        # as this will serve as argument to parallel process function ... we
        # need to be a dataclass field
        self._child_connector = self._pipe[1]

        # error log file
        _DIR = logger.MULTIPROCESSING_LOG_DIR
        if not _DIR.is_dir():
            _DIR.mkdir(exist_ok=True, parents=True)
        _FILE = _DIR / f"{self.name}.logs"
        if _FILE.is_file():
            raise e.code.CodingError(
                msgs=[
                    f"There should ideally no file {_FILE} on disk",
                    f"Whenever an exception occurs in a thread an error log "
                    f"file will be created in child process and while in main "
                    f"thread it will be read and deleted"
                ]
            )
        self._error_log_file = _FILE

        # check if process with same name exists
        if self.name in self._RUNNING_PROCESSES:
            raise e.code.CodingError(
                msgs=[
                    f"The process with name {self.name!r} is already running"
                ]
            )

        # check if fn is overriden
        if self.__class__.process_fn == Process.process_fn:
            raise e.code.CodingError(
                msgs=[
                    f"You need to override method `fn` which will "
                    f"execute the parallel process code",
                    f"NOTE: ",
                    f"When you override always favour to use python "
                    f"exceptions instead of error.* exceptions"
                ]
            )

    def _register(self):
        # check if process with same name exists
        if self.name in self._RUNNING_PROCESSES:
            raise e.code.CodingError(
                msgs=[
                    f"Cannot register process with name {self.name!r}"
                ]
            )
        else:
            self._RUNNING_PROCESSES.append(self.name)

    def _unregister(self):
        # check if process with same name exists
        if self.name not in self._RUNNING_PROCESSES:
            raise e.code.CodingError(
                msgs=[
                    f"Cannot unregister process with name {self.name!r}"
                ]
            )
        else:
            self._RUNNING_PROCESSES.remove(self.name)

    def _process_fn_wrap(self):
        # --------------------------------------------------------------- 01
        # the first signal to be received should be start
        _recv_signal = self._child_connector.recv()
        # noinspection PyProtectedMember
        if _recv_signal == Process.SIGNAL._start:
            # noinspection PyProtectedMember
            self._child_connector.send(Process.SIGNAL._started)
        else:
            # noinspection PyProtectedMember
            raise e.code.CodingError(
                msgs=[
                    f"While using process the first signal needs to be to "
                    f"{Process.SIGNAL._start}",
                    f"Instead found {_recv_signal}"
                ]
            )

        # --------------------------------------------------------------- 02
        # an infinite loop to get many more signals
        while True:

            # ----------------------------------------------------------- 02.01
            # get signal
            _recv_signal = self._child_connector.recv()

            # ----------------------------------------------------------- 02.02
            # if signal is close break
            # noinspection PyProtectedMember
            if _recv_signal == Process.SIGNAL._close:
                # noinspection PyProtectedMember
                self._child_connector.send(Process.SIGNAL._closed)
                break

            # ----------------------------------------------------------- 02.03
            # Now that we are here that means the _recv_signal must be one of
            # supported signals
            if _recv_signal not in self.supported_signals:
                raise e.code.CodingError(
                    msgs=[
                        f"Signal {_recv_signal} is unrecognized",
                        f"Note that it should not be one of internal signals"
                    ]
                )

            # ----------------------------------------------------------- 02.04
            # call the process fn
            # noinspection PyBroadException
            try:
                # noinspection PyArgumentList
                self.process_fn(_recv_signal)
            except Exception as _e:
                # write error message to file
                _err_msg = ""
                if self._error_log_file.is_file():
                    _err_msg += f"The error log file should not exist on " \
                                f"disk. \n We will overwrite. \n\n"
                _err_msg += f"{traceback.format_exc()} \n" \
                            f"-----------------------------------------------" \
                            f"\n"
                _err_msg += f"There was an exception as above and now we " \
                            f"will wait for signal " \
                            f"Process._SIGNAL.exception_ack from main " \
                            f"thread.\n" \
                            f"-----------------------------------------------" \
                            f"\n" \
                            f"Meanwhile if we received any other signals " \
                            f"they are as logged below.\n\n"
                self._error_log_file.touch(exist_ok=True)
                self._error_log_file.write_text(_err_msg)

                # inform main thread about exception in process
                self._child_connector.send(Process.SIGNAL._exception)

                # now that exception have occurred hold the process infinitely
                # until the main process responds with ack
                i = 0
                while True:
                    i += 1
                    _recv_signal_1 = self._child_connector.recv()
                    if _recv_signal_1 == Process.SIGNAL._exception_ack:
                        break
                    else:
                        # some other message was received so lot that for reader
                        with self._error_log_file.open("a") as f:
                            f.write(
                                f" . Received signal [{i:04d}]: "
                                f" {_recv_signal_1!r} "
                                f"at time {_now()}\n"
                            )

                # final break as we received proper ack from main thread
                break

    @staticmethod
    @atexit.register
    def _at_exit_clean_up():
        # checking for any child processes and sending kill signal
        _processes = mp.active_children()
        if bool(_processes):
            _LOGGER.warning(
                msg=f"************ Found Some Zombie Processes ***************")
            _LOGGER.warning(
                msg=f">>>> TODO: If possible address the zombie processes <<<<")
            for p in _processes:
                _LOGGER.warning(msg=f"- Killing child process {p}")
                p.kill()
                p.join()
                p.close()

            _LOGGER.warning(
                msg=f"************ *************************** ***************")

    # noinspection PyMethodMayBeStatic
    def process_fn(self, signal: str):
        # todo: ... do we need to check this thing ... i.e. preferring python
        #  or our own custom exceptions (i.e. error.*)

        # NOTE: that using our exceptions will raise system exit and
        # hence parallel child processes will not be killed .... here we
        # still use it to serve as reminder .... do not raise custom
        # exceptions from error module ... only use python exceptions instead
        raise e.code.CodingError(
            msgs=[
                f"You need to override method `fn` which will "
                f"execute the parallel process code",
                f"NOTE: ",
                f"When you override always favour to use python "
                f"exceptions instead of error.* exceptions"
            ]
        )

    def process_start(self):
        # ---------------------------------------------------------------- 01
        # start the process thread
        self._process.start()

        # ---------------------------------------------------------------- 02
        # signal it to start
        self._main_connector.send(self.SIGNAL._start)

        # ---------------------------------------------------------------- 03
        # wait for ack
        _received_message = self._main_connector.recv()

        # ---------------------------------------------------------------- 04
        # confirm if received message is correct
        if _received_message != self.SIGNAL._started:
            raise e.code.CodingError(
                msgs=[
                    f"Should receive a message "
                    f"{self.SIGNAL._started} instead received"
                    f"{_received_message}"
                ]
            )

        # ---------------------------------------------------------------- 05
        # register
        self._register()

        # ---------------------------------------------------------------- 06
        # log ...
        _LOGGER.info(
            msg=f"Started parallel process {self.name!r} ..."
        )

    def process_close(self):

        # ---------------------------------------------------------------- 01
        # signal process to close
        self._main_connector.send(self.SIGNAL._close)

        # ---------------------------------------------------------------- 02
        # wait for ack
        _received_message = self._main_connector.recv()

        # ---------------------------------------------------------------- 03
        # if the child process has led to exception it will have already sent
        # exception signal .... and will be in no position to accept anymore
        # signals and will be simple waiting for signal exception_ack
        if _received_message == self.SIGNAL._exception:
            # send child thread the ack so that it can exit
            self._main_connector.send(self.SIGNAL._exception_ack)
            # the exception handling must have
            # created and written log ... so read it in string
            _error_log = self._error_log_file.read_text().split("\n")
            # remove log file as it is temporary
            self._error_log_file.unlink()  # mandatory
            # join and close child process
            self._process.join()
            self._process.close()
            raise e.code.CodingError(
                msgs=[
                    ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                    f"Parallel process {self.name!r} has crashed",
                    f"The traceback from the child process is as follows:",
                    ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                    *_error_log,
                    ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                ]
            )

        # ---------------------------------------------------------------- 04
        # if there was no exception then simple we expect response as closed
        # signal for our close request
        # confirm if received message is correct
        if _received_message != self.SIGNAL._closed:
            raise e.code.CodingError(
                msgs=[
                    f"Should receive a message "
                    f"{self.SIGNAL._closed} instead received "
                    f"{_received_message}"
                ]
            )
        # things are as expected so close things
        else:
            # just for safety join as after broadcasting message "close" it
            # might not have much time to exit ... hence wait :)
            self._process.join()
            # more safety close the process
            self._process.close()

        # ---------------------------------------------------------------- 05
        # unregister
        self._unregister()

        # ---------------------------------------------------------------- 06
        # log ...
        _LOGGER.info(
            msg=f"Closed parallel process {self.name!r} ..."
        )

    def process_send_signal(self, signal: str):

        # ---------------------------------------------------------------- 01
        # some verification
        if signal not in self.supported_signals:
            raise e.code.CodingError(
                msgs=[
                    f"Provided signal {signal!r} is not supported by you",
                    f"Allowed signals are:",
                    self.supported_signals
                ]
            )

        # ---------------------------------------------------------------- 02
        # signal it to terminate
        self._main_connector.send(signal)

        # ---------------------------------------------------------------- xx
        # note we do not wait for ack as this will cause main thread to wait

    # noinspection PyArgumentList
    @staticmethod
    def test():

        p = _TryProcess()

        p.process_start()

        p.process_send_signal("xyz")
        # p.do_it(signal="fff")

        p.process_close()


@dataclasses.dataclass
class _TryProcess(Process):
    xx: int = 5

    @property
    def supported_signals(self) -> t.List[str]:
        return ["xyz"]

    def process_fn(self, signal: str):
        # raise Exception()
        time.sleep(5)
        if signal == "xyz":
            print(signal)
        else:
            raise Exception("Error")


class TestUtil:
    # noinspection PyPep8Naming
    @staticmethod
    def try_CacheResult():
        class B:
            ...

        class A:

            @property
            @CacheResult
            def p(self) -> "B":
                # noinspection PyTypeChecker
                return None  # as we are using setter and there
                # is util.CacheResult

        a = A()
        # a.p = 1

        print(a.p)
