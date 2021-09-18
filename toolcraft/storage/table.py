"""
Module related to data frame storage mostly designed using pyarrow file
systems and file formats

*** Writing and storing in streams ***
todo: Stream writes and reads from pyarrow to pandas Dataframe
  https://wesmckinney.com/blog/arrow-streaming-columnar/


*** Parquet vs Feather ***
todo: we will support both
  + parquet for long term storage of the analysis
  + feather for short term storage for analysis and building visualization
    server

https://stackoverflow.com/questions/48083405/what-are-the-differences-between-feather-and-parquet
'''
Parquet format is designed for long-term storage, where Arrow is more intended
for short term or ephemeral storage (Arrow may be more suitable for long-term
storage after the 1.0.0 release happens, since the binary format will be
stable then)

Parquet is more expensive to write than Feather as it features more layers of
encoding and compression. Feather is unmodified raw columnar Arrow memory. We
will probably add simple compression to Feather in the future.

Due to dictionary encoding, RLE encoding, and data page compression, Parquet
files will often be much smaller than Feather files

Parquet is a standard storage format for analytics that's supported by many
different systems: Spark, Hive, Impala, various AWS services, in future by
BigQuery, etc. So if you are doing analytics, Parquet is a good option as a
reference storage format for query by multiple systems

The benchmarks you showed are going to be very noisy since the data you read
and wrote is very small. You should try compressing at least 100MB or upwards
1GB of data to get some more informative benchmarks, see e.g.
http://wesmckinney.com/blog/python-parquet-multithreading/
'''

todo: explore `pds.Expression` and `pds.Dataset.scan`
"""


import typing as t
import pathlib
import dataclasses
import pyarrow as pa
import pyarrow.fs as pafs
import pyarrow.dataset as pds
import types
import operator
import time

from .. import util
from .. import error as e
from .. import marshalling as m
from .. import storage as s
from . import file_system as our_fs
from . import Folder

# noinspection PyUnresolvedReferences
if False:
    from . import store

_PARTITIONING = "hive"
# _FILE_FORMAT = pds.ParquetFileFormat()
# _FILE_FORMAT = pds.CsvFileFormat()
_FILE_FORMAT = pds.IpcFileFormat()


# see documentation for filters in pyarrow
# https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetDataset.html
FILTER_VALUE_TYPE = t.Union[int, float, str, set, list, tuple]
FILTER_OPS_TYPE = t.Literal[
    '=', '==', '<', '>', '<=', '>=', '!=', '&', '|', 'in', 'not in'
]
FILTER_TYPE = t.Tuple[
    str, FILTER_OPS_TYPE,
    FILTER_VALUE_TYPE
]
# Predicates are expressed in disjunctive normal form (DNF),
# like [[('x', '=', 0), ...], ...]
FILTERS_TYPE = t.List[t.Union[FILTER_TYPE, t.List[FILTER_TYPE]]]


# todo: check pds.Expression for more operations that are supported

_OP_MAPPER = {
    '=': operator.eq,
    '==': operator.eq,
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '!=': operator.ne,
    'and': operator.and_,
    'or': operator.or_,
    'in': lambda _x, _l: _x in _l,
    'not in': lambda _x, _l: _x not in _l,
    # todo: dont know how this will be used filter tuple that uses three
    #  elements
    # '~': lambda _x: ~x,
    # todo: not sure about this
    # 'not': lambda _x: ~x,
}

# do not try to reuse code for operators as we encounter problem of using
# last value while looping over dict _OP_MAPPER (loop rolling issue with python)
_OP_MAPPER_EXP = {
    '=': lambda _x, _y: operator.eq(pds.field(_x), pds.scalar(_y)),
    '==': lambda _x, _y: operator.eq(pds.field(_x), pds.scalar(_y)),
    '<': lambda _x, _y: operator.lt(pds.field(_x), pds.scalar(_y)),
    '>': lambda _x, _y: operator.gt(pds.field(_x), pds.scalar(_y)),
    '<=': lambda _x, _y: operator.le(pds.field(_x), pds.scalar(_y)),
    '>=': lambda _x, _y: operator.ge(pds.field(_x), pds.scalar(_y)),
    '!=': lambda _x, _y: operator.ne(pds.field(_x), pds.scalar(_y)),
    'and': lambda _x, _y: operator.and_(pds.field(_x), pds.scalar(_y)),
    'or': lambda _x, _y: operator.or_(pds.field(_x), pds.scalar(_y)),
    'in': lambda _x, _l: pds.field(_x).isin(_l),
    'not in': lambda _x, _l: operator.inv(pds.field(_x).isin(_l)),
    # todo: dont know how this will be used filter tuple that uses three
    #  elements
    # '~': lambda _x: operator.inv(pds.scalar(_x)),
    # todo: not sure about this
    # 'not': lambda _x: operator.inv(pds.scalar(_x)),
}


def bake_expression(
    _elements: t.List, _err_msg, _columns_allowed=None,
    # todo: support validation against schema later ...
    #  + check `pds.Expression.is_valid` and `pds.Expression.validate`
    _schema=None,
) -> t.Optional[pds.Expression]:
    # ---------------------------------------------------01
    # if None return
    if _elements is None:
        return None

    # ---------------------------------------------------02
    # some references
    _expression = None

    # ---------------------------------------------------02
    # we always expect list and loop over it here
    for _element in _elements:
        # -----------------------------------------------02.01
        # if list recursion
        if isinstance(_element, list):
            # todo: remove this limitation when we understand DNF queries
            #   that is add support for filters that are nested lists
            e.code.NotSupported(
                msgs=[
                    f"We will support nested filters list once we figure out "
                    f"how DNF queries work ..."
                ]
            )
            for _e in _element:
                _r = bake_expression(_e, _err_msg, _columns_allowed, _schema)
                if _expression is None:
                    _expression = _r
                else:
                    # assuming that the the filters from nested list get
                    # `and`ed with other elements in list
                    _expression = operator.and_(_expression, _r)
        # -----------------------------------------------02.02
        # if tuple bake expression
        elif isinstance(_element, tuple):
            # -------------------------------------------02.02.01
            # basic validations
            # check if three elements
            if len(_element) != 3:
                e.validation.NotAllowed(
                    msgs=[
                        _err_msg,
                        f"We expect filters that are tuples and "
                        f"made of three elements",
                        f"Check unsupported tuple {_element}",
                    ]
                )
            # validate first element
            e.validation.ShouldBeInstanceOf(
                value=_element[0], value_types=(str, ),
                msgs=[
                    _err_msg,
                    f"The first element of every filter tuple should be a str"
                ]
            )
            # validate first element if it is one of _columns_allowed if
            # supplied
            if _columns_allowed is not None:
                e.validation.ShouldBeOneOf(
                    value=_element[0],
                    values=_columns_allowed,
                    msgs=[
                        _err_msg,
                        f"Filter cannot be used on column {_element[0]}",
                        f"You can use filters only on below columns: ",
                        _columns_allowed,
                    ]
                )
            # validate second element
            # noinspection PyUnresolvedReferences
            e.validation.ShouldBeOneOf(
                value=_element[1],
                values=FILTER_OPS_TYPE.__args__,
                msgs=[
                    _err_msg,
                    "Invalid query string used for filter tuple ..."
                ]
            )
            # validate third element
            # noinspection PyUnresolvedReferences
            e.validation.ShouldBeInstanceOf(
                value=_element[2],
                value_types=FILTER_VALUE_TYPE.__args__,
                msgs=[
                    _err_msg,
                    f"PyArrow filters kwarg tuple do not understand numpy "
                    f"or other types",
                ]
            )
            # -------------------------------------------02.02.02
            # bake expression for tuple
            _exp = _OP_MAPPER_EXP[_element[1]](
                _element[0], _element[2]
            )
            # -------------------------------------------02.02.04
            # make global expression
            if _expression is None:
                _expression = _exp
            else:
                # assuming that the the filters from nested list get
                # `and`ed with other elements in list
                _expression = operator.and_(_expression, _exp)
        # -----------------------------------------------02.03
        # else not supported
        else:
            e.code.ShouldNeverHappen(
                msgs=[
                    _err_msg,
                    f"We only support filters that are tuples "
                    f"with three elements or the list of those "
                    f"three element tuples",
                    f"Found type {type(_element)}",
                ]
            )

    # ---------------------------------------------------03
    # return
    return _expression


# noinspection PyArgumentList
def _read_table(
    df_file: "Table",
    columns: t.List[str],
    filter_expression: pds.Expression,
    partitioning: pds.Partitioning,
    table_schema: pa.Schema,
) -> pa.Table:
    """
    todo: need to find a way to preserve indexes while writing or
     else find a way to read with sort with pyarrow ... then there
     will be no need to use to_pandas() and also no need ofr casting
    """
    # noinspection PyProtectedMember
    _table = pa.Table.from_batches(
        batches=pds.dataset(
            source=df_file.path.as_posix(),
            filesystem=df_file.file_system,
            format=_FILE_FORMAT,
            schema=table_schema,
            partitioning=partitioning,
        ).to_batches(
            columns=columns,
            filter=filter_expression,
        ),
        schema=table_schema,
    )

    # todo: should we reconsider sort overhead ???
    # return self.file_type.deserialize(
    #     _table
    # ).sort_index(axis=0)
    return _table


def _write_table(
    df_file: "Table",
    table: pa.Table,
    partitioning: pds.Partitioning,
):
    # file name formatter
    _file_name = str(time.time_ns()) + ".{i}"

    # we introduce 1 micro second delay so that file names remain unique in
    # nano seconds
    time.sleep(1.0 / 1000000.0)

    # write to disk
    # noinspection PyProtectedMember
    pds.write_dataset(
        data=table,
        base_dir=df_file.path.as_posix(),
        filesystem=df_file.file_system,
        partitioning=partitioning,
        format=_FILE_FORMAT,
        # todo: modify in future if append writes are supported by pyarrow
        #  right now this is our solution
        #  + we use timestamp that is unique for every write while `i` will
        #    record the the ith file that was written for this disk
        #
        # todo: side effect we can use timestamp i.e. name as file to achieve
        #  timestamp based streaming ;)
        basename_template=_file_name,
    )


class TableInternal(m.Internal):

    partitioning: t.Optional[pds.Partitioning]
    schema: t.Optional[pa.Schema]
    partition_cols: t.Optional[t.List[str]]

    @property
    def is_updated(self) -> bool:
        """
        Any one internal present means all will be present ...
        """
        return self.has("partitioning")

    def update_from_table_or_config(
        self, table: t.Optional[pa.Table]
    ):
        """
        We want to save some things in internal for faster access as going
        through config will need with context and unnecessary sync process.

        If first write happens that means table is provided. In that case if
        schema is provided by StoreField decorator we validate the schema on
        first write. While if schema is not provided we infer it from table.

        If table is None that means this is happening while object is created
        and in that case if data exists on disk then we load schema from config
        on disk. Else we set things to None
        """
        # schema from config
        # noinspection PyUnresolvedReferences
        _c = self.owner.config
        _schema_in_config = _c.schema

        # if table is provided that means either validate schema if schema
        # in config or else infer schema from table and sync that to
        # config to disk for future use
        if table is not None:
            # check if table has all the partition columns ... this needs
            # to be checked when the returned table by decorated method
            # misses out on certain columns that are needed for partitions
            _tables_cols = [_.name for _ in table.schema]
            _partition_cols = _c.partition_cols
            if _partition_cols is None:
                _partition_cols = []
            for _col in _partition_cols:
                if _col not in _tables_cols:
                    e.code.CodingError(
                        msgs=[
                            f"While returning pa.Table from the decorated "
                            f"method you missed to add important partition "
                            f"column `{_col}`"
                        ]
                    )

            # if table_schema none estimate from first table and write it
            # back to config
            if _schema_in_config is None:
                _c.schema = table.schema
            # if table_schema available then validate
            else:
                if _schema_in_config != table.schema:
                    e.code.CodingError(
                        msgs=[
                            f"The yielded/returned table schema is "
                            f"not valid",
                            {
                                "expected": _schema_in_config,
                                "found": table.schema
                            }
                        ]
                    )
        # if table is None and this method is called we expect the schema to
        # be available in config file ... check for config file and raise
        # error if table schema not available
        else:
            # if table schema in config is none raise error
            if _schema_in_config is None:
                e.code.CodingError(
                    msgs=[
                        f"We cannot update internals as you have not "
                        f"supplied table nor there is schema definition "
                        f"available in config which should be either "
                        f"supplied by user via StoreField decorator or "
                        f"inferred from table written on the disk."
                    ]
                )

        # update internal for faster access later
        self.partitioning = _c.get_partitioning()
        self.schema = _c.schema
        self.partition_cols = _c.partition_cols


@dataclasses.dataclass
class TableConfig(s.Config):

    schema: t.Optional[t.Dict] = None
    partition_cols: t.Optional[t.List[str]] = None

    def get_partitioning(self) -> t.Optional[pds.Partitioning]:
        if self.schema is None:
            e.code.CodingError(
                msgs=[
                    f"Ideally by now this should be set by now if not "
                    f"available",
                    f"That is possible on first write where table schema not "
                    f"provided it is estimated while writing and stored in "
                    f"config file"
                ]
            )
        if self.partition_cols is None:
            return None
        # noinspection PyUnresolvedReferences
        return pds.partitioning(
            self.schema.empty_table().select(self.partition_cols).schema
        )


# noinspection PyDataclass
@dataclasses.dataclass(frozen=True)
class Table(Folder):
    """
    This means files storage for Data frames i.e. for columnar data.
    Although it is named Table we extend Folder to implement this because of
    Hive formatting where we have folders for columns.

    Every Dataframe is a Folder:
      It might surprise you that we are inheriting Folder instead of FileGroup.
      This is because Dataframe is save in folders because of hive
      partitioning. And we treat this folder as Dataframe file. Where the root
      folder has our *.info file and *.config file where we store more
      information about Dataframe and its schema.

    Note that file_df.py combines the power of file_system.py plus
    additional things like write append read exists with filters etc ;)
    specifically designed to achieve modern columnar storage requirements.

    todo: While file_group.py is for blob storage. In future we can enable it to
      use file_system.py (with no need for write, append filters like
      database features). This will nicely handle blob storage requirements as
      well as columnar storage for analytics. While data can move across
      multiple file systems.
      ...
      This might feel less priority as the main job of file_group will be to
      move data on internal servers rather than moving data on cloud for
      analytics. But we can think of scenarios where we might push big files
      on cloud storage.

    Note:
        Have a strong reason to override file_system related methods or read
        write exists based file methods to be overriden in child class of
        FileDf ... the sole purpose of subclasses to provide extra arguments
        and do extra validations when required.
    """

    # we override type as this is always method name which was decorated with
    # StoreField
    for_hashable: str
    parent_folder: "store.StoreFieldsFolder"

    @property
    @util.CacheResult
    def config(self) -> TableConfig:
        return TableConfig(
            hashable=self, path_prefix=self.path.as_posix()
        )

    @property
    @util.CacheResult
    def internal(self) -> TableInternal:
        return TableInternal(self)

    @property
    def contains(self) -> None:
        # although default we make sure that this is overridden
        # we know that the Table folder will have unmanageable content
        # managed by pyarrow
        return None

    @property
    def uses_parent_folder(self) -> bool:
        return True

    @property
    def file_system(self) -> t.Union[
        pafs.FileSystem,
        # todo: eventually this needs to be migrated tp `pafs.FileSystem` as
        #   `pa.filesystem.FileSystem` will be deprecated by pyarrow
        pa.filesystem.FileSystem,
    ]:
        # todo: currently only local file system .... we need to plan other
        #  file systems later ...
        # todo: for local we are going with singleton pattern
        return our_fs.LocalFileSystem.get_instance()

    def init_validate(self):
        # call super
        super().init_validate()

        # make sure that for_hashable is str as in super class it
        # can be even HashableClass and that cannot be tolerated here
        if not isinstance(self.for_hashable, str):
            e.code.NotAllowed(
                msgs=[
                    f"We only allow for_hashable to be a str as this is "
                    f"Table.",
                    f"Most likely for_hashable is name of method on which "
                    f"StoreField decorator was used.",
                ]
            )

    def init(self):
        # call super
        super().init()

        # if config has table_schema update internal from config on disk
        # Note that in case the schema was not provided via StoreField
        # decorator we still infer schema on first write and store it in
        # *.config file ... Here if it is available from previous writes on
        # disk we can fetch it
        _s = self.config.schema
        if _s is not None:
            self.internal.update_from_table_or_config(table=None)

    def exists(
        self,
        columns: t.List[str],
        filter_expression: pds.Expression,
        return_table: bool,
    ) -> t.Union[bool, pa.Table]:
        """
        This is weird design choice here to return table when filters are
        used. This is just to avoid multiple data reads. Anyways you can
        easily avoid using already fetched tables by casting them using
        bool(...) ... Note that is is not possible to use filters without
        actually reading data.

        While filters are not provide and if something present we return True
        and not the Table.

        When filters=None we will get simple exists check ... i.e. True or
        False will be returned and no data on the disk will be read ;)
        """
        # if nothing exists simply exit ... as there is no table to read on disk
        # noinspection PyTypeChecker
        if not self.file_system.exists(self.path):
            return False
        # if folder exists but empty then return False
        if util.io_is_dir_empty(self.path):
            return False
        # read table with filters to see if something exists
        # Note that columns is None as it is irrelevant while checking for
        # exists as we will use filters and check if minimum one row is
        # returned or not ... and at that time it does not matter which
        # column we select in that row
        _table = _read_table(
            self, columns=columns, filter_expression=filter_expression,
            table_schema=self.internal.schema,
            partitioning=self.internal.partitioning,
        )
        # return Table if one or more rows exist else return False
        if return_table:
            return _table if len(_table) > 0 else False
        else:
            return bool(_table)

    # Note that the parent delete is for Folder but for Table also we have
    # folder which represents folder and we will take care of the delete. But
    # note that this delete is special with `filters` argument while `force`
    # argument will have no purpose.
    # noinspection PyMethodOverriding
    def delete_(
        self, *, filters: FILTERS_TYPE,
    ) -> bool:
        """
        Note that this is not Folder.delete but delete related to mode=`d`

        IMPORTANT:
        This delete_ with filters=None will delete all contents of
        StoreFieldsFolder but will keep the empty dir and its state files
        intact. While delete acts like normal Folder.delete() and is also
        responsible to delete state files and empty dirs.

        Note that delete is not supported by pyarrow so we have our own
        implementation. We expect simple filters that can resolve to folder
        paths that we can delete. To achieve this we use _columns_allowed
        argument of method of _check_filters.

        Given that we will use columns that use partition_cols we can be
        sure that there are files or folders to delete. And that is the
        reason why we do not allow columns apart from partition columns.

        Also looks like this code should work on file written in batches. But
        in case we use columns apart from partition cols that might be
        difficult to achieve.

        todo: for writes with one row per file we can delete based on columns
          that are not partition columns .... check if we can support it in
          future
        """
        # ------------------------------------------------------01
        # if filters=None then delete everything
        # Note that this is with mode i.e. we are in delete_ not delete
        # method... the job here is only to delete pyarrow data and not to
        # take over job of Folder.delete ... so once things are deleted we
        # keep intact the empty folder ...
        # DO NOT BE TEMPTED .... to call delete which deletes the state file
        # this is because consecutive writes will work but since they do not
        # use create method of Folder the state files will not be generated
        # ... also that is never the job of delete_ as it only is responsible
        # for pyarrow stuff and not the Folder stuff
        if not bool(filters):
            # noinspection PyTypeChecker
            self.file_system.delete(self.path, recursive=True)
            # just make a empty dir again fo that things are consistent for
            # Folder class i.e. is_created can detect things properly
            self.path.mkdir()
            # return need to satisfy the API
            return True

        # ------------------------------------------------------02
        # basic tests
        # for now we expect simple filters i.e. list of tuples ... we do not
        # support nested list of filters yet
        # todo: add support for filters that are nested lists
        for f in filters:
            if isinstance(f, list):
                e.code.NotAllowed(
                    msgs=[
                        f"For delete mode we support simple filters that "
                        f"operate on partition columns ... nested "
                        f"filters is not yet supported ..."
                    ]
                )
        # some vars
        _partition_cols = self.internal.partition_cols

        # ------------------------------------------------------03
        # loop over filters and make a dictionary with key as partition
        # column and value as the list of tuple (operation, value)
        # todo: I hope this handles the use case of multiple filters over same
        #  column properly
        _filters_dict_of_op_val_list = {
            pc: [] for pc in _partition_cols
        }
        for f in filters:
            _filters_dict_of_op_val_list[f[0]].append((_OP_MAPPER[f[1]], f[2]))

        # ------------------------------------------------------04
        # deletion helper method

        def _delete(_depth: int, _path: pathlib.Path) -> bool:
            # --------------------------------------------------04.01
            # variable to track if something deleted
            _something_deleted = False

            # --------------------------------------------------04.02
            # the path must be a dir
            if not _path.is_dir():
                e.code.CodingError(
                    msgs=[
                        f"We were expecting path {_path} to be a dir ..."
                    ]
                )

            # --------------------------------------------------04.03
            # expect partition column
            _pc_exp = _partition_cols[_depth]

            # --------------------------------------------------04.04
            # increment depth for further recursion if needed
            _depth += 1

            # --------------------------------------------------04.05
            # get filters for this partition column
            _filters_op_val_list = _filters_dict_of_op_val_list[_pc_exp]

            # --------------------------------------------------04.06
            # crawl over folder for partition cols
            for _nested_path in _path.iterdir():

                # ----------------------------------------------04.06.01
                # should be a dir
                if not _nested_path.is_dir():
                    e.code.CodingError(
                        msgs=[
                            f"We were expecting folder ..."
                        ]
                    )

                # ----------------------------------------------04.06.02
                # todo: sometimes the folder names are like
                #  <column_name>=<_val> and sometimes the folder names are
                #  just value of columns ... this may be because of new
                #  pyarrow version or may be because we supply schema
                #  everywhere appropriately
                # # get tokens from folder name
                # _pc, _val = _nested_path.name.split("=")
                # # the _pc from folder name should match expected partition
                # # column
                # if _pc != _pc_exp:
                #     e.code.CodingError(
                #         msgs=[
                #             f"We were expecting all folder names to start "
                #             f"with expected partition column name {_pc_exp}, "
                #             f"instead found it to be {_pc}"
                #         ]
                #     )
                # todo: this is when folder name is just column value
                _val = _nested_path.name
                try:
                    # note that if int then becomes float bit that is okay with
                    # expression matching in python
                    _val = float(_val)
                except ValueError:
                    # nothing to do if exception it remains string
                    ...

                # ----------------------------------------------04.06.03
                # check if nested dir satisfies the criterion for deletion
                # based on the filters
                # If filters are provided check filters and then decide if
                # nested path needs to be deleted or not
                if bool(_filters_op_val_list):
                    _del = True  # flag
                    for _op, _val1 in _filters_op_val_list:
                        # Note that _filters_op_val_list is for specific _pc
                        # so when all filter conditions we can delete if any
                        # one is False then do not delete
                        try:
                            _del &= _op(_val, _val1)
                        except TypeError:
                            e.code.CodingError(
                                msgs=[
                                    f"Check supplied filters",
                                    f"Operation {_op} cannot be applied on "
                                    f"values {(_val, _val1)} with type "
                                    f"{(type(_val), type(_val1))}"
                                ]
                            )
                        # quick break
                        if not _del:
                            break
                # if no filters for the partition column then all child
                # folders are eligible for delete as no filter is applied
                else:
                    _del = True

                # ----------------------------------------------04.06.04
                # if _del then delete
                if _del:
                    # if last partition delete the folder
                    if _pc_exp == _partition_cols[-1]:
                        # delete
                        # noinspection PyTypeChecker
                        self.file_system.delete(
                            _nested_path, recursive=False)
                        # if nested path is empty the delete empty dir
                        # todo: can this be optimized ??
                        if _nested_path.exists():
                            if util.io_is_dir_empty(_nested_path):
                                _nested_path.unlink()
                        # update global flag
                        _something_deleted |= True
                    # else call the method in recursion
                    else:
                        _something_deleted |= \
                            _delete(_depth=_depth, _path=_nested_path)

            # --------------------------------------------------04.07
            # return
            return _something_deleted

        # ------------------------------------------------------05
        # call recursive function and track if deleted
        _is_something_deleted = _delete(_depth=0, _path=self.path)

        # ------------------------------------------------------06
        # return True ... anyways when it reaches till here
        # _is_something_deleted will be True
        return _is_something_deleted

    def read(
        self,
        columns: t.List[str],
        filter_expression: pds.Expression,
    ) -> pa.Table:
        # this should always be there and would be known even if not provided
        # on first write
        _partitioning = self.internal.partitioning
        _schema = self.internal.schema

        # read table
        _table = _read_table(
            self, columns=columns, filter_expression=filter_expression,
            partitioning=_partitioning,
            table_schema=_schema
        )

        # extra check
        if len(_table) == 0:
            e.code.ShouldNeverHappen(
                msgs=[
                    "The exists check before read call should handled it.",
                    "Found a empty table while reading",
                    f"Please do not use `.` or `_` at start of any folder in "
                    f"the path as the pyarrow does not raise error but reads "
                    f"empty table.",
                    f"Check path {self.path}"
                ]
            )

        # return
        return _table

    def append(
        self,
        value: t.Union[pa.Table, types.GeneratorType],
        yields: bool,
    ) -> bool:
        # is value a generator type
        _is_generator_type = isinstance(value, types.GeneratorType)

        # check if yields value should be generator
        if yields:
            if not _is_generator_type:
                e.validation.NotAllowed(
                    msgs=[
                        f"Are you using return ?? ... ",
                        f"We expect you to yield"
                    ]
                )
        else:
            if _is_generator_type:
                e.validation.NotAllowed(
                    msgs=[
                        f"Are you using yield ?? ... ",
                        f"We expect you to return"
                    ]
                )

        # check if partition columns exist in table that is to be
        # written to disk
        # todo: this check is inefficient especially for append writes
        # todo: this check works when `yields=False` but when `yields=True`
        #  this fails as value is generator. For now we comment this check
        #  will take action later ... NOT A PRIORITY
        # if self.partition_cols is not None:
        #     for pc in self.partition_cols:
        #         if pc not in value.column_names:
        #             e.code.CodingError(
        #                 msgs=[
        #                     f"We expect you to supply mandatory column "
        #                     f"`{pc}` in the returned/yielded pyarrow table."
        #                 ]
        #             )

        # if not generator make it iterator so that looping happens once
        if not _is_generator_type:
            # todo: Is this efficient ???
            value = [value]

        # get iterator
        _iterator = iter(value)

        # get first element
        _table = next(_iterator)  # type: pa.Table

        # if not pa.Table then raise error
        if not isinstance(_table, pa.Table):
            e.code.CodingError(
                msgs=[
                    f"We expect the decorated method to return {pa.Table} "
                    f"but instead found return value of type {type(_table)}"
                ]
            )

        # get schema if in config else get schema from table and write
        # back to config
        if not self.internal.is_updated:
            # now update as config is updated
            self.internal.update_from_table_or_config(table=_table)

        # get partitioning
        _partitioning = self.internal.partitioning

        # default behaviour is to append .... if you do not want that
        # please call self.delete() before calling this
        # write first element
        _write_table(self, _table, _partitioning)
        # now write remaining
        for _table in _iterator:
            _write_table(self, _table, _partitioning)

        # we do not return what we just wrote
        # for append and write we return True to avoid huge reads ....
        # just use read Mode to get the values
        # return bool
        return True
