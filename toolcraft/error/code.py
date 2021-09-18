import typing as t
import traceback
import sys
import numpy as np

from . import CustomException
from ..logger import MESSAGES_TYPE


class ShouldNeverHappen(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "This should never happen !!!",
                *msgs
            ]
        )


class NotAllowed(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "This is Not Allowed !!!",
                *msgs
            ]
        )


class CodingError(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "Possible error/bug while coding !!!",
                *msgs
            ]
        )


class RaiseUnhandledException(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE,
        exception: Exception,
    ):
        super().__init__(
            msgs=[
                "Encountered unhandled exception !!!",
                *msgs
            ],
            unhandled_exception=exception,
        )


class NotImplementedCorrectly(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "The functionality is not implemented correctly !!!",
                *msgs
            ]
        )


class NotSupported(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "We do not support this!!!",
                *msgs
            ]
        )


class AssertError(CustomException):
    def __init__(
        self, *,
        value1, value2,
        msgs: MESSAGES_TYPE
    ):
        if isinstance(value1, np.ndarray):
            if np.array_equal(value1, value2):
                return

        if value1 == value2:
            return

        super().__init__(
            msgs=[
                *msgs,
                f"Value {value1} != {value2}",
                f"Value types are {type(value1)}, {type(value2)}"
            ]
        )


class ExitGracefully(CustomException):
    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "Exiting Gracefully !!!",
                *msgs
            ]
        )
