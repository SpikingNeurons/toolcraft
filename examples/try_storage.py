"""
todo: Some bugs to be fixed
  [1] try_arrow_storage()
  Exists check with filter queries
    + need test cases
    + and is not working
"""


import pathlib
import sys

sys.path.append("..\\..")
import typing as t
import dataclasses
import pyarrow as pa
import tensorflow.keras as tk
import numpy as np
import pandas as pd
import time
import enum
from toolcraft import settings
from toolcraft import marshalling as m
from toolcraft import storage as s
from toolcraft import util

settings.DEBUG_HASHABLE_STATE = False

_TEMP_PATH = pathlib.Path("storage_temp")


class NewEnum(m.FrozenEnum, enum.Enum):
    a1 = 11


@dataclasses.dataclass(frozen=True)
class HashableTryChild(m.HashableClass):

    a: int
    l: m.FrozenKeras


@dataclasses.dataclass(frozen=True)
class HashableTry(m.HashableClass):
    a: int
    l: m.FrozenKeras
    o: m.FrozenKeras
    d: m.FrozenDict
    e: NewEnum
    child: HashableTryChild


def try_hashable_ser():
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>1")
    _hashable = HashableTry(
        a=33,
        l=m.FrozenKeras(
            tk.losses.CategoricalCrossentropy(label_smoothing=1.0)
        ),
        o=m.FrozenKeras(
          tk.optimizers.Adam(
              learning_rate=tk.optimizers.schedules.ExponentialDecay(
                  0.1, 2, 0.3
              )
          )
        ),
        d=m.FrozenDict(
            {11: 1, "2": 2, "3": 33}
        ),
        e=NewEnum.a1,
        child=HashableTryChild(
            a=66,
            l=m.FrozenKeras(
                tk.losses.CategoricalCrossentropy(label_smoothing=2.0)
            )
        )
    )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>2")
    # noinspection PyTypeChecker
    _de_ser_hashable = HashableTry.from_yaml(
        _hashable.yaml()
    )  # type: HashableTry
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>3")

    print(_hashable.yaml())
    print(_de_ser_hashable.yaml())

    # assert if yaml repr is correct
    assert _hashable.yaml() == _de_ser_hashable.yaml()

    # check if when object created in the program the keras obj remains keras
    assert isinstance(_hashable.l.get(), tk.losses.Loss)
    assert isinstance(_hashable.child.l.get(), tk.losses.Loss)

    # check if when load from yaml-str the resulting object converts the
    # _KerasParse object to keras actual object
    assert isinstance(_de_ser_hashable.l.get(), tk.losses.Loss)
    assert isinstance(_de_ser_hashable.child.l.get(), tk.losses.Loss)

    # check enum
    assert _hashable.e == NewEnum.a1, "enums are not same"

    # check if deserialization always lead to new instances for FrozenKeras
    assert id(_hashable.l) == id(_hashable.l)
    _1, _2 = _hashable.l.get(), _hashable.l.get()
    assert id(_1) != id(_2), "should be different"

    # check if deserialization always lead to new instances for FrozenDict
    assert id(_hashable.d) == id(_hashable.d)
    _1, _2 = _hashable.d.get(), _hashable.d.get()
    assert id(_1) != id(_2), "should be different"


class DnTestFile(s.DownloadFileGroup):
    @property
    def meta_info(self) -> dict:
        return {}

    def get_urls(self) -> t.Dict[str, str]:
        return {
            "file": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
                    "resources/pdf/dummy.pdf"
        }

    def get_hashes(self) -> t.Dict[str, str]:
        return {
            "file": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1"
                    "885e6adb4"
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
    df.get_file(file_key="file")
    df.delete(force=True)


class DnTestFileAutoHashed(s.DownloadFileGroup):
    @property
    def meta_info(self) -> dict:
        return {}

    def get_urls(self) -> t.Dict[str, str]:
        return {
            "file": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
                    "resources/pdf/dummy.pdf"
        }

    @property
    def is_auto_hash(self) -> bool:
        return True


def try_auto_hashed_download_file():
    # noinspection SpellCheckingInspection
    df = DnTestFileAutoHashed()
    if not df.is_created:
        df.create()
    df.get_file(file_key="file")

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
        print(df.config.make_dict_from_current_state().get())
        df.get_file(file_key="file")
        print(df.yaml())
        print(df.config.make_dict_from_current_state().get())
        time.sleep(1)

    df.delete(force=True)


@dataclasses.dataclass(frozen=True)
class Folder0(s.Folder):

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return _TEMP_PATH

    @property
    def contains(self) -> t.Type["Folder1"]:
        return Folder1


@dataclasses.dataclass(frozen=True)
class Folder1(s.Folder):

    parent_folder: s.Folder

    @property
    def uses_parent_folder(self) -> bool:
        return True

    @property
    def contains(self) -> t.Type["Folder2"]:
        return Folder2


@dataclasses.dataclass(frozen=True)
class Folder2(s.Folder):

    parent_folder: s.Folder

    @property
    def uses_parent_folder(self) -> bool:
        return True

    @property
    def contains(self) -> t.Type["Folder3"]:
        return Folder3


@dataclasses.dataclass(frozen=True)
class Folder3(s.Folder):

    parent_folder: s.Folder

    @property
    def uses_parent_folder(self) -> bool:
        return True


@dataclasses.dataclass(frozen=True)
class ParentTestStorage(m.HashableClass):
    a: int
    b: float


def try_creating_folders():
    folder0 = Folder0(
        for_hashable="arrow_storage"
    )
    folder1 = Folder1(
        parent_folder=folder0, for_hashable="parent_1"
    )
    folder2 = Folder2(
        parent_folder=folder1, for_hashable=ParentTestStorage(44, 55.)
    )
    folder3 = Folder3(
        parent_folder=folder2, for_hashable="leaf_folder"
    )

    # either delete from bottom to top
    # folder3.delete(force=True)
    # folder2.delete(force=True)
    # folder1.delete(force=True)
    # folder0.delete(force=True)

    # or else just delete the super parent and things will chain
    folder0.delete(force=True)
    # note that after this any access to all four instances should get
    # blocked but we still can access them ... check below
    # todo: need to figure out what to do with folders that are deleted ...
    #  adding some flag will increase overhead in __getattribute__ method ...
    #  somehow need to invalidate use of the instance maybe by overriding
    #  dunder methods on fly
    print(folder0.items.keys())
    print(folder1.items.keys())
    print(folder2.items.keys())
    # not this one as it contains None so cannot access items but this too
    # needs to be blocked for any future access
    # print(folder3.items.keys())


@dataclasses.dataclass(frozen=True)
class TestStorageResultsFolder(s.ResultsFolder):

    @property
    @util.CacheResult
    def root_dir(self) -> pathlib.Path:
        return _TEMP_PATH


@dataclasses.dataclass(frozen=True)
class TestStorage(m.HashableClass):
    a: int
    b: float

    @property
    def results_folder(self) -> TestStorageResultsFolder:
        return TestStorageResultsFolder(
            for_hashable=self
        )

    @staticmethod
    def data_vector(
        key: str,
        a: int = None,
        b: int = None,
    ) -> pa.Table:
        return {
            "pandas_dataframe":
                pa.table({"a": np.asarray([1, 2, 3, 4])}),
            "pandas_dataframe_with_partition_cols":
                pa.table(
                    {
                        "a": np.asarray([a]*4),
                        "b": np.asarray([b]*4),
                        "c": np.asarray([6, 7, 8, 9]),
                    }
                )
        }[key]

    # noinspection PyUnusedLocal
    @s.StoreField()
    # noinspection PyMethodMayBeStatic
    def store(self, mode: s.MODE_TYPE) -> pa.Table:
        return self.data_vector("pandas_dataframe")

    # noinspection PyUnusedLocal
    @s.StoreField(partition_cols=["a", "b"])
    def store_with_partition_cols(
        self, mode: s.MODE_TYPE, a: int, b: int, filters: s.FILTERS_TYPE = None
    ) -> pa.Table:
        return self.data_vector("pandas_dataframe_with_partition_cols", a, b)

    # noinspection PyUnusedLocal
    @s.StoreField(streamed_write=True)
    # noinspection PyMethodMayBeStatic
    def store_streamed(self, mode: s.MODE_TYPE) -> pa.Table:
        return self.data_vector("pandas_dataframe")

    # noinspection PyUnusedLocal
    @s.StoreField(streamed_write=True, partition_cols=["a", "b"])
    # noinspection PyMethodMayBeStatic
    def store_streamed_with_partition_cols(
        self, mode: s.MODE_TYPE, a: int, b: int
    ) -> pa.Table:
        return self.data_vector("pandas_dataframe_with_partition_cols", a, b)

    # noinspection PyUnusedLocal
    @s.StoreField(partition_cols=['epoch'])
    def store_with_data_kwarg(
        self, mode: s.MODE_TYPE, epoch: int, data: t.Dict
    ) -> pa.Table:
        return pa.table(
            data={
                'epoch': [epoch],
                **data,
            }
        )

    @s.StoreField()
    def store_with_list(
            self,
            mode: s.MODE_TYPE
    ) -> pa.Table:
        result = np.ones((4, 5))
        return pa.table(
            {
               "list": [_ for _ in result]
            }
        )


def try_arrow_storage():
    ts = TestStorage(1, 2.0)

    # ---------------------------------------------------------01
    print("---------------------------------------------------------01")
    # pandas_dataframe
    r = ts.store(mode='rw')
    print("ts.store(mode='rw')")
    assert r == ts.data_vector("pandas_dataframe")

    r = ts.store(mode='r')
    print("ts.store(mode='r')")
    assert r == ts.data_vector("pandas_dataframe")

    r = ts.store(mode='r')
    print("Ensure reading twice works -> ts.store(mode='r')")
    assert r == ts.data_vector("pandas_dataframe")

    r = ts.store(mode='d')
    print("ts.store(mode='d')")
    assert r

    r = ts.store(mode='w')
    print("ts.store(mode='w')")
    assert r

    r = ts.store(mode='r')
    print("ts.store(mode='r')")
    assert r == ts.data_vector("pandas_dataframe")

    r = ts.store(mode='d')
    print("ts.store(mode='d')")
    assert r

    # ---------------------------------------------------------02
    print("---------------------------------------------------------02")
    print("---------------------------------------------------------02.01")
    # pandas_dataframe_with_partition_cols
    r = ts.store_with_partition_cols(mode='rw', a=1, b=2)
    print("ts.store_with_partition_cols(mode='rw', a=1, b=2)")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector(
            "pandas_dataframe_with_partition_cols", a=1, b=2
        ).to_pandas().sort_index(axis=1)
    )

    r = ts.store_with_partition_cols(mode='r')
    print("ts.store_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector(
            "pandas_dataframe_with_partition_cols", a=1, b=2
        ).to_pandas().sort_index(axis=1)
    )

    r = ts.store_with_partition_cols(mode='d')
    print("ts.store_with_partition_cols(mode='d')")
    assert r

    print("---------------------------------------------------------02.02")
    r = ts.store_with_partition_cols(mode='w', a=1, b=22)
    print("ts.store_with_partition_cols(mode='w', a=1, b=22)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=33)
    print("ts.store_with_partition_cols(mode='w', a=1, b=33)")
    assert r

    r = ts.store_with_partition_cols(mode='r')
    print("ts.store_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=22
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=33
                ).to_pandas().sort_index(axis=1),
            ],
            ignore_index=True,
        )
    )

    r = ts.store_with_partition_cols(mode='r', a=1)
    print("ts.store_with_partition_cols(mode='r', a=1)")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=22
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=33
                ).to_pandas().sort_index(axis=1),
            ],
            ignore_index=True,
        )
    )

    r = ts.store_with_partition_cols(mode='r', a=1, b=22)
    print("ts.store_with_partition_cols(mode='r', a=1, b=22)")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector(
            "pandas_dataframe_with_partition_cols", a=1, b=22
        ).to_pandas().sort_index(axis=1),
    )

    r = ts.store_with_partition_cols(mode='e', a=1, b=22)
    print("ts.store_with_partition_cols(mode='r', a=1, b=22)")
    assert r

    r = ts.store_with_partition_cols(mode='e', a=1, b=33)
    print("ts.store_with_partition_cols(mode='r', a=1, b=33)")
    assert r

    r = ts.store_with_partition_cols(mode='e', a=1, b=55)
    print("ts.store_with_partition_cols(mode='r', a=1, b=55)")
    assert not r

    r = ts.store_with_partition_cols(mode='d', b=33)
    print("ts.store_with_partition_cols(mode='d', b=33)")
    assert r

    r = ts.store_with_partition_cols(mode='e', b=33)
    print("ts.store_with_partition_cols(mode='r', b=33)")
    assert not r

    r = ts.store_with_partition_cols(mode='r')
    print("ts.store_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        ts.data_vector(
            "pandas_dataframe_with_partition_cols", a=1, b=22
        ).to_pandas().sort_index(axis=1),
    )

    r = ts.store_with_partition_cols(mode='d')
    print("ts.store_with_partition_cols(mode='d')")
    assert r

    print("---------------------------------------------------------02.03")
    r = ts.store_with_partition_cols(mode='w', a=1, b=11)
    print("ts.store_with_partition_cols(mode='w', a=1, b=11)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=22)
    print("ts.store_with_partition_cols(mode='w', a=1, b=22)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=33)
    print("ts.store_with_partition_cols(mode='w', a=1, b=33)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=44)
    print("ts.store_with_partition_cols(mode='w', a=1, b=44)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=55)
    print("ts.store_with_partition_cols(mode='w', a=1, b=55)")
    assert r

    r = ts.store_with_partition_cols(mode='w', a=1, b=66)
    print("ts.store_with_partition_cols(mode='w', a=1, b=66)")
    assert r

    r = ts.store_with_partition_cols(
        mode='d', a=1, filters=[
            ('b', '=', '77')
        ]
    )
    print(
        """r = ts.store_with_partition_cols(
    mode='d', a=1, filters=[
        ('b', '=', '77')
    ]
)""")
    assert not r

    r = ts.store_with_partition_cols(
        mode='d', a=1, filters=[
            ('b', '<=', 55), ('b', '>', 22),
        ]
    )
    print(
        """r = ts.store_with_partition_cols(
    mode='d', a=1, filters=[
        ('b', '<=', 55), ('b', '>', 22),
    ]
)"""
    )
    assert r

    r = ts.store_with_partition_cols(mode='r')
    print("ts.store_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=11
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=22
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=1, b=66
                ).to_pandas().sort_index(axis=1),
            ],
            ignore_index=True,
        )
    )

    r = ts.store_with_partition_cols(mode='d', filters=[])
    print("ts.store_with_partition_cols(mode='d')")
    assert r

    r = ts.store_with_partition_cols(mode='d')
    print("ts.store_with_partition_cols(mode='d')")
    assert r

    # ---------------------------------------------------------03
    print("---------------------------------------------------------03")
    # pandas_dataframe_streamed

    r = ts.store_streamed(mode='a')
    print("ts.store_streamed(mode='a')")
    assert r

    r = ts.store_streamed(mode='a')
    print("ts.store_streamed(mode='a')")
    assert r

    r = ts.store_streamed(mode='a')
    print("ts.store_streamed(mode='a')")
    assert r

    r = ts.store_streamed(mode='r')
    print("ts.store_streamed(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas(),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe"
                ).to_pandas(),
                ts.data_vector(
                    "pandas_dataframe"
                ).to_pandas(),
                ts.data_vector(
                    "pandas_dataframe"
                ).to_pandas(),
            ],
            ignore_index=True
        )
    )

    r = ts.store_streamed(mode='d')
    print("ts.store_streamed(mode='d')")
    assert r

    # ---------------------------------------------------------04
    print("---------------------------------------------------------04")
    # pandas_dataframe_streamed_group_by

    r = ts.store_streamed_with_partition_cols(mode='a', a=11, b=22)
    print("ts.store_streamed_with_partition_cols(mode='a', a=11, b=22)")
    assert r

    r = ts.store_streamed_with_partition_cols(mode='a', a=33, b=44)
    print("ts.store_streamed_with_partition_cols(mode='a', a=33, b=44)")
    assert r

    r = ts.store_streamed_with_partition_cols(mode='a', a=55, b=66)
    print("ts.store_streamed_with_partition_cols(mode='a', a=55, b=66)")
    assert r

    r = ts.store_streamed_with_partition_cols(mode='r')
    print("ts.store_streamed_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=11, b=22
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=33, b=44
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=55, b=66
                ).to_pandas().sort_index(axis=1),
            ],
            ignore_index=True
        )
    )

    r = ts.store_streamed_with_partition_cols(mode='d', a=11)
    print("ts.store_streamed_with_partition_cols(mode='d', a=11)")
    assert r

    r = ts.store_streamed_with_partition_cols(mode='r')
    print("ts.store_streamed_with_partition_cols(mode='r')")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pd.concat(
            [
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=33, b=44
                ).to_pandas().sort_index(axis=1),
                ts.data_vector(
                    "pandas_dataframe_with_partition_cols", a=55, b=66
                ).to_pandas().sort_index(axis=1),
            ],
            ignore_index=True
        )
    )

    r = ts.store_streamed_with_partition_cols(mode='d')
    print("ts.store_streamed_with_partition_cols(mode='d')")
    assert r

    # ---------------------------------------------------------05
    print("---------------------------------------------------------05")
    # using data dict for dumping
    r = ts.store_with_data_kwarg(mode='w', epoch=10, data={'a': [22]})
    print("ts.store_with_data_kwarg(mode='w', epoch=10, data={'a': [22]})")
    assert r

    r = ts.store_with_data_kwarg(mode='r', epoch=10)
    print("ts.store_with_data_kwarg(mode='r', epoch=10)")
    pd.testing.assert_frame_equal(
        r.to_pandas().sort_index(axis=1),
        pa.table(
            {
                'epoch': [10],
                'a': [22]
            }
        ).to_pandas().sort_index(axis=1)
    )

    r = ts.store_with_data_kwarg(mode='d', epoch=10)
    print("ts.store_with_data_kwarg(mode='d', epoch=10)")
    assert r

    r = ts.store_with_data_kwarg(mode='d')
    print("ts.store_with_data_kwarg(mode='d')")
    assert r

    # ---------------------------------------------------------06
    print("---------------------------------------------------------06")
    # todo: add unittests for columns ... also data dict cannot take multiple
    #  columns
    print("check columns ... still todo")
    # using data dict for dumping
    # r = ts.store_with_data_kwarg(
    #     mode='w', epoch=1, data={'a': [1], 'b': [11]}
    # )
    # assert r
    # r = ts.store_with_data_kwarg(
    #     mode='w', epoch=2, data={'a': [2], 'b': [22]}
    # )
    # assert r
    # r = ts.store_with_data_kwarg(
    #     mode='w', epoch=3, data={'a': [3], 'b': [33]}
    # )
    # assert r
    #
    # r = ts.store_with_data_kwarg(mode='r')
    # print(r.to_pandas())
    #
    # r = ts.store_with_data_kwarg(mode='r', epoch=2)
    # print(r.to_pandas())
    #
    # r = ts.store_with_data_kwarg(mode='r', epoch=2, columns=['a'])
    # print(r.to_pandas())
    #
    # r = ts.store_with_data_kwarg(mode='d')
    # print("ts.store_with_data_kwarg(mode='d')")
    # assert r

    # ---------------------------------------------------------07
    print("---------------------------------------------------------07")
    # finally delete folder for hashable that has StoreFields
    ts.results_folder.store.delete()
    ts.results_folder.delete()
    print("ts.store_fields_folder.delete()")


def try_main():
    global _TEMP_PATH
    if _TEMP_PATH.exists():
        util.io_path_delete(_TEMP_PATH, force=True)
    _TEMP_PATH.mkdir(parents=True, exist_ok=True)
    _TEMP_PATH = _TEMP_PATH.resolve()
    # try_hashable_ser()
    # try_download_file()
    # try_auto_hashed_download_file()
    # try_metainfo_file()
    # try_creating_folders()
    try_arrow_storage()
    _TEMP_PATH.rmdir()


if __name__ == '__main__':
    try_main()
