"""
Module related to saving results of methods in HashableClass
It uses storage.df_file to save all results in pyarrow based data frame
storage.

todo: explore https://github.com/tensorflow/io/tree/master/tensorflow_io/arrow
      + pandas dataframe ArrowDataset.from_pandas
      + ArrowFeatherDataset (efficient write of pandas dataframe)
      + ArrowStreamDataset (streaming ... awesome)
      + plasma https://arrow.apache.org/docs/python/plasma.html
      + IPC https://arrow.apache.org/docs/format/Columnar.html#serialization-
        and-interprocess-communication-ipc


todo: Also explore pq.ParquetDataset pq.ParquetFile pq.ParquetPartition etc.

todo: https://xnd.io/
  Note xnd has support for plasma store

"""

import typing as t
import inspect
import pyarrow as pa
import pathlib
import enum
import pyarrow.dataset as pds
import dataclasses

from .. import marshalling as m
from .. import error as e
from .. import util
from .table import \
    Table, FILTERS_TYPE, FILTER_VALUE_TYPE, bake_expression
from . import Folder, ResultsFolder


MODE_TYPE = t.Literal['r', 'rw', 'd', 'e', 'a', 'w']

_IS_STORE_FIELD = '_is_store_field'


# noinspection PyDataclass
@dataclasses.dataclass(frozen=True)
class StoreFieldsFolder(Folder):
    """
    A special Folder for StoreFields that will be saved as Table's
    Note that here we use `for_hashable` to get `path`, so that user can use
    `parent_folder=None`
    """
    parent_folder: ResultsFolder
    for_hashable: str

    @property
    def contains(self) -> t.Type[Table]:
        return Table

    @property
    def uses_parent_folder(self) -> bool:
        return True


@enum.unique
class Mode(enum.Enum):
    read = "r"
    write = "w"
    append = "a"
    read_write = "rw"
    delete = "d"
    exists = "e"

    @property
    def is_streaming_possible(self) -> bool:
        """
        Note that streaming has nothing to do with delete, exists or read.
        but we return True here so that we are allowed to pass through. This
        property states that read_write mode can never be used with
        write and read_write.
        """
        if self in [self.append, self.delete, self.exists, self.read]:
            return True
        elif self in [self.read_write, self.write]:
            return False
        else:
            e.code.CodingError(
                msgs=[
                    f"Mode {self} is not yet supported"
                ]
            )

    @property
    def is_write_or_delete_mode(self) -> bool:
        """
        This property decides if filters are used they can be allowed only on
        partition/pivot columns

        This property also decides if columns can be used
        """
        # write/delete related modes can only work on columns related partitions
        # todo: if we do not write batches to disk in that case investigate
        #  if we can delete based on filters on non-pivot columns
        if self in [
            self.write, self.delete,
            self.read_write, self.append,
        ]:
            return True
        elif self in [
            self.read, self.exists
        ]:
            return False
        else:
            e.code.ShouldNeverHappen(
                msgs=[
                    f"Mode {self} is not yet supported"
                ]
            )

    @classmethod
    def mode_from_str(cls, mode: MODE_TYPE) -> "Mode":
        for _m in cls:
            if _m.value == mode:
                return _m
        e.code.NotAllowed(
            msgs=[
                f"The mode str cannot be parsed to valid mode",
                {
                    "value": mode, "type": type(mode)
                },
                f"Possible valid str values are:",
                [_m.value for _m in cls]
            ]
        )
        raise


class OnCallReturn(t.NamedTuple):
    mode: Mode
    filters: t.Optional[FILTERS_TYPE]
    filter_expression: t.Optional[pds.Expression]
    mode_options: t.Optional[t.Dict[str, t.Any]]
    columns: t.Optional[t.List[str]]

    def process(
        self,
        for_hashable: m.HashableClass,
        store_field: "StoreField",
        df_file: Table,
        **kwargs
    ) -> t.Union[bool, pa.Table]:
        """
        Process based on mode

        Args:
            for_hashable:
            store_field:
            df_file:

        Returns:

        """
        # ------------------------------------------------------- 01
        if self.mode is Mode.read:
            _exists = df_file.exists(
                columns=self.columns,
                filter_expression=self.filter_expression,
                return_table=True
            )
            if isinstance(_exists, pa.Table):
                return _exists
            elif isinstance(_exists, bool):
                if _exists:
                    return df_file.read(
                        columns=self.columns,
                        filter_expression=self.filter_expression,
                    )
                else:
                    e.validation.NotAllowed(
                        msgs=[
                            f"There is nothing to read on the disk. Please "
                            f"check if exists before performing read."
                        ]
                    )
                    raise
            else:
                e.code.ShouldNeverHappen(
                    msgs=[
                        f"Cannot recognize type {type(_exists)}"
                    ]
                )
                raise
        # ------------------------------------------------------- 02
        elif self.mode is Mode.write:
            _exists = df_file.exists(
                columns=self.columns,
                filter_expression=self.filter_expression,
                return_table=False
            )
            if _exists:
                e.validation.NotAllowed(
                    msgs=[
                        "Cannot write as data already exists on the disk.",
                        "Please check if exists before writing"
                    ]
                )
                raise
            else:
                # noinspection PyTypeChecker
                return df_file.append(
                    value=store_field.dec_fn(for_hashable, **kwargs),
                    yields=store_field.yields,
                )
        # ------------------------------------------------------- 03
        elif self.mode is Mode.append:
            # noinspection PyTypeChecker
            return df_file.append(
                value=store_field.dec_fn(for_hashable, **kwargs),
                yields=store_field.yields,
            )
        # ------------------------------------------------------- 04
        elif self.mode is Mode.delete:
            return df_file.delete_(filters=self.filters)
        # ------------------------------------------------------- 05
        elif self.mode is Mode.exists:
            return df_file.exists(
                columns=self.columns,
                filter_expression=self.filter_expression,
                return_table=False
            )
        # ------------------------------------------------------- 06
        elif self.mode is Mode.read_write:
            # check if exists
            _exists = df_file.exists(
                columns=self.columns,
                filter_expression=self.filter_expression,
                return_table=True
            )
            if isinstance(_exists, pa.Table):
                return _exists
            elif isinstance(_exists, bool):
                # if something existed then it should have been a table so
                # raise error ...
                if _exists:
                    e.code.CodingError(
                        msgs=[
                            f"Ideally this should be table as we used "
                            f"return_table=True",
                            f"If nothing exists it should be false ... check "
                            f"the code ..."
                        ]
                    )
                # else create table
                else:
                    _yields = store_field.yields
                    _value = store_field.dec_fn(for_hashable, **kwargs)
                    # noinspection PyTypeChecker
                    df_file.append(
                        value=_value,
                        yields=_yields,
                    )

                    # the _value will be generator if yields was mentioned so
                    # we need to read it else we return _value
                    if _yields:
                        return df_file.read(
                            columns=self.columns,
                            filter_expression=self.filter_expression,
                        )
                    else:
                        # noinspection PyTypeChecker
                        return _value
            else:
                e.code.ShouldNeverHappen(
                    msgs=[
                        f"Cannot recognize type {type(_exists)}"
                    ]
                )
                raise
        # ------------------------------------------------------- 07
        else:
            e.code.ShouldNeverHappen(
                msgs=[f"Unsupported mode {self.mode}"]
            )
            raise


class StoreField:
    """
    Will be used as a decorator.
    """

    class LITERAL:
        mode = "mode"
        mode_options = "mode_options"
        partition_kwargs = "partition_kwargs"
        filters = "filters"
        columns = "columns"
        reserved_kwarg_names = [
            mode, mode_options, filters, columns
        ]
        mandatory_kwarg_names = [mode]
        res_kwarg_ann_defs = {
            mode: MODE_TYPE,
            filters: FILTERS_TYPE,
            mode_options: t.Dict[str, t.Any],
            columns: t.List[str],
        }

    # noinspection PyUnusedLocal
    def __init__(
        self, *,
        streamed_write: bool = False,
        partition_cols: t.Optional[t.List[str]] = None,
        yields: bool = False,
        table_schema: pa.Schema = None,
    ):
        """
        Decorating for_hashable's methods or properties with this class will
        allow them to store their results to disk as pa.Table's.

        The resulting object is Table which will be managed by
        StoreFieldsFolder. The name of Table will be property/method name.

        Args:
            streamed_write:
              If the pandas dataframe will be written as a stream
            partition_cols:
              Pivots the table for efficient grouping of columnar data
            yields:
              The decorated function yields pd.Dataframe instead of return.
              todo: While yielding generator computes values and we loop over
                it ... can we parallelize yield ?? such that data-frames are
                computed and stored in parallel ... check for parallel-io and
                parallel-compute
            table_schema:
              Schema of the table that will be returned ... if provided we
              will validate it with first write
              todo: still not implemented must be done in df_file._write_table
                 when self.table_schema is None we will auto figure it out or
                 else we will use it to validate against the table to be
                 written .... later we can overwrite self._table_schema so
                 that it happens only once
        """
        # ------------------------------------------------------- 01
        # store inside instance
        self.streamed_write = streamed_write
        self.partition_cols = partition_cols
        self.yields = yields
        self.table_schema = table_schema

        # ------------------------------------------------------- 02
        # validate - note that this is decorator so you can afford to do lot
        # of validations
        self.validate()

    def __call__(self, dec_fn: t.Callable) -> t.Callable:
        """
        Remember this only happens when the decorator instance is created
        during class load.

        Note that this only wraps the decorated function and does not get
        called when the decorated method is actually called. The actual code
        that will get called is in method `on_call`. This is how class based
        decorators work. Note that the code for decorated method will be
        wrapped in `on_call`

        Hence we use this method to register the function we decorated,
        its name and the info associated for debugging.
        """
        # ------------------------------------------------------- 01
        # store decorated fn in decorator instance
        self.dec_fn = dec_fn
        self.dec_fn_name = dec_fn.__name__
        # noinspection PyUnresolvedReferences
        self.dec_fn_info = {
            "module": dec_fn.__module__,
            "class": dec_fn.__qualname__.split(".")[0],
            "function": dec_fn.__name__
        }
        self.dec_fn_args = inspect.getfullargspec(dec_fn).args

        # ------------------------------------------------------- 02
        # validate dec_fn
        self.validate_dec_fn()

        # ------------------------------------------------------- 03
        # return wrapped method that will be called instead of decorated method
        # Note that the method used for wrapping will anyways call the
        # original dec_fn
        def _wrap_fn(*args, **kwargs):
            if len(args) != 1:
                e.code.CodingError(
                    msgs=[
                        f"The class methods decorated with {StoreField} do "
                        f"not allow args ... only use kwargs ..."
                    ]
                )
            return self.on_call(for_hashable=args[0], **kwargs)
        setattr(_wrap_fn, _IS_STORE_FIELD, True)
        return _wrap_fn

    def on_call(
        self, for_hashable: m.HashableClass, *args, **kwargs
    ) -> t.Union[bool, pa.Table]:
        """
        Note that this method gets called everytime the decorated method is
        called.

        Args:
            for_hashable:
            *args:
            **kwargs:

        Returns:

        """
        # ------------------------------------------------------- 01
        # first validate things that are new for every call to decorated method
        # i.e. when this method gets called
        _on_call_ret_tuple = self.validate_on_call_and_get_things(
            for_hashable, *args, **kwargs
        )

        # ------------------------------------------------------- 02
        # get store_fields_folder the Folder that manages all Tables for
        # for_hashable
        _folder = for_hashable.results_folder.store  # type: StoreFieldsFolder

        # ------------------------------------------------------- 03
        # get Table
        _item = self.dec_fn_name
        if _item in _folder.items.keys():
            _df_file = _folder.items[_item]  # type: Table
        else:
            # The Table is special Folder it takes string that is name as
            # function to create a sub-folder under _folder. Note that
            # for_hashable is known to _folder so _df_file does not need to
            # know it as it is known via parent_folder
            _df_file = Table(
                for_hashable=_item, parent_folder=_folder
            )
            # we need to update config for partition_cols and table_schema
            _c = _df_file.config
            if _c.schema != self.table_schema:
                _c.schema = self.table_schema
            if _c.partition_cols != self.partition_cols:
                _c.partition_cols = self.partition_cols
            # track using _folder
            # the above instance creation automatically adds to items in _folder
            # _folder.add_item(hashable=_df_file)

        # ------------------------------------------------------- 04
        # now process
        _ret_table = _on_call_ret_tuple.process(
            for_hashable=for_hashable,
            store_field=self,
            df_file=_df_file,
            **kwargs
        )

        # ------------------------------------------------------- 05
        return _ret_table

    def validate_on_call_and_get_things(
        self, for_hashable: m.HashableClass,
        *args, **kwargs
    ) -> OnCallReturn:

        # ------------------------------------------------------- 01
        # test for_hashable
        # Make sure that it is HashableClass
        e.validation.ShouldBeInstanceOf(
            value=for_hashable, value_types=(m.HashableClass,),
            msgs=[
                f"We expect you to use {self.__class__} decorator on "
                f"methods of classes that are subclasses of "
                f"{m.HashableClass}",
            ]
        )

        # ------------------------------------------------------- 02
        # do not allow args
        if bool(args):
            e.code.NotAllowed(
                msgs=[
                    f"We do not allow you to pass args to function "
                    f"which is decorated by {StoreField}",
                    f"\t > Found args: {args}",
                    f"Please check call to: ",
                    self.dec_fn_info,
                ]
            )

        # ------------------------------------------------------- 03
        # check if mandatory kwargs are supplied
        for mk in self.LITERAL.mandatory_kwarg_names:
            if mk not in kwargs.keys():
                e.code.CodingError(
                    msgs=[
                        f"We expect mandatory kwarg {mk} to be supplied "
                        f"while calling decorated function ",
                        self.dec_fn_info,
                    ]
                )

        # ------------------------------------------------------- 04
        # get mode ... need to fetch it earlier as it is important
        # check if mode is one of supported modes
        # Also if not instance of Mode then we make it here as it will be
        # used in validation that follows later
        _mode = kwargs[self.LITERAL.mode]
        if not isinstance(_mode, Mode):
            # note that this will raise error if invalid str
            _mode = Mode.mode_from_str(_mode)

        # ------------------------------------------------------- 05
        # if store_field is for `streamed_write` then check if corresponding
        # mode allows it
        if self.streamed_write:
            if not _mode.is_streaming_possible:
                e.code.CodingError(
                    msgs=[
                        f"Mode `{_mode.value}` cannot be used when "
                        f"storage field is configured for streamed write "
                        f"...",
                        f"Please check call to: ",
                        self.dec_fn_info,
                    ]
                )

        # ------------------------------------------------------- 06
        # if any reserved kwarg is supplied make sure to test if it was
        # provided in method definition
        # todo: as of now it is impossible to do this check only once at
        #  class load time
        for rk in self.LITERAL.reserved_kwarg_names:
            if rk in kwargs.keys():
                if rk not in self.dec_fn_args:
                    e.code.CodingError(
                        msgs=[
                            f"Looks like you are supplying one of the reserved "
                            f"kwarg i.e. `{rk}` used by StoreField mechanism.",
                            f"Please make sure to provide it in method "
                            f"definition even if you are not consuming it.",
                            f"StoreField mechanism will internally consume it "
                            f"while it is optional for you to consume it "
                            f"within your decorated method.",
                            f"Please check method:",
                            self.dec_fn_info,
                        ]
                    )

        # ------------------------------------------------------- 07
        # related to filters and partition_cols
        # ------------------------------------------------------- 07.01
        # first get filters from partition cols related kwargs
        # noinspection PyTypeChecker
        _f_for_pivots = []  # type: FILTERS_TYPE
        if bool(self.partition_cols):
            for pk in self.partition_cols:
                if pk in kwargs.keys():
                    pkv = kwargs[pk]  # type: FILTER_VALUE_TYPE
                    # noinspection PyTypeChecker
                    _f_for_pivots.append((pk, "=", pkv))
        # then add some extra filters if user has provided
        _f_from_filters = kwargs.get(
            self.LITERAL.filters, []
        )  # type: FILTERS_TYPE
        if _f_from_filters is None:
            _f_from_filters = []
        # ------------------------------------------------------- 07.02
        # Bake expression for filters
        # if something to filter then validate and bake expression
        # Note on validation
        #  + write and delete related modes only allow filters applied to pivot
        #    columns
        #    + delete mode can also work on some or all pivot columns plus it
        #      can also use other comparisons for group select like <=, >= etc.
        #    + write related modes require all pivot filters and they should
        #      be specified via partition column kwargs
        #  + read related modes work on any filters and are not restricted on
        #    pivot only filters
        _filter_expression = None  # type: t.Optional[pds.Expression]
        _f_all = _f_for_pivots + _f_from_filters
        # if _f_all empty make it None
        if not bool(_f_all):
            _f_all = None
        # else something to filter then create _filter_expression
        else:
            # --------------------------------------------------- 07.02.01
            # if pivot only filters i.e. modes related to write and delete
            if _mode.is_write_or_delete_mode:
                # extra check not delete mode
                # + filters kwarg must not be supplied i.e. _f_from_filters
                #   should be empty
                # + all pivot columns must be specified
                if _mode is not Mode.delete:
                    if bool(_f_from_filters):
                        e.code.NotAllowed(
                            msgs=[
                                f"You cannot use `filters` kwarg for mode "
                                f"{_mode}"
                            ]
                        )
                    if len(_f_for_pivots) != len(self.partition_cols):
                        e.code.NotAllowed(
                            msgs=[
                                f"For mode {_mode} all partition related "
                                f"kwargs must be supplied",
                                f"That is supply values for all kwargs below",
                                self.partition_cols
                            ]
                        )
                # Now cook expression from filters ... note that for delete
                # mode we anyways fix columns to pivot only because of kwarg
                # _columns_allowed
                _filter_expression = bake_expression(
                    _elements=_f_all,
                    _err_msg=f"Filters used for mode {_mode} are not "
                             f"appropriate ....",
                    _columns_allowed=self.partition_cols,
                )
            # --------------------------------------------------- 07.02.02
            # when read related modes i.e. read and exists allow anything
            else:
                _filter_expression = bake_expression(
                    _elements=_f_all,
                    _err_msg=f"Filters used for mode {_mode} are not "
                             f"appropriate ....",
                    _columns_allowed=None,
                )

        # ------------------------------------------------------- 08
        # get mode options if supplied
        # todo: use in future if you want to do something more with mode like
        #  buffered reads .... wipe cache etc ...
        _mode_options = None  # type: t.Optional[t.Dict[str, t.Any]]
        if self.LITERAL.mode_options in kwargs.keys():
            _mode_options = \
                kwargs[self.LITERAL.mode_options]  # type: t.Dict[str, t.Any]

        # ------------------------------------------------------- 09
        # get columns options if supplied
        _columns = None  # type: t.Optional[t.List[str]]
        if self.LITERAL.columns in kwargs.keys():
            # check if mode allows
            if _mode.is_write_or_delete_mode:
                e.code.NotAllowed(
                    msgs=[
                        f"The `columns` kwarg cannot be used with mode "
                        f"{_mode}"
                    ]
                )
            # set var
            _columns = kwargs[self.LITERAL.columns]  # type: t.List[str]

        # ------------------------------------------------------- xx
        # todo: Although this is expensive that is this check will happen every
        #   time the call to decorated method happens. We have to do it here as
        #   _fn_run_file_system is available here. May be we can set a flag so
        #   that this only happens once in the lifetime of the application.
        # ...
        # Here we check if columns mentioned as partition_cols were actually
        # written to disk this is because pyarrow does not care if the column
        # provided is written to disk or not and the corresponding filter
        # that use columns that was not written to disk simply return the
        # entire table
        # ...
        # Apart from that the user might change the partitioned_cols list
        # i.e. he might change the sequence or add new column to the list ...
        # in that case the partitioned column structure on disk is not valid
        # todo: we keep this feature pending ... for local file system we can
        #  just iterate over directory and check if all folders start with
        #  column list as provided by partition_cols as we deep dive in the
        #  folder structure
        #  ...
        #  To make this work for other file systems the
        #  `self._fn_run_file_system.path` should be iterable which can
        #  iterate over file system on cloud or an online data_store

        # ------------------------------------------------------- xx
        # return
        return OnCallReturn(
            mode=_mode,
            filters=_f_all,
            filter_expression=_filter_expression,
            mode_options=_mode_options,
            columns=_columns
        )

    def validate_dec_fn(self):

        # ------------------------------------------------------- 01
        # check function name and __qualname__
        _fn_qualname_split = self.dec_fn.__qualname__.split(".")
        if len(_fn_qualname_split) != 2:
            e.code.CodingError(
                msgs=[
                    f"Cannot understand fn qualifier name "
                    f"{self.dec_fn.__qualname__}",
                    f"Was expecting format `<class_name>.<method_name>`",
                    f"Please check: ",
                    self.dec_fn_info
                ]
            )
        # noinspection PyUnresolvedReferences
        _fn_module_name = self.dec_fn.__module__
        _fn_class_name = _fn_qualname_split[0]
        _fn_name = _fn_qualname_split[1]
        if _fn_name != self.dec_fn.__name__:
            e.code.CodingError(
                msgs=[
                    f"Should be ideally same",
                    {
                        "_fn_name from __qualname__": _fn_name,
                        "fn.__name__": self.dec_fn.__name__
                    },
                    f"Please check: ",
                    self.dec_fn_info
                ]
            )

        # ------------------------------------------------------- 02
        # get function kwargs defined in the method
        _dec_fn_full_arg_spec = inspect.getfullargspec(self.dec_fn)
        _dec_fn_arg_names = _dec_fn_full_arg_spec.args
        # get some more vars
        _partition_cols = self.partition_cols
        _reserved_kwargs = self.LITERAL.reserved_kwarg_names
        _mandatory_kwargs = self.LITERAL.mandatory_kwarg_names
        _res_kwarg_ann_defs = self.LITERAL.res_kwarg_ann_defs

        # ------------------------------------------------------- 03
        # make sure that first arg is self and update fn_args to ignore name
        # self
        if _dec_fn_arg_names[0] != "self":
            e.code.CodingError(
                msgs=[
                    f"We expect first arg of decorated function to be self "
                    f"as it will be instance method and also we want to stick "
                    f"to python naming conventions.",
                    f"Please check function: ",
                    self.dec_fn_info,
                ]
            )
        # update so as to ignore the name self
        _dec_fn_arg_names = _dec_fn_arg_names[1:]

        # ------------------------------------------------------- 04
        # make sure that mandatory kwargs are defined in function
        for k in _mandatory_kwargs:
            if k not in _dec_fn_arg_names:
                e.code.CodingError(
                    msgs=[
                        f"Make sure to define mandatory kwarg {k} in function "
                        f"below ... ",
                        self.dec_fn_info,
                    ]
                )

        # ------------------------------------------------------- 05
        # make sure that all kwargs specified in partition_cols are defined in
        # method definition
        if bool(_partition_cols):
            for k in _partition_cols:
                if k not in _dec_fn_arg_names:
                    e.code.CodingError(
                        msgs=[
                            f"You specified key `{k}` as a partition column "
                            f"while decorating method with StoreField. ",
                            f"So please make sure to define it in method "
                            f"definition and also make sure to consume it.",
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )

        # ------------------------------------------------------- 06
        # check the annotations for reserved kwargs if provided in method
        # definition
        # ------------------------------------------------------- 06.01
        # get
        _dec_fn_annotations = _dec_fn_full_arg_spec.annotations
        # ------------------------------------------------------- 06.02
        # check if return annotation correct
        if 'return' not in _dec_fn_annotations.keys():
            e.code.CodingError(
                msgs=[
                    f"Please annotate return type for method",
                    self.dec_fn_info,
                ]
            )
        else:
            if _dec_fn_annotations['return'] != pa.Table:
                e.code.CodingError(
                    msgs=[
                        f"The return annotation should be {pa.Table}, "
                        f"instead found annotation to be "
                        f"{_dec_fn_annotations['return']} ...",
                        f"Please check function: ",
                        self.dec_fn_info,
                    ]
                )
        # ------------------------------------------------------- 06.03
        # check annotations for reserved kwargs
        for k in _dec_fn_arg_names:
            if k in _reserved_kwargs:
                if _res_kwarg_ann_defs[k] != _dec_fn_annotations[k]:
                    e.code.CodingError(
                        msgs=[
                            f"For reserved kwarg `{k}` the supplied "
                            f"annotation is not correct.",
                            {
                                "supplied": _dec_fn_annotations[k],
                                "expected": _res_kwarg_ann_defs[k],
                            },
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )
        # ------------------------------------------------------- 06.04
        # check if defaults supplied are None except for mode
        # ------------------------------------------------------- 06.04.01
        # extract default values
        # note that default is tuple and ending args in function definition
        # have default values
        if _dec_fn_full_arg_spec.defaults is None:
            _default_value_pairs = {}
        else:
            _default_value_pairs = dict(
                zip(
                    _dec_fn_full_arg_spec.args[::-1],
                    _dec_fn_full_arg_spec.defaults[::-1]
                )
            )
        # ------------------------------------------------------- 06.04.02
        # if reserved kwarg specified then it should have default value None
        # except mode
        for rk in _reserved_kwargs:
            # skip reserved kwarg mode
            if rk == self.LITERAL.mode:
                continue
            # if reserved kwarg is defined in fn args
            if rk in _dec_fn_arg_names:
                # if default not specified raise error
                if rk not in _default_value_pairs.keys():
                    e.code.CodingError(
                        msgs=[
                            f"We expect you to supply default value None to "
                            f"reserved kwarg `{rk}`",
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )
                # else if default value specified it should be None
                else:
                    if _default_value_pairs[rk] is not None:
                        e.code.CodingError(
                            msgs=[
                                f"We expect default value to be None for "
                                f"reserved kwarg `{rk}`",
                                f"Please check function: ",
                                self.dec_fn_info,
                            ]
                        )

    def validate(self):
        """
        note that this is decorator so you can afford to do lot  of validations
        """
        # ------------------------------------------------------- 01
        # check partition_cols
        if bool(self.partition_cols):
            # check if partition cols do not have repeat keys
            if len(set(self.partition_cols)) != len(self.partition_cols):
                e.code.CodingError(
                    msgs=[
                        "Please check the partition_cols, looks like you "
                        "repeated string in the list provided ..."
                    ]
                )
            # check if partition column name is a reserved kwarg
            for col_name in self.partition_cols:
                if col_name in self.LITERAL.reserved_kwarg_names:
                    e.validation.NotAllowed(
                        msgs=[
                            f"You cannot use column name to be `{col_name}` as "
                            f"it is reserved for use by storage.StoreField..."
                        ]
                    )


def is_store_field(_fn) -> bool:
    if inspect.ismethod(_fn) or inspect.isfunction(_fn):
        return hasattr(_fn, _IS_STORE_FIELD)
    else:
        return False
