"""
todo: check validators library
      https://validators.readthedocs.io/en/latest/
"""
import dataclasses
import inspect
import typing as t

import numpy as np

from ..logger import MESSAGES_TYPE
from . import CustomException


class ShouldBeOneOf(CustomException):
    def __init__(self, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 msgs: MESSAGES_TYPE):
        if value in values:
            return
        super().__init__(msgs=[
            *msgs,
            f"Supplied value `{value}` should be one of: ",
            values if bool(values) else "[]",
        ])


class ShouldNotBeOneOf(CustomException):
    def __init__(self, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 msgs: MESSAGES_TYPE):
        if value not in values:
            return
        super().__init__(msgs=[
            *msgs,
            f"Supplied value `{value}` should not be one of:",
            values,
        ])


class ShouldBeEqual(CustomException):
    def __init__(self, *, value1, value2, msgs: MESSAGES_TYPE):
        _in_npy_test = isinstance(value1, np.ndarray) and isinstance(
            value2, np.ndarray)
        if _in_npy_test:
            if np.array_equal(value1, value2):
                return
        if value1 == value2:
            return
        if _in_npy_test:
            _msgs = [
                f"The numpy arrays are not equal:",
                {
                    "shape": f"{value1.shape}, {value2.shape}",
                    "dtype": f"{value1.dtype}, {value2.dtype}",
                    "value1": f"{value1}",
                    "value2": f"{value2}",
                },
            ]
        else:
            _msgs = [
                f"Value {value1} != {value2}",
                f"Value types are {type(value1)}, {type(value2)}",
            ]
        super().__init__(msgs=[*msgs, *_msgs])


class ShouldNotBeEqual(CustomException):
    def __init__(self, *, value1, value2, msgs: MESSAGES_TYPE):
        if value1 != value2:
            return
        super().__init__(msgs=[
            *msgs,
            f"Value {value1} == {value2}",
            f"Value types are {type(value1)}, {type(value2)}",
        ])


class ValueNotAllowed(CustomException):
    def __init__(self, *, value, not_be_value, msgs: MESSAGES_TYPE):
        if value != not_be_value:
            return
        super().__init__(msgs=[
            *msgs,
            f"We do not allow value {value!r}.",
        ])


class SliceShouldNotOverlap(CustomException):
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


class NotAllowed(CustomException):
    def __init__(self, *, msgs: MESSAGES_TYPE):
        super().__init__(msgs=["This is Not Allowed !!!", *msgs])


class OnlyValueAllowed(CustomException):
    def __init__(self, *, value, to_be_value, msgs: MESSAGES_TYPE):
        if value == to_be_value:
            return
        super().__init__(msgs=[
            *msgs,
            f"We do not allow value {value!r}. "
            f"Only value allowed is {to_be_value!r}.",
        ])


class IsSliceOrListWithin(CustomException):
    def __init__(
        self,
        *,
        value: t.Union[slice, t.List[int]],
        min_value: int,
        max_value: int,
        msgs: MESSAGES_TYPE,
    ):
        _raise = False
        if isinstance(value, slice):
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
        else:
            msgs += [
                f"Expected a int, slice or list of int instead found "
                f"type {type(value)}"
            ]
            _raise = True

        if not _raise:
            return

        super().__init__(msgs=[*msgs])


class ShouldBeBetween(CustomException):
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


class ShouldBeGreaterThan(CustomException):
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


class ShouldBeInstanceOf(CustomException):
    def __init__(self, *, value: t.Any, value_types: t.Tuple,
                 msgs: MESSAGES_TYPE):
        if isinstance(value, value_types):
            return

        super().__init__(msgs=[
            *msgs,
            f"Supplied value type {type(value)!r} is not one of: ",
            value_types,
        ])


class ShouldBeSubclassOf(CustomException):
    def __init__(self, *, value: t.Any, value_types: t.Tuple,
                 msgs: MESSAGES_TYPE):
        if issubclass(value, value_types):
            return

        super().__init__(msgs=[
            *msgs,
            f"Supplied class {value!r} is not a subclass of: ",
            value_types,
        ])


class ShouldBeClassMethod(CustomException):
    def __init__(self, *, value: t.Callable, msgs: MESSAGES_TYPE):
        if inspect.ismethod(value):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a method instead found value {value} with type"
            f" {type(value)}",
            f"Note that this helps us obtain respective instance .__self__",
        ])


class ShouldBeFunction(CustomException):
    def __init__(self, *, value: t.Callable, msgs: MESSAGES_TYPE):
        if inspect.isfunction(value):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a function instead found value {value} with type"
            f" {type(value)}",
        ])


class ShouldBeDataClass(CustomException):
    def __init__(self, *, obj: t.Callable, msgs: MESSAGES_TYPE):
        if dataclasses.is_dataclass(obj):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect a dataclass instead found value {obj} with "
            f"type {type(obj)}",
        ])


class ShouldHaveAttribute(CustomException):
    def __init__(self, *, attr_name: str, obj: t.Any, msgs: MESSAGES_TYPE):
        if hasattr(obj, attr_name):
            return

        super().__init__(msgs=[
            *msgs,
            f"We expect an attribute {attr_name!r} in object:",
            f"{obj}.",
        ])


class ShouldHaveProperty(CustomException):
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


class ShouldNotHaveAttribute(CustomException):
    def __init__(self, *, attr_name: str, obj: t.Any, msgs: MESSAGES_TYPE):
        if not hasattr(obj, attr_name):
            return

        super().__init__(msgs=[
            *msgs,
            f"We do not expect a attribute {attr_name} in object:",
            f"{obj}.",
        ])
