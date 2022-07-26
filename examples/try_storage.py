"""
todo: Some bugs to be fixed
  [1] try_arrow_storage()
  Exists check with filter queries
    + need test cases
    + and is not working
"""
import dataclasses
import enum
import pathlib
import sys
import time
import typing as t
# todo ... get rich dunder methods for YamlRepr and then get rid of this print ;)
from rich import print


sys.path.append("..")

import numpy as np
import pandas as pd
import pyarrow as pa
from toolcraft import marshalling as m
from toolcraft import settings
from toolcraft import storage as s
from toolcraft import util, richy, logger
from toolcraft.storage import file_system, Path
from toolcraft.storage.table import Filter
from toolcraft.storage.table import make_expression as me

settings.DEBUG_HASHABLE_STATE = False

_LOGGER = logger.get_logger()
_TEMP_PATH = "storage_temp"


class NewEnum(m.FrozenEnum, enum.Enum):
    a1 = 11


@dataclasses.dataclass(frozen=True)
class HashableTryChild(m.HashableClass):

    a: int


@dataclasses.dataclass(frozen=True)
class HashableTry(m.HashableClass):
    a: int
    e: NewEnum
    child: HashableTryChild


def try_hashable_ser():
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>1")
    _hashable = HashableTry(
        a=33,
        e=NewEnum.a1,
        child=HashableTryChild(
            a=66,
        ),
    )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>2")
    # noinspection PyTypeChecker
    _de_ser_hashable = HashableTry.from_yaml(
        _hashable.yaml(),
    )  # type: HashableTry
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>3")

    print(_hashable.yaml())
    print(_de_ser_hashable.yaml())

    # assert if yaml repr is correct
    assert _hashable.yaml() == _de_ser_hashable.yaml()

    # check enum
    assert _hashable.e == NewEnum.a1, "enums are not same"


@dataclasses.dataclass(frozen=True)
class DnTestFile(s.DownloadFileGroup):

    @property
    def meta_info(self) -> dict:
        return {}

    def get_urls(self) -> t.Dict[str, str]:
        return {
            "file1": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file2": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file3": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file4": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
        }

    def get_hashes(self) -> t.Dict[str, str]:
        return {
            "file1": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1"
            "885e6adb4",
            "file2": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1"
            "885e6adb4",
            "file3": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1"
            "885e6adb4",
            "file4": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1"
            "885e6adb4",
        }


def try_download_file():

    # noinspection SpellCheckingInspection
    df = DnTestFile()
    if df.is_created:
        df.delete(force=True)

    df = DnTestFile()

    if not df.is_created:
        df.create()
        df.check()

    df.get_file(file_key="file1")
    df.delete(force=True)


@dataclasses.dataclass(frozen=True)
class DnTestFileAutoHashed(s.DownloadFileGroup):

    @property
    def meta_info(self) -> dict:
        return {}

    def get_urls(self) -> t.Dict[str, str]:
        return {
            "file1": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file2": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file3": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
            "file4": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
            "resources/pdf/dummy.pdf",
        }

    @property
    def is_auto_hash(self) -> bool:
        return True


def try_auto_hashed_download_file():
    # noinspection SpellCheckingInspection
    df = DnTestFileAutoHashed()
    if not df.is_created:
        df.create()
    df.get_file(file_key="file1")

    df0 = DnTestFile()

    assert df0.get_hashes() == df.config.auto_hashes

    df0.delete(force=True)
    df.delete(force=True)


def try_metainfo_file():
    # noinspection SpellCheckingInspection
    df = DnTestFile()
    # note that creating instance above creates file
    df.delete(force=True)
    df = DnTestFile()
    if not df.is_created:
        df.create()
    if df.periodic_check_needed:
        df.check()

    for _ in range(5):
        print(">>>>>>>>>>>>>>>>>>>>>>>>", _)
        print(df.yaml())
        print(df.config)
        df.get_file(file_key="file1")
        print(df.yaml())
        print(df.config)
        time.sleep(1)

    df.delete(force=True)


@dataclasses.dataclass(frozen=True)
class Folder0(s.Folder):
    file_system: str


@dataclasses.dataclass(frozen=True)
class Folder1(s.Folder):
    parent_folder: Folder0


@dataclasses.dataclass(frozen=True)
class Folder2(s.Folder):

    parent_folder: Folder1


@dataclasses.dataclass(frozen=True)
class Folder3(s.Folder):

    parent_folder: Folder2


@dataclasses.dataclass(frozen=True)
class ParentTestStorage(m.HashableClass):
    a: int
    b: float


def try_creating_folders():
    folder0 = Folder0(for_hashable=f"{_TEMP_PATH}/folders", file_system="CWD")
    folder1 = Folder1(parent_folder=folder0, for_hashable="parent_1")
    folder2 = Folder2(
        parent_folder=folder1,
        for_hashable=ParentTestStorage(44, 55.0),
    )
    folder3 = Folder3(parent_folder=folder2, for_hashable="leaf_folder")

    print([_.full_path for _ in folder0.path.ls()])

    # or else just delete the super parent and things will chain
    folder0.delete(force=True)
    # note that after this any access to all four instances should get
    # blocked but we still can access them ... check below
    # todo: need to figure out what to do with folders that are deleted ...
    #  adding some flag will increase overhead in __getattribute__ method ...
    #  somehow need to invalidate use of the instance maybe by overriding
    #  dunder methods on fly
    # print(folder0.path.ls())
    # not this one as it contains None so cannot access items but this too
    # needs to be blocked for any future access
    # print(folder3.items.keys())


@dataclasses.dataclass(frozen=True)
class TestStorageResultsFolder(s.Folder):
    @property
    def file_system(self) -> str:
        return "CWD"


@dataclasses.dataclass(frozen=True)
class TestStorageResultsFolderGcs(s.Folder):
    @property
    def file_system(self) -> str:
        return "GCS"


@dataclasses.dataclass(frozen=True)
class TestStorage(m.HashableClass):
    a: int
    b: float

    @property
    @util.CacheResult
    def results_folder(self) -> TestStorageResultsFolder:
        return TestStorageResultsFolder(
            for_hashable=f"{_TEMP_PATH}/{self.hex_hash}")

    @property
    @util.CacheResult
    def store(self) -> s.Table:
        return s.Table(parent_folder=self.results_folder, for_hashable="store")

    @property
    @util.CacheResult
    def store_with_partition_cols(self) -> s.Table:
        return s.Table(parent_folder=self.results_folder,
                       for_hashable="store_with_partition_cols",
                       partition_cols=["a", "b"],)

    @staticmethod
    def data_vector(
        key: str,
        a: int = None,
        b: int = None,
    ) -> pa.Table:
        return {
            "pandas_dataframe": pa.table({"a": np.asarray([1, 2, 3, 4])}),
            "pandas_dataframe_with_partition_cols": pa.table(
                {
                    "a": np.asarray([a] * 4),
                    "b": np.asarray([b] * 4),
                    "c": np.asarray([6, 7, 8, 9]),
                },
            ),
        }[key]


@dataclasses.dataclass(frozen=True)
class TestStorageGcs(TestStorage):

    @property
    @util.CacheResult
    def results_folder(self) -> TestStorageResultsFolderGcs:
        return TestStorageResultsFolderGcs(
            for_hashable=f"{_TEMP_PATH}/{self.hex_hash}")


@dataclasses.dataclass(frozen=True)
class FileGroup0(s.FileGroup):

    start_str: str
    parent_folder: Folder0

    @property
    def is_auto_hash(self) -> bool:
        return True

    @property
    @util.CacheResult
    def file_keys(self) -> t.List[str]:
        return [self.start_str + _ for _ in ["a", "b", "c", "d"]]

    def create_file(
        self, *, file_key: str, richy_panel: richy.StatusPanel = None
    ) -> Path:
        _ret = self.path / file_key
        _ret.touch()
        return _ret


def try_arrow_storage(gcs: bool):
    if gcs:
        ts = TestStorageGcs(1, 2.0)
    else:
        ts = TestStorage(1, 2.0)

    # ---------------------------------------------------------01
    print("---------------------------------------------------------01")
    # pandas_dataframe
    print("ts.store.write(value=...)")
    assert ts.store.write(value=ts.data_vector("pandas_dataframe"))

    print("ts.store.read()")
    assert ts.store.read() == ts.data_vector("pandas_dataframe")

    print("Ensure reading twice works -> ts.store.read()")
    assert ts.store.read() == ts.data_vector("pandas_dataframe")

    print("ts.store.delete_()")
    assert ts.store.delete_()

    print("ts.store.write(value=...)")
    assert ts.store.write(value=ts.data_vector("pandas_dataframe"))

    print("ts.store.read()")
    assert ts.store.read() == ts.data_vector("pandas_dataframe")

    print("ts.store.delete_()")
    assert ts.store.delete_()

    # ---------------------------------------------------------02
    print("---------------------------------------------------------02")
    print("---------------------------------------------------------02.01")
    # pandas_dataframe_with_partition_cols
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=2")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=2),
    )
    r = ts.store_with_partition_cols.read()
    print("ts.store_with_partition_cols.read()")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=2)
        .to_pandas()
        .sort_index(axis=1),
    )
    print("ts.store_with_partition_cols.delete_()")
    assert ts.store_with_partition_cols.delete_()

    print("---------------------------------------------------------02.02")
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=22")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=33")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=33),
    )
    r = ts.store_with_partition_cols.read()
    print("ts.store_with_partition_cols.read()")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22)
                .to_pandas()
                .sort_index(axis=1),
                ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=33)
                .to_pandas()
                .sort_index(axis=1),
            ],
            ignore_index=True,
        ),
    )
    r = ts.store_with_partition_cols.read(filter_expression=me([Filter('a', '=', 1)]))
    print("ts.store_with_partition_cols.read(filter_expression=me(\n\t[Filter('a', '=', 1)]))")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22)
                .to_pandas()
                .sort_index(axis=1),
                ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=33)
                .to_pandas()
                .sort_index(axis=1),
            ],
            ignore_index=True,
        ),
    )
    r = ts.store_with_partition_cols.read(filter_expression=me([Filter('a', '=', 1), Filter('b', '=', 22)]))
    print("ts.store_with_partition_cols.read(filter_expression=me(\n\t[Filter('a', '=', 1), Filter('b', '=', 22)]))")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22)
        .to_pandas()
        .sort_index(axis=1),
    )

    print("ts.store_with_partition_cols.exists(filter_expression=me(\n\t[Filter('a', '=', 1), Filter('b', '=', 22)]))")
    assert ts.store_with_partition_cols.exists(filter_expression=me([Filter('a', '=', 1), Filter('b', '=', 22)]))

    print("ts.store_with_partition_cols.exists(filter_expression=me(\n\t[Filter('a', '=', 1), Filter('b', '=', 33)]))")
    assert ts.store_with_partition_cols.exists(filter_expression=me([Filter('a', '=', 1), Filter('b', '=', 33)]))

    print("not ts.store_with_partition_cols.exists(filter_expression=me(\n\t[Filter('a', '=', 1), Filter('b', '=', 55)]))")
    assert not ts.store_with_partition_cols.exists(filter_expression=me([Filter('a', '=', 1), Filter('b', '=', 55)]))

    print("ts.store_with_partition_cols.delete_(filters=[Filter('b', '=', 33)])")
    assert ts.store_with_partition_cols.delete_(filters=[Filter('b', '=', 33)])

    print("not ts.store_with_partition_cols.exists(filter_expression=me([Filter('b', '=', 33)]))")
    assert not ts.store_with_partition_cols.exists(filter_expression=me([Filter('b', '=', 33)]))

    r = ts.store_with_partition_cols.read()
    print("ts.store_with_partition_cols.read()")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22)
                .to_pandas()
                .sort_index(axis=1),
            ],
            ignore_index=True,
        ),
    )

    print("ts.store_with_partition_cols.delete_()")
    assert ts.store_with_partition_cols.delete_()

    print("---------------------------------------------------------02.03")
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=11")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=11),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=22")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=1, b=33")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=33),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=2, b=44")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=2, b=44),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=2, b=55")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=2, b=55),
    )
    print("ts.store_with_partition_cols.write(value=...) >> a=2, b=66")
    assert ts.store_with_partition_cols.write(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=2, b=66),
    )
    # todo: support this test later when delete_ supports filter_expression
    # r = ts.store_with_partition_cols(mode="d", a=1, filters=[("b", "=", "77")])
    # print(
    #     """r = ts.store_with_partition_cols(
    #         mode='d', a=1, filters=[
    #             ('b', '=', '77')
    #         ]
    #     )""",
    # )
    # assert not r
    # todo: support this test later when delete_ supports filter_expression
    # r = ts.store_with_partition_cols(
    #     mode="d",
    #     a=1,
    #     filters=[
    #         ("b", "<=", 55),
    #         ("b", ">", 22),
    #     ],
    # )
    # print(
    #     """r = ts.store_with_partition_cols(
    #         mode='d', a=1, filters=[
    #             ('b', '<=', 55), ('b', '>', 22),
    #         ]
    #     )""",
    # )
    # assert r
    # r = ts.store_with_partition_cols(mode="r")
    # print("ts.store_with_partition_cols(mode='r')")
    # pd.testing.assert_frame_equal(
    #     r.to_pandas().sort_index(axis=1),
    #     pd.concat(
    #         [
    #             ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=11)
    #             .to_pandas()
    #             .sort_index(axis=1),
    #             ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=22)
    #             .to_pandas()
    #             .sort_index(axis=1),
    #             ts.data_vector("pandas_dataframe_with_partition_cols", a=1, b=66)
    #             .to_pandas()
    #             .sort_index(axis=1),
    #         ],
    #         ignore_index=True,
    #     ),
    # )

    print("ts.store_with_partition_cols.delete_()")
    assert ts.store_with_partition_cols.delete_()

    print("ts.store_with_partition_cols.delete_()")
    assert ts.store_with_partition_cols.delete_()

    # ---------------------------------------------------------03
    print("---------------------------------------------------------03")
    # pandas_dataframe_append

    print("ts.store.append(value=...)")
    assert ts.store.append(value=ts.data_vector("pandas_dataframe"))

    print("ts.store.read()")
    assert ts.store.read() == ts.data_vector("pandas_dataframe")

    print("ts.store.append(value=...)")
    assert ts.store.append(value=ts.data_vector("pandas_dataframe"))

    print("ts.store.append(value=...)")
    assert ts.store.append(value=ts.data_vector("pandas_dataframe"))

    print("ts.store.append(value=...)")
    assert ts.store.append(value=ts.data_vector("pandas_dataframe"))

    r = ts.store.read()
    print(r)
    print("ts.store_streamed.read()")
    pd.testing.assert_frame_equal(
        r.to_pandas(),
        pd.concat(
            [
                ts.data_vector("pandas_dataframe").to_pandas(),
                ts.data_vector("pandas_dataframe").to_pandas(),
                ts.data_vector("pandas_dataframe").to_pandas(),
                ts.data_vector("pandas_dataframe").to_pandas(),
            ],
            ignore_index=True,
        ),
    )

    print("ts.store_streamed.delete()")
    assert ts.store.delete_()

    # ---------------------------------------------------------04
    print("---------------------------------------------------------04")
    # pandas_dataframe_append with partition cols

    print("ts.store_with_partition_cols.append(value=...) >> a=11, b=22")
    assert ts.store_with_partition_cols.append(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=11, b=22),
    )

    print("ts.store_with_partition_cols.append(value=...) >> a=33, b=44")
    assert ts.store_with_partition_cols.append(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=33, b=44),
    )

    print("ts.store_with_partition_cols.append(value=...) >> a=55, b=66")
    assert ts.store_with_partition_cols.append(
        value=ts.data_vector("pandas_dataframe_with_partition_cols", a=55, b=66),
    )

    r = ts.store_with_partition_cols.read()
    print("ts.store_with_partition_cols.read()")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector("pandas_dataframe_with_partition_cols", a=11, b=22,)
                .to_pandas().sort_index(axis=1),
                ts.data_vector("pandas_dataframe_with_partition_cols", a=33, b=44,)
                .to_pandas().sort_index(axis=1),
                ts.data_vector("pandas_dataframe_with_partition_cols", a=55, b=66,)
                .to_pandas().sort_index(axis=1),
            ],
            ignore_index=True,
        ),
    )

    # todo: support this test later when delete_ supports filter_expression
    # r = ts.store_append_with_partition_cols(mode="d", a=11)
    # print("ts.store_streamed_with_partition_cols(mode='d', a=11)")
    # assert r
    #
    # r = ts.store_append_with_partition_cols(mode="r")
    # print("ts.store_streamed_with_partition_cols(mode='r')")
    # pd.testing.assert_frame_equal(
    #     r.to_pandas().sort_index(axis=1),
    #     pd.concat(
    #         [
    #             ts.data_vector(
    #                 "pandas_dataframe_with_partition_cols",
    #                 a=33,
    #                 b=44,
    #             )
    #             .to_pandas()
    #             .sort_index(axis=1),
    #             ts.data_vector(
    #                 "pandas_dataframe_with_partition_cols",
    #                 a=55,
    #                 b=66,
    #             )
    #             .to_pandas()
    #             .sort_index(axis=1),
    #         ],
    #         ignore_index=True,
    #     ),
    # )

    print("ts.store_with_partition_cols.delete_()")
    assert ts.store_with_partition_cols.delete_()

    # ---------------------------------------------------------05
    print("---------------------------------------------------------05")
    # finally, delete folder for hashable that has StoreFields
    print("ts.store.delete(force=True)")
    ts.store.delete(force=True)
    print("ts.store_with_partition_cols.delete(force=True)")
    ts.store_with_partition_cols.delete(force=True)
    print("ts.results_folder.delete(force=True)")
    ts.results_folder.delete(force=True)


def try_file_storage(gcs: bool):
    # create simple file group inside folder
    print("---------------------------------------------------------01")
    print("Create folder0=Folder0(...)")
    folder0 = Folder0(for_hashable=f"{_TEMP_PATH}/folder0", file_system="CWD")
    print("Create fg0=FileGroup0(...)")
    fg0 = FileGroup0(start_str="f1", parent_folder=folder0)
    print("Create fg1=FileGroup0(...)")
    fg1 = FileGroup0(start_str="f2", parent_folder=folder0)
    print("Delete fg0")
    fg0.delete(force=True)
    print("Delete fg1")
    fg1.delete(force=True)
    print("Delete folder0")
    folder0.delete(force=True)

    # create file group from path
    print("---------------------------------------------------------02")
    print("Create folder0=Folder0(...)")
    folder0 = Folder0(for_hashable=f"{_TEMP_PATH}/folder0", file_system="CWD")
    print("Create some folders and files inside it with folder0 as parent")
    _fgs = []
    for _dir, _files in {
        "dir0": ["aa", "bb", "cc"],
        "dir1": ["xxaa", "xxbb", "xxcc", "xxdd"]
    }.items():
        print(f"    create for {_dir}")
        (folder0.path / _dir).mkdir()
        for _file in _files:
            (folder0.path / _dir / _file).touch()
        _fgs.append(
            s.FileGroupFromPaths(
                parent_folder=folder0, folder_name=_dir, keys=_files,
            )
        )
    print("Delete file groups")
    for _fg in _fgs:
        _fg.delete(force=True)
    print("Delete folder0")
    folder0.delete(force=True)


def try_main():
    global _TEMP_PATH
    _path = pathlib.Path(_TEMP_PATH)
    if _path.exists():
        util.io_path_delete(_path, force=True)
    _path.mkdir(parents=True, exist_ok=True)
    _path = _path.resolve()
    try_hashable_ser()
    try_download_file()
    try_auto_hashed_download_file()
    try_metainfo_file()
    try_creating_folders()
    try_arrow_storage(gcs=False)
    try_file_storage(gcs=False)

    # todo: support gcs ...
    #   Note: tests cannot work behind firewall for GCS, only use local machine
    #   loading fs and credentials for gcs is done ... only other things like adding
    #   bucket information to Path is pending ... can be done easily
    # try_arrow_storage(gcs=True)
    # try_file_storage(gcs=True)

    _path.rmdir()


if __name__ == "__main__":
    try_main()
