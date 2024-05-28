
import pathlib
import typing as t

from .__base__ import _CustomException
from ..logger import MESSAGES_TYPE


class FileMustBeOnDiskOrNetwork(_CustomException):

    @classmethod
    def check(
        cls, *,
        path: pathlib.Path,
        notes: MESSAGES_TYPE = None
    ):
        if path.is_file():
            return

        if path.is_dir():
            _notes = [f"File `{str(path)}` is a directory."]
        else:
            _notes = [f"File `{str(path)}` not on disk."]

        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)


class FolderMustBeOnDiskOrNetwork(_CustomException):

    @classmethod
    def check(
        cls, *,
        path: pathlib.Path,
        notes: MESSAGES_TYPE = None
    ):
        if path.is_dir():
            return

        if path.is_file():
            _notes = [f"Folder `{str(path)}` is a file."]
        else:
            _notes = [f"Folder `{str(path)}` not on disk or network."]

        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)


class FileMustNotBeOnDiskOrNetwork(_CustomException):

    @classmethod
    def check(
        cls, *,
        path: pathlib.Path,
        notes: MESSAGES_TYPE = None
    ):
        if not path.exists():
            return

        _notes = [f"`{str(path)}` already on disk or network."]
        if path.is_dir():
            _notes.append("And it happens to be a directory !!!")

        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)


class FolderMustNotBeOnDiskOrNetwork(_CustomException):

    @classmethod
    def check(
        cls, *,
        path: pathlib.Path,
        notes: MESSAGES_TYPE = None
    ):
        if not path.exists():
            return

        _notes = [f"`{str(path)}` already on disk or network."]
        if path.is_file():
            _notes.append("And it happens to be a file !!!")

        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)


class LongPath(_CustomException):

    @classmethod
    def check(
        cls, *,
        path: str,
        notes: MESSAGES_TYPE = None
    ):
        from ..settings import Settings

        _path_len = len(path)

        if _path_len < Settings.FILE_SYSTEMS_PATH_LENGTH:
            return

        _notes = [
            f"Length of the path is too long {_path_len} > {Settings.FILE_SYSTEMS_PATH_LENGTH}",
            f"Try to not use deep nesting structures and keep short folder names.",
            f"Supplied path {path}",
        ]
        if bool(notes):
            _notes = notes + _notes

        raise cls(notes=_notes)
