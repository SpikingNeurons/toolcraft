"""
Module related to data frame storage mostly designed using pyarrow file
systems and file formats

todo: make table use file_system with this interface
  https://arrow.apache.org/docs/python/filesystems.html#using-fsspec-compatible-filesystems-with-arrow
  All this is made possible via FSSpecHandler
  https://arrow.apache.org/docs/python/generated/pyarrow.fs.FSSpecHandler.html
  Note that we can also stram data via pyarrow so that jobs on server can write
  while client can read

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

todo: we use table as counterpart to mlflow metrics ... we have more options here for
  fast analytics due to underlying pivot based columnar storage ... we will also
  explore aggregating multiple tables from different HashableClass instances with same HashableClass
"""


import typing as t
import pathlib
import dataclasses
import pyarrow as pa
import pyarrow.dataset as pds
import types
import itertools
import operator
import time

from .. import util
from .. import error as e
from .. import marshalling as m
from .. import storage as s
from . import Folder

# noinspection PyUnresolvedReferences
if False:
    from . import store

# _PARTITIONING = "hive"
# _FILE_FORMAT = pds.ParquetFileFormat()
# _FILE_FORMAT = pds.CsvFileFormat()
_FILE_FORMAT = pds.IpcFileFormat()


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


class Filter(t.NamedTuple):
    """
    see documentation for filters in pyarrow
    https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetDataset.html

    Predicates are expressed in disjunctive normal form (DNF),
    like [[('x', '=', 0), ...], ...]
    """
    column: str
    op_type: t.Literal[
        '=', '==', '<', '>', '<=', '>=', '!=', '&', '|', 'in', 'not in',
        # '~', 'not',
    ]
    value: t.Union[bool, int, float, str, set, list, tuple]

    @property
    def expression(self) -> pds.Expression:
        return _OP_MAPPER_EXP[self.op_type](self.column, self.value)


# Predicates are expressed in disjunctive normal form (DNF),
# like [[('x', '=', 0), ...], ...]
# list of tuples act like and expression
# list of lists act like or expression
# todo: dont know what happens with list of lista and tuples
FILTERS_TYPE = t.List[t.Union[Filter, t.List[Filter]]]


def make_expression(
    filters: FILTERS_TYPE, restrict_columns: t.List[str] = None
) -> pds.Expression:
    """
    Predicates are expressed in disjunctive normal form (DNF),
    like [[('x', '=', 0), ...], ...]
    list of tuples act like and expression
    list of lists act like or expression
    todo: dont know what happens with list of lista and tuples

    _expression = operator.and_(_expression, _exp)
    """
    # ---------------------------------------------------- 01
    # validate
    e.validation.ShouldBeInstanceOf(
        value=filters, value_types=(list, ),
        msgs=["Was expecting list type for filters"]
    ).raise_if_failed()

    # ---------------------------------------------------- 02
    # loop
    _ret_exp = None
    for _filter in filters:
        if isinstance(_filter, list):
            _exp = make_expression(_filter)
            if _ret_exp is None:
                _ret_exp = _exp
            else:
                _ret_exp = operator.or_(_ret_exp, _exp)
        elif isinstance(_filter, Filter):
            if bool(restrict_columns):
                e.validation.ShouldBeOneOf(
                    value=_filter.column, values=restrict_columns,
                    msgs=["You should use one of restricted columns ..."]
                ).raise_if_failed()
            _exp = _filter.expression
            if _ret_exp is None:
                _ret_exp = _exp
            else:
                _ret_exp = operator.and_(_ret_exp, _exp)
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown type {type(_filter)}"])

    # ---------------------------------------------------- 03
    # return
    return _ret_exp


# noinspection PyArgumentList
def _read_table(
    table_as_folder: "Table",
    columns: t.List[str],
    filter_expression: pds.Expression,
    partitioning: pds.Partitioning,
    table_schema: pa.Schema,
) -> pa.Table:
    """
    Refer: https://arrow.apache.org/docs/python/dataset.html#dataset

    todo: need to find a way to preserve indexes while writing or
     else find a way to read with sort with pyarrow ... then there
     will be no need to use to_pandas() and also no need ofr casting
    """
    if bool(columns):
        table_schema = pa.schema(
            fields=[table_schema.field(_c) for _c in columns],
            metadata=table_schema.metadata
        )
    # noinspection PyProtectedMember
    _path = table_as_folder.path
    _table = pa.Table.from_batches(
        batches=pds.dataset(
            source=_path.full_path,
            filesystem=_path.fs,
            format=_FILE_FORMAT,
            schema=table_schema,
            partitioning=partitioning,
        ).to_batches(
            # todo: verify below claim and test if this will remain generally correct
            # using filters like columns and filter_expression here is more efficient
            # as it applies for per batch loaded rather than loading entire table and
            # then applying filters
            columns=columns,
            filter=filter_expression,
        ),
        # if column is specified table_schema will change as some columns will
        # disappear ... so we set to None
        # todo: check how to drop remaining columns from table_schema
        schema=table_schema,
    )

    # todo: should we reconsider sort overhead ???
    # return self.file_type.deserialize(
    #     _table
    # ).sort_index(axis=0)
    return _table


def _write_table(
    table_as_folder: "Table", table: pa.Table, append: bool,
    delete_partition: bool = False,
):
    # file name formatter
    # note you might confuse with (i) ... looks like it is used by pyarrow internals
    # when instead of pa.Table we will be saving batches ...
    # todo: explore usage of `.{i}` ...
    #  applicable for both e `Table.append` and `Table.write`
    if append:
        # this also helps time stamp based append
        _file_name = str(time.time_ns()) + ".{i}"
        # we introduce 1 micro second delay so that file names remain unique in
        # nanoseconds
        time.sleep(1.0 / 1000000.0)
    else:
        _file_name = "data.{i}"

    # if anything encountered then delete it ... useful with append write as can
    # delete entire partition folder ... while in write mode this will have same
    # behaviour
    if delete_partition:
        _existing_data_behavior = 'delete_matching'
    else:
        _existing_data_behavior = "overwrite_or_ignore"

    # get partitioning
    _partitioning = table_as_folder.partitioning

    # write to disk
    _path = table_as_folder.path
    # noinspection PyProtectedMember
    pds.write_dataset(
        data=table,
        base_dir=_path.full_path,
        filesystem=_path.fs,
        partitioning=_partitioning,
        format=_FILE_FORMAT,
        basename_template=_file_name,
        existing_data_behavior=_existing_data_behavior,
    )


class _TableInternal(m.Internal):

    partitioning: t.Optional[pds.Partitioning]
    schema: t.Optional[pa.Schema]
    partition_cols: t.Optional[t.List[str]]

    @property
    def is_updated(self) -> bool:
        """
        Any one internal present means all will be present ...
        """
        return self.has("partitioning")


@dataclasses.dataclass
class TableConfig(s.Config):
    schema: t.Optional[pa.Schema] = None

    def update_schema(
        self, table: pa.Table = None
    ):
        # ------------------------------------------------------------- 01
        # if table is not provided we expect that schema is already available
        if table is None:
            if self.schema is None:
                raise e.code.CodingError(
                    msgs=[
                        f"We cannot guess schema as you have not "
                        f"supplied table nor there is schema definition "
                        f"available in config which should be either "
                        f"supplied by user or guessed while first write."
                    ]
                )
            return

        # ------------------------------------------------------------- 02
        # else table is provided so get schema from it and update config
        # if table is provided that means either validate schema if schema
        # in config or else infer schema from table and sync that to
        # config to disk for future use
        # ------------------------------------------------------------- 02.01
        # check if table has all the partition columns ... this needs
        # to be checked when the returned table by decorated method
        # misses out on certain columns that are needed for partitions
        _tables_cols = [_.name for _ in table.schema]
        _partition_cols = self.hashable.partition_cols
        if _partition_cols is None:
            _partition_cols = []
        for _col in _partition_cols:
            if _col not in _tables_cols:
                raise e.code.CodingError(
                    msgs=[
                        f"The pa.Table provided do not have important partition "
                        f"column `{_col}`"
                    ]
                )
        # ------------------------------------------------------------- 02.02
        # if table_schema none estimate from first table and write it
        # back to config
        if self.schema is None:
            self.schema = table.schema
            return
        # if table_schema available then validate
        else:
            if self.schema != table.schema:
                raise e.code.CodingError(
                    msgs=[
                        f"The table schema is "
                        f"not valid",
                        {
                            "expected": self.schema,
                            "found": table.schema
                        }
                    ]
                )
            return


# noinspection PyDataclass
@dataclasses.dataclass(frozen=True)
class Table(Folder):
    """
    We refer
    https://arrow.apache.org/docs/python/filesystems.html#using-fsspec-compatible-filesystems-with-arrow

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

    todo: get rid of info and config files if needed but then Table will no
      longer be Folder. Explore using pyarrow metadata feature
      https://stackify.dev/292501-how-to-assign-arbitrary-metadata-to-pyarrow-table-parquet-columns
    """

    # we override type as this is always method name which was decorated with
    # StoreField
    for_hashable: str
    parent_folder: "store.StoreFieldsFolder"
    partition_cols: t.List[str] = None

    @property
    @util.CacheResult
    def config(self) -> TableConfig:
        return TableConfig(
            hashable=self,
        )

    @property
    @util.CacheResult
    def partitioning(self) -> t.Optional[pds.Partitioning]:
        if self.partition_cols is None:
            return None
        _schema = self.config.schema
        if _schema is None:
            raise e.code.CodingError(
                msgs=[
                    f"Ideally by now this should be set by now if not "
                    f"available",
                    f"That is possible on first write where table schema not "
                    f"provided it is estimated while writing and stored in "
                    f"config file"
                ]
            )
        # noinspection PyUnresolvedReferences
        return pds.partitioning(
            _schema.empty_table().select(self.partition_cols).schema
        )

    def init_validate(self):
        # call super
        super().init_validate()

        # make sure that for_hashable is str as in super class it
        # can be even HashableClass and that cannot be tolerated here
        if not isinstance(self.for_hashable, str):
            raise e.code.NotAllowed(
                msgs=[
                    f"We only allow for_hashable to be a str as this is "
                    f"Table.",
                    f"Most likely for_hashable is name of method on which "
                    f"StoreField decorator was used.",
                ]
            )

    def something_exists(self) -> bool:
        """
        A faster version of exists with no columns or filter_expression kwargs
        Useful when only used for write ...
        """
        if not self.path.exists():
            return False
        if self.path.is_dir_empty():
            return False
        return True

    def exists(
        self,
        columns: t.List[str] = None,
        filter_expression: pds.Expression = None,
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
        if not self.path.exists():
            return False
        if self.path.is_dir_empty():
            return False

        # this should always be there as above check suggests that something
        # is already there
        _partitioning = self.partitioning
        _schema = self.config.schema
        assert _schema is not None  # todo remove later

        # read table
        _table = _read_table(
            self, columns=columns, filter_expression=filter_expression,
            partitioning=_partitioning,
            table_schema=_schema
        )

        # return
        return _table

    def read(
        self,
        columns: t.List[str] = None,
        filter_expression: pds.Expression = None,
    ) -> t.Optional[pa.Table]:
        # log
        _rp = self.richy_panel
        _rp.update(f"reading for {self.__class__}")

        # if nothing exists simply exit ... as there is no table to read on disk
        # noinspection PyTypeChecker
        if not self.path.exists():
            return None
        if self.path.is_dir_empty():
            return None

        # this should always be there as above check suggests that something
        # is already there
        _partitioning = self.partitioning
        _schema = self.config.schema
        assert _schema is not None  # todo remove later

        # read table
        _table = _read_table(
            self, columns=columns, filter_expression=filter_expression,
            partitioning=_partitioning,
            table_schema=_schema
        )

        # extra check
        if len(_table) == 0:
            raise e.code.ShouldNeverHappen(
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

    def write(self, value: pa.Table) -> bool:
        # log
        _rp = self.richy_panel
        _rp.update(f"writing for {self.__class__}")

        # make sure if some partition folders exists ...
        # applicable when partition_cols present
        if bool(self.partition_cols):
            _unique_filters = [
                [Filter(_pc, "=", _v) for _v in value[_pc].unique().tolist()]
                for _pc in self.partition_cols
            ]
            _filters = [list(_) for _ in itertools.product(*_unique_filters)]
            _table = self.exists(
                columns=self.partition_cols,
                filter_expression=make_expression(_filters))
            if _table:
                e.validation.NotAllowed(
                    msgs=[
                        "Below partition col values already exist",
                        _table.to_pydict()
                    ]
                )

        # if schema is None update it
        if self.config.schema is None:
            self.config.update_schema(table=value)

        # write
        _write_table(self, table=value, append=False)

        # return success
        return True

    def append(self, value: pa.Table, delete_partition: bool = False) -> bool:
        """
        delete_partition:
          makes it possible to delete the folder for pivot and overwrite it completely
          note that all appends will be wiped ...
        """
        # log
        _rp = self.richy_panel
        _rp.update(f"appending for {self.__class__}")

        # if schema is None update it
        if self.config.schema is None:
            self.config.update_schema(table=value)

        # write
        _write_table(self, table=value, delete_partition=delete_partition, append=True)

        # return success
        return True

    # Note that the parent delete is for Folder but for Table also we have
    # folder which represents folder and we will take care of the delete. But
    # note that this delete is special with `filters` argument while `force`
    # argument will have no purpose.
    # noinspection PyMethodOverriding
    def delete_(
        self, *, filters: FILTERS_TYPE = None,
    ) -> bool:
        """
        Note that this is not Folder.delete but delete related to s.Table

        Note that only pivot level delete is supported

        filters:
          We are not using pds.Expression as we want to make sure that only
          filters related to partition_cols are used

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
          future ... most likely this si not possible so reject this proposal
        """
        # log
        _rp = self.richy_panel
        _rp.update(f"deleting_ for {self.__class__}")

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
        # for s.Table stuff and not the s.Folder stuff
        _partition_cols = self.partition_cols
        if filters is None:
            # noinspection PyTypeChecker
            self.path.delete(recursive=True)
            # just make a empty dir again fo that things are consistent for
            # Folder class i.e. is_created can detect things properly
            self.path.mkdir()
            # return need to satisfy the API
            return True

        # ------------------------------------------------------02
        if _partition_cols is None:
            raise e.validation.NotAllowed(
                msgs=["This Table does not use partition_cols and hence there "
                      "is no point using filters while calling delete_"]
            )

        # ------------------------------------------------------02
        # cook _filter_expression
        # make sure that filters are only made for partition_cols as only folders
        # i.e. pivots can be deleted
        _filter_expression = make_expression(
            filters=filters, restrict_columns=_partition_cols)

        # ------------------------------------------------------03
        # lets figure out what matches and make dict that can help resolve
        # paths to delete
        _matches = self.read(
            columns=_partition_cols, filter_expression=_filter_expression
        )
        _uniques = [_matches[_c].unique().to_pylist() for _c in _partition_cols]

        # ------------------------------------------------------04
        # make all combos then resolve paths and delete them
        _path = self.path
        for _tuple in itertools.product(*_uniques):
            _p = _path
            for _ in _tuple:
                _p /= str(_)
            _p.delete(recursive=True)

        # ------------------------------------------------------05
        return True
