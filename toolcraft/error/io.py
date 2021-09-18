
import pathlib
import typing as t

from . import CustomException
from ..logger import MESSAGES_TYPE


class FileMustBeOnDiskOrNetwork(CustomException):
    def __init__(
        self, *,
        path: pathlib.Path,
        msgs: MESSAGES_TYPE
    ):
        if path.is_file():
            return

        if path.is_dir():
            _msg = f"File `{str(path)}` is a directory."
        else:
            _msg = f"File `{str(path)}` not on disk."

        super().__init__(
            msgs=[
                *msgs, _msg
            ]
        )


class FolderMustBeOnDiskOrNetwork(CustomException):
    def __init__(
        self, *,
        path: pathlib.Path,
        msgs: MESSAGES_TYPE
    ):
        if path.is_dir():
            return

        if path.is_file():
            _msg = f"Folder `{str(path)}` is a file."
        else:
            _msg = f"Folder `{str(path)}` not on disk or network."

        super().__init__(
            msgs=[
                *msgs, _msg
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


class FileMustNotBeOnDiskOrNetwork(CustomException):
    def __init__(
        self, *,
        path: pathlib.Path,
        msgs: MESSAGES_TYPE
    ):
        if not path.exists():
            return

        _msg = f"`{str(path)}` already on disk or network."
        if path.is_dir():
            _msg += "And it happens to be a directory !!!"

        super().__init__(
            msgs=[
                *msgs, _msg
            ]
        )


class FolderMustNotBeOnDiskOrNetwork(CustomException):
    def __init__(
        self, *,
        path: pathlib.Path,
        msgs: MESSAGES_TYPE
    ):
        if not path.exists():
            return

        _msg = f"`{str(path)}` already on disk or network."
        if path.is_file():
            _msg += "And it happens to be a file !!!"

        super().__init__(
            msgs=[
                *msgs, _msg
            ]
        )


class LongPath(CustomException):

    def __init__(
            self, *,
            path: pathlib.Path,
            msgs: MESSAGES_TYPE
    ):
        if not path.is_absolute():
            super().__init__(
                msgs=[
                    *msgs,
                    f"The path provided is relative please provide absolute "
                    f"path.",
                    f"Supplied path {path}"
                ]
            )

        _path_len = len(path.as_posix())

        # 260 is for windows ... leave 60 for arrow storage
        # todo: adapt code based on OS platform
        if _path_len < 260 - 60:
            return

        super().__init__(
            msgs=[
                *msgs,
                f"Length of the path is too long {_path_len} > 260",
                f"Try to not use deep nesting structures and keep short "
                f"folder names.",
                f"Supplied path {path}",
                f"If possible do not keep project working dir is nested "
                f"directories.",
            ]
        )
