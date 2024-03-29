"""
todo: check validators library
      https://validators.readthedocs.io/en/latest/
"""
import dataclasses
import inspect
import typing as t

import numpy as np

from ..logger import MESSAGES_TYPE
from .__base__ import _CustomException


class ShouldBeOneOf(_CustomException):
    def __init__(self, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 msgs: MESSAGES_TYPE):
        if value in values:
            return
        super().__init__(msgs=[
            *msgs,
            f"Supplied value `{value}` should be one of: ",
            values if bool(values) else "[]",
        ])


class ShouldNotBeOneOf(_CustomException):
    def __init__(self, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 msgs: MESSAGES_TYPE):
        if value not in values:
            return
        super().__init__(msgs=[
            *msgs,
            f"Supplied value `{value}` should not be one of:",
            values,
        ])


class ShouldBeEqual(_CustomException):
    def __init__(self, *, value1, value2, msgs: MESSAGES_TYPE):
        _in_npy_test = isinstance(value1, np.ndarray) and isinstance(
            value2, np.ndarray)
        if _in_npy_test:
            if np.array_equal(value1, value2):
                return
        if value1 == value2:
            return
        _msgs_dict = {
            "value1": f"{value1}",
            "value2": f"{value2}",
        }
        if isinstance(value1, dict) and isinstance(value2, dict):
            _msgs_dict["keys"] = f"{value1.keys()}, {value2.keys()}"
        if _in_npy_test:
            _msgs_dict["shape"] = f"{value1.shape}, {value2.shape}"
            _msgs_dict["dtype"] = f"{value1.dtype}, {value2.dtype}"
            _msgs = [
                f"The numpy arrays are not equal:",
                _msgs_dict,
            ]
        else:
            _msgs = [
                f"Value {value1} != {value2}",
                f"Value types are {type(value1)}, {type(value2)}",
            ]
        super().__init__(msgs=[*msgs, *_msgs])


class ShouldNotBeEqual(_CustomException):
    def __init__(self, *, value1, value2, msgs: MESSAGES_TYPE):
        if value1 != value2:
            return
        super().__init__(msgs=[
            *msgs,
            f"Value {value1} == {value2}",
            f"Value types are {type(value1)}, {type(value2)}",
        ])


class ValueNotAllowed(_CustomException):
    def __init__(self, *, value, not_be_value, msgs: MESSAGES_TYPE):
        if value != not_be_value:
            return
        super().__init__(msgs=[
            *msgs,
            f"We do not allow value {value!r}.",
        ])


class SliceShouldNotOverlap(_CustomException):
    def __init__(self, *, slice1: slice, slice2: slice, msgs: MESSAGES_TYPE):
        # step should be always None
        if slice1.step is not None or slice2.step is not None:
            super().__init__(msgs=[
                *msgs,
                f"One of the supplied slices have step==None.",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ])

        # check overlap
        if slice1.start <= slice2.start < slice1.stop:
            super().__init__(msgs=[
                *msgs,
                f"The start of slice overlaps slice2",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ])
        if slice1.start < slice2.stop <= slice1.stop:
            super().__init__(msgs=[
                *msgs,
                f"The stop of slice overlaps slice2",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ])

        # add redundant return for code checker to indicate that this need not
        # be explicitly raised
        return


class NotAllowed(_CustomException):

    _RAISE_EXPLICITLY = True

    def __init__(self, *, msgs: MESSAGES_TYPE):
        super().__init__(msgs=["This is Not Allowed !!!", *msgs])


class ConfigError(_CustomException):

    _RAISE_EXPLICITLY = True

    def __init__(self, *, msgs: MESSAGES_TYPE):
        super().__init__(msgs=["Error with .toolcraft/config.toml", *msgs])


class OnlyValueAllowed(_CustomException):
    def __init__(self, *, value, to_be_value, msgs: MESSAGES_TYPE):
        if value == to_be_value:
            return
        super().__init__(msgs=[
            *msgs,
            f"We do not allow value {value!r}. "
            f"Only value allowed is {to_be_value!r}.",
        ])


class IsIntOrSliceOrListWithin(_CustomException):
    def __init__(
        self,
        *,
        value: t.Union[int, slice, t.List[int]],
        min_value: int,
        max_value: int,
        msgs: MESSAGES_TYPE,
    ):
        _raise = False
        if isinstance(value, slice):
            value = slice(*value.indices(max_value))
            if value.start < 0:
                msgs += [
                    f"Please do not provide negative `start`, "
                    f"found start={value.start!r} "
                ]
                _raise = True
            if value.stop < 0:
                msgs += [
                    f"Please do not provide negative `stop`, "
                    f"found stop={value.stop!r} "
                ]
                _raise = True
            if value.start > value.stop:
                msgs += [
                    f"Slice `stop` should be greater that `start`, "
                    f"found `start={value.start}` > `stop={value.stop}`"
                ]
                _raise = True
            if not min_value <= value.start < max_value:
                msgs += [
                    f"We need slice `start` to be between "
                    f"`{min_value} <= start < {max_value}`, "
                    f"found start={value.start!r}"
                ]
                _raise = True
            if not min_value < value.stop <= max_value:
                msgs += [
                    f"We need slice `stop` to be between "
                    f"`{min_value} < stop <= {max_value}`, "
                    f"found stop={value.stop!r}"
                ]
                _raise = True
        elif isinstance(value, list):
            for i, index in enumerate(value):
                if not min_value <= index < max_value:
                    msgs += [
                        f"The item {i} in the list is not within range i.e. "
                        f"between {min_value} and {max_value}",
                        f"Found value {index}",
                    ]
                    _raise = True
                    break
        elif isinstance(value, int):
            if not min_value <= value < max_value:
                msgs += [
                    f"The value {value} is not within range i.e. "
                    f"between {min_value} and {max_value}",
                ]
                _raise = True
        else:
            msgs += [
                f"Expected a int, slice or list of int instead found "
                f"type {type(value)}"
            ]
            _raise = True

        if not _raise:
            return

        super().__init__(msgs=[*msgs])


class ShouldBeBetween(_CustomException):
    def __init__(
        self,
        *,
        value: t.Union[int, float],
        minimum: t.Union[int, float],
        maximum: t.Union[int, float],
        msgs: MESSAGES_TYPE,
    ):
        if not isinstance(value, (int, float)):
            super().__init__(msgs=[
                *msgs,
                f"The value supplied is not a int or float. "
                f"Found unrecognized type {type(value)}.",
            ])
        if minimum <= value < maximum:
            return
        super().__init__(msgs=[
            *msgs,
            f"Value should be in the range {minimum} <= value < {maximum}",
            f"Instead found value {value!r} which is out of range."
            f"{type(value)}.",
        ])


class ShouldBeGreaterThan(_CustomException):
    def __init__(
        self,
        *,
        value: t.Union[int, float],
        minimum_value: t.Union[int, float],
        msgs: MESSAGES_TYPE,
    ):
        if value > minimum_value:
            return
        super().__init__(msgs=[
            *msgs, f"Value {value} should be greater than {minimum_value}."
        ])


class ShouldBeLessThanEqTo(_CustomException):
    def __init__(
        self,
        *,
        value: t.Union[int, float],
        maximum_value: t.Union[int, float],
        msgs: MESSAGES_TYPE,
    ):
        if value <= maximum_value:
            return
        super().__init__(msgs=[
            *msgs, f"Value {value} should be <= {maximum_value}."
        ])


class ShouldBeInstanceOf(_CustomException):
    def __init__(self, *, value: t.Any, value_types: t.Tuple,
                 msgs: MESSAGES_TYPE):
        if isinstance(value, value_types):
            return

        super().__init__(msgs=[
            *msgs,
            f"Supplied value type {type(value)!r} is not one of: ",
            value_types,
        ])


class ShouldNotBeInstanceOf(_CustomException):
    def __init__(self, *, value: t.Any, value_types: t.Tuple,
                 msgs: MESSAGES_TYPE):
        if not isinstance(value, value_types):
            return

        super().__init__(msgs=[
            *msgs,
            f"Supplied value type {type(value)!r} is one of: ",
            value_types,
        ])


class ShouldBeSubclassOf(_CustomException):
    def __init__(self, *, value: t.Any, value_types: t.Tuple,
                 msgs: MESSAGES_TYPE):
        if issubclass(value, value_types):
            return

        super().__init__(msgs=[
            *msgs,
            f"Supplied class {value!r} is not a subclass of: ",
            value_types,
        ])


class ShouldBeClassMethod(_CustomException):
    def __init__(self, *, value: t.Callable, msgs: MESSAGES_TYPE):
        if inspect.ismethod(value):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a method instead found value {value} with type"
            f" {type(value)}",
            f"Note that this helps us obtain respective instance .__self__",
        ])


class ShouldBeFunction(_CustomException):
    def __init__(self, *, value: t.Callable, msgs: MESSAGES_TYPE):
        if inspect.isfunction(value):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a function instead found value {value} with type"
            f" {type(value)}",
        ])


class ShouldBeDataClass(_CustomException):
    def __init__(self, *, obj: t.Callable, msgs: MESSAGES_TYPE):
        if dataclasses.is_dataclass(obj):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a dataclass instead found value {obj} with "
            f"type {type(obj)}",
        ])


class ShouldHaveAttribute(_CustomException):
    def __init__(self, *, attr_name: str, obj: t.Any, msgs: MESSAGES_TYPE):
        if hasattr(obj, attr_name):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect an attribute {attr_name!r} in object:",
            f"{obj}.",
        ])


class ShouldHaveProperty(_CustomException):
    def __init__(self, *, attr_name: str, obj: t.Any, msgs: MESSAGES_TYPE):
        if not hasattr(obj.__class__, attr_name):
            super().__init__(msgs=[
                *msgs,
                f"We expect class {obj.__class__} to have a property "
                f"named {attr_name!r}",
            ])

        if not isinstance(getattr(obj.__class__, attr_name), property):
            super().__init__(msgs=[
                *msgs,
                f"The member {attr_name!r} of class {obj.__class__} is "
                f"not a property.",
                f"Instead, found type "
                f"{type(getattr(obj.__class__, attr_name))}",
            ])
        return


class ShouldNotHaveAttribute(_CustomException):
    def __init__(self, *, attr_name: str, obj: t.Any, msgs: MESSAGES_TYPE):
        if not hasattr(obj, attr_name):
            return

        super().__init__(msgs=[
            *msgs,
            f"We do not expect a attribute {attr_name} in object:",
            f"{obj}.",
        ])
