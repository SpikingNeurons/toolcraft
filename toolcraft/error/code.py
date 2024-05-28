import typing as t

from .__base__ import _CustomException
from ..logger import MESSAGES_TYPE


class ShouldNeverHappen(_CustomException):
    """
    This should never happen !!!
    """
    ...


class NotAllowed(_CustomException):
    """
    This is Not Allowed !!!
    """
    ...


class CodingError(_CustomException):
    """
    Possible error/bug while coding !!!
    """
    ...


class NotImplementedCorrectly(_CustomException):
    """
    The functionality is not implemented correctly !!!
    """
    ...


class NotYetImplemented(_CustomException):
    """
    The functionality is not yet implemented we might support it later !!!
    """
    ...


class ImplementInChildClass(_CustomException):
    """
    Please implement this in child class !!!
    """
    ...


class NotSupported(_CustomException):
    """
    We do not support this!!!
    """
    ...


class AssertError(_CustomException):

    @classmethod
    def check(
        cls, *,
        value1, value2,
        notes: MESSAGES_TYPE
    ):
        try:
            import numpy as np
            if isinstance(value1, np.ndarray):
                if np.array_equal(value1, value2):
                    return
        except ImportError:
            ...

        if value1 == value2:
            return

        _notes = [
            f"Value {value1} != {value2}",
            f"Value types are {type(value1)}, {type(value2)}"
        ]

        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)


class ExitGracefully(_CustomException):
    """
    Exiting Gracefully !!!
    """
    ...
