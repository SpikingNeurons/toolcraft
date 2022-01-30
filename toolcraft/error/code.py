import typing as t
import traceback
import sys
import numpy as np

from .__base__ import _CustomException
from ..logger import MESSAGES_TYPE


class RaiseExplicitly(_CustomException):

    _RAISE_EXPLICITLY = True

    def __init__(
        self, *,
        msgs: MESSAGES_TYPE
    ):
        super().__init__(
            msgs=[
                "Error while coding !!!",
                *msgs
            ]
        )


class ShouldNeverHappen(_CustomException):

    _RAISE_EXPLICITLY = True

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


class NotAllowed(_CustomException):

    _RAISE_EXPLICITLY = True

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


class CodingError(_CustomException):

    _RAISE_EXPLICITLY = True

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


class RaiseUnhandledException(_CustomException):

    _RAISE_EXPLICITLY = True

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


class NotImplementedCorrectly(_CustomException):

    _RAISE_EXPLICITLY = True

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


class NotSupported(_CustomException):

    _RAISE_EXPLICITLY = True

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


class AssertError(_CustomException):
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


class ExitGracefully(_CustomException):

    _RAISE_EXPLICITLY = True

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
