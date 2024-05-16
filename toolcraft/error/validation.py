"""
todo: check validators library
      https://validators.readthedocs.io/en/latest/
"""
import dataclasses
import inspect
import typing as t

from ..logger import MESSAGES_TYPE
from .__base__ import _CustomException


class ShouldBeOneOf(_CustomException):
    @classmethod
    def check(cls, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 notes: MESSAGES_TYPE = None):
        if value in values:
            return
        _notes = [
            f"Supplied value `{value}` should be one of: ",
            values if bool(values) else "[]",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldNotBeOneOf(_CustomException):
    @classmethod
    def check(cls, *, value: t.Any, values: t.Union[t.List, t.Tuple],
                 notes: MESSAGES_TYPE = None):
        if value not in values:
            return
        _notes = [
            f"Supplied value `{value}` should not be one of:",
            values,
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeEqual(_CustomException):
    @classmethod
    def check(cls, *, value1, value2, notes: MESSAGES_TYPE = None):
        _in_npy_test = False
        try:
            import numpy as np
            _in_npy_test = isinstance(value1, np.ndarray) and isinstance(value2, np.ndarray)
            if _in_npy_test:
                if np.array_equal(value1, value2):
                    return
        except ImportError:
            ...
        if value1 == value2:
            return
        _notes_dict = {
            "value1": f"{value1}",
            "value2": f"{value2}",
        }
        if isinstance(value1, dict) and isinstance(value2, dict):
            _notes_dict["value1_keys"] = f"{value1.keys()}"
            _notes_dict["value2_keys"] = f"{value2.keys()}"
        if _in_npy_test:
            _notes_dict["value1_shape_dtype"] = f"{value1.shape}, {value1.dtype}"
            _notes_dict["value2_shape_dtype"] = f"{value2.shape}, {value2.dtype}"
        else:
            _notes_dict["value1_type"] = f"{type(value1)}"
            _notes_dict["value2_type"] = f"{type(value2)}"
        _notes = ["Value should be equal", _notes_dict]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldNotBeEqual(_CustomException):
    @classmethod
    def check(cls, *, value1, value2, notes: MESSAGES_TYPE = None):
        if value1 != value2:
            return
        _notes = [
            f"Value {value1} == {value2}",
            f"Value types are {type(value1)}, {type(value2)}",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ValueNotAllowed(_CustomException):
    @classmethod
    def check(cls, *, value, not_be_value, notes: MESSAGES_TYPE = None):
        if value != not_be_value:
            return
        _notes = [f"We do not allow value {value!r}."]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class SliceShouldNotOverlap(_CustomException):
    @classmethod
    def check(cls, *, slice1: slice, slice2: slice, notes: MESSAGES_TYPE = None):
        # step should be always None
        if slice1.step is not None or slice2.step is not None:
            _notes = [
                "One of the supplied slices have step==None.",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)

        # check overlap
        if slice1.start <= slice2.start < slice1.stop:
            _notes = [
                f"The start of slice overlaps slice2",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)

        if slice1.start < slice2.stop <= slice1.stop:
            _notes = [
                f"The stop of slice overlaps slice2",
                {
                    "slice1": slice1,
                    "slice2": slice2,
                },
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)


class NotAllowed(_CustomException):
    """
    This is Not Allowed !!!
    """
    ...


class ConfigError(_CustomException):

    def __init__(self, *, notes: MESSAGES_TYPE = None):
        from ..settings import Settings
        _notes = [
            f"Error with config file {Settings.TC_CONFIG_FILE}"
        ]
        if bool(notes):
            _notes = notes + _notes
        super().__init__(notes=_notes)


class OnlyValueAllowed(_CustomException):
    @classmethod
    def check(cls, *, value, to_be_value, notes: MESSAGES_TYPE = None):
        if value == to_be_value:
            return
        _notes = [
            f"We do not allow value {value!r}. "
            f"Only value allowed is {to_be_value!r}.",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class IsIntOrSliceOrListWithin(_CustomException):
    @classmethod
    def check(
        cls,
        *,
        value: t.Union[int, slice, t.List[int]],
        min_value: int,
        max_value: int,
        notes: MESSAGES_TYPE = None,
    ):
        _raise = False
        if isinstance(value, slice):
            value = slice(*value.indices(max_value))
            if value.start < 0:
                notes += [
                    f"Please do not provide negative `start`, "
                    f"found start={value.start!r} "
                ]
                _raise = True
            if value.stop < 0:
                notes += [
                    f"Please do not provide negative `stop`, "
                    f"found stop={value.stop!r} "
                ]
                _raise = True
            if value.start > value.stop:
                notes += [
                    f"Slice `stop` should be greater that `start`, "
                    f"found `start={value.start}` > `stop={value.stop}`"
                ]
                _raise = True
            if not min_value <= value.start < max_value:
                notes += [
                    f"We need slice `start` to be between "
                    f"`{min_value} <= start < {max_value}`, "
                    f"found start={value.start!r}"
                ]
                _raise = True
            if not min_value < value.stop <= max_value:
                notes += [
                    f"We need slice `stop` to be between "
                    f"`{min_value} < stop <= {max_value}`, "
                    f"found stop={value.stop!r}"
                ]
                _raise = True
        elif isinstance(value, list):
            for i, index in enumerate(value):
                if not min_value <= index < max_value:
                    notes += [
                        f"The item {i} in the list is not within range i.e. "
                        f"between {min_value} and {max_value}",
                        f"Found value {index}",
                    ]
                    _raise = True
                    break
        elif isinstance(value, int):
            if not min_value <= value < max_value:
                notes += [
                    f"The value {value} is not within range i.e. "
                    f"between {min_value} and {max_value}",
                ]
                _raise = True
        else:
            notes += [
                f"Expected a int, slice or list of int instead found "
                f"type {type(value)}"
            ]
            _raise = True

        if _raise:
            raise cls(notes=notes)


class ShouldBeBetween(_CustomException):
    @classmethod
    def check(
        cls,
        *,
        value: t.Union[int, float],
        minimum: t.Union[int, float],
        maximum: t.Union[int, float],
        notes: MESSAGES_TYPE = None,
    ):
        if not isinstance(value, (int, float)):
            _notes = [
                f"The value supplied is not a int or float. "
                f"Found unrecognized type {type(value)}.",
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)
        if minimum <= value < maximum:
            return
        _notes = [
            f"Value should be in the range {minimum} <= value < {maximum}",
            f"Instead found value {value!r} which is out of range with type {type(value)}.",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeGreaterThan(_CustomException):
    @classmethod
    def check(
        cls,
        *,
        value: t.Union[int, float],
        minimum_value: t.Union[int, float],
        notes: MESSAGES_TYPE = None,
    ):
        if value > minimum_value:
            return
        _notes = [f"Value {value} should be greater than {minimum_value}."]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeLessThanEqTo(_CustomException):
    @classmethod
    def check(
        cls,
        *,
        value: t.Union[int, float],
        maximum_value: t.Union[int, float],
        notes: MESSAGES_TYPE = None,
    ):
        if value <= maximum_value:
            return
        _notes = [f"Value {value} should be <= {maximum_value}."]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeInstanceOf(_CustomException):

    @classmethod
    def check(cls, *, value: t.Any, value_types: t.Tuple,
                 notes: MESSAGES_TYPE = None):
        if isinstance(value, value_types):
            return
        _notes = [
            f"Supplied value type {type(value)!r} is not one of: ",
            value_types,
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldNotBeInstanceOf(_CustomException):
    @classmethod
    def check(cls, *, value: t.Any, value_types: t.Tuple,
                 notes: MESSAGES_TYPE = None):
        if not isinstance(value, value_types):
            return
        _notes = [
            f"Supplied value type {type(value)!r} is one of: ",
            value_types,
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeSubclassOf(_CustomException):
    @classmethod
    def check(cls, *, value: t.Any, value_types: t.Tuple,
                 notes: MESSAGES_TYPE = None):
        if issubclass(value, value_types):
            return
        _notes = [
            f"Supplied class {value!r} is not a subclass of: ",
            value_types,
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeClassMethod(_CustomException):
    @classmethod
    def check(cls, *, value: t.Callable, notes: MESSAGES_TYPE = None):
        if inspect.ismethod(value):
            return
        _notes = [
            f"We expect a class method instead found value {value} with type"
            f" {type(value)}",
            f"Note that this helps us obtain respective instance .__self__",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeFunction(_CustomException):
    @classmethod
    def check(cls, *, value: t.Callable, notes: MESSAGES_TYPE = None):
        if inspect.isfunction(value):
            return
        _notes = [
            f"We expect a function instead found value {value} with type {type(value)}"
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldBeDataClass(_CustomException):
    @classmethod
    def check(cls, *, obj: t.Callable, notes: MESSAGES_TYPE = None):
        if dataclasses.is_dataclass(obj):
            return
        _notes = [
            f"We expect a dataclass instead found value {obj} with "
            f"type {type(obj)}",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldHaveAttribute(_CustomException):
    @classmethod
    def check(cls, *, attr_name: str, obj: t.Any, notes: MESSAGES_TYPE = None):
        if hasattr(obj, attr_name):
            return
        _notes = [
            f"We expect an attribute {attr_name!r} in object:",
            f"{obj}.",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)


class ShouldHaveProperty(_CustomException):
    @classmethod
    def check(cls, *, attr_name: str, obj: t.Any, notes: MESSAGES_TYPE = None):
        if not hasattr(obj.__class__, attr_name):
            _notes = [
                f"We expect class {obj.__class__} to have a property "
                f"named {attr_name!r}",
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)

        if not isinstance(getattr(obj.__class__, attr_name), property):
            _notes = [
                f"The member {attr_name!r} of class {obj.__class__} is "
                f"not a property.",
                f"Instead, found type "
                f"{type(getattr(obj.__class__, attr_name))}",
            ]
            if bool(notes):
                _notes = notes + _notes
            raise cls(notes=_notes)


class ShouldNotHaveAttribute(_CustomException):
    @classmethod
    def check(cls, *, attr_name: str, obj: t.Any, notes: MESSAGES_TYPE = None):
        if not hasattr(obj, attr_name):
            return
        _notes = [
            f"We do not expect a attribute {attr_name} in object:",
            f"{obj}.",
        ]
        if bool(notes):
            _notes = notes + _notes
        raise cls(notes=_notes)
