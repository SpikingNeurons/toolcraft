"""
Module related to saving results of methods in HashableClass
The classes here will be used to decorate methods of HashableClass
The places that will be used to store things will defined by property `stores`
which will return dict of special `StoreFolder`

Here we offer storage decorators for
+ Table (pyarrow tables) >> should be used as alternative to mlflow metrics
+ FileGroup >> should be used as alternate to mlflow artifacts
+ State (not yet decided will be using dapr state instead) >> alternate to mlflow tags
+ Stream (not yet decided ... also see module `storage.stream`) >>
    no equivalent in mlflow

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
import pathlib
import typing as t
import inspect
import pyarrow as pa
import enum
import pyarrow.dataset as pds
import dataclasses

from .. import marshalling as m
from .. import error as e
from . import table
from . import Folder
from . import file_group
from . import state


MODE_TYPE = t.Literal['r', 'rw', 'd', 'e', 'a', 'w']

_IS_DECORATED = '_is_decorated'


# noinspection PyDataclass
@dataclasses.dataclass(frozen=True)
class StoreFolder(Folder):
    """
    A special Folder for decorators `@s.dec.XYZ` that will use property stores to
      figure out where to save results for decorated methods

    Note that here we use `for_hashable` to get `path`, so that user can use
      `parent_folder=None`
    """
    for_hashable: m.HashableClass

    def init_validate(self):
        # call super
        super().init_validate()

        # check if path has the unique name
        # this is needed as the user need to take care of keeping
        # path unique as then he can decide the possible
        # sequence of folders under which he can store the storage results
        if self.path.as_posix().find(
            self.for_hashable.name
        ) == -1:
            e.validation.NotAllowed(
                msgs=[
                    f"You need to have unique path for `{self.__class__}` "
                    f"derived from hashable class"
                    f" {self.for_hashable.__class__}",
                    f"Please try to have `self.for_hashable.name` in the "
                    f"`{self.__class__}` property `path` to avoid this error"
                ]
            )


class _Dec:

    class LITERAL:
        reserved_kwarg_names = []
        reserved_kwarg_ann_defs = {}
        reserved_kwarg_default_values = {}
        return_ann_def = None

        @classmethod
        def mandatory_kwarg_names(cls) -> t.List[str]:
            # reserved kwarg that does not have default is mandatory
            return [
                _k for _k in cls.reserved_kwarg_names
                if _k not in cls.reserved_kwarg_default_values.keys()
            ]

    def __init__(self, *, store_name: str = 'base'):
        # save vars
        self.store_name = store_name

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
                        f"Please refrain from passing args for this specially "
                        f"decorated methods meant to be used for storing Table "
                        f"and FileGroup's etc."
                    ]
                )
            # validate on_call first
            self.validate_on_call(for_hashable=args[0], **kwargs)
            return self.on_call(for_hashable=args[0], **kwargs)
        setattr(_wrap_fn, _IS_DECORATED, True)
        return _wrap_fn

    def on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ) -> t.Any:
        e.code.CodingError(
            msgs=[
                f"You expect you to always override this method in subclassed class "
                f"{self.__class__}"
            ]
        )
        raise

    def validate(self):
        # ------------------------------------------------------- 01
        # todo: this class level check should move to rules.py eventually
        if self.LITERAL.return_ann_def is None:
            e.code.CodingError(
                msgs=[
                    f"Please define return annotation type in {self.LITERAL} for "
                    f"performing type checks ..."
                ]
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
        _reserved_kwargs = self.LITERAL.reserved_kwarg_names
        _mandatory_kwargs = self.LITERAL.mandatory_kwarg_names()
        _reserved_kwarg_ann_defs = self.LITERAL.reserved_kwarg_ann_defs
        _reserved_kwarg_default_values = self.LITERAL.reserved_kwarg_default_values

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
        # update to ignore the name self
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
        # check the annotations for reserved kwargs if provided in method
        # definition
        # ------------------------------------------------------- 05.01
        # get
        _dec_fn_annotations = _dec_fn_full_arg_spec.annotations
        # ------------------------------------------------------- 05.02
        # check if return annotation correct
        if 'return' not in _dec_fn_annotations.keys():
            e.code.CodingError(
                msgs=[
                    f"Please annotate return type for method",
                    self.dec_fn_info,
                ]
            )
        if _dec_fn_annotations['return'] != self.LITERAL.return_ann_def:
            e.code.CodingError(
                msgs=[
                    f"The return annotation should be {self.LITERAL.return_ann_def}, "
                    f"instead found annotation to be "
                    f"{_dec_fn_annotations['return']} ...",
                    f"Please check function: ",
                    self.dec_fn_info,
                ]
            )
        # ------------------------------------------------------- 05.03
        # check annotations for reserved kwargs
        for k in _dec_fn_arg_names:
            if k in _reserved_kwargs:
                if _reserved_kwarg_ann_defs[k] != _dec_fn_annotations[k]:
                    e.code.CodingError(
                        msgs=[
                            f"For reserved kwarg `{k}` the supplied "
                            f"annotation is not correct.",
                            {
                                "supplied": _dec_fn_annotations[k],
                                "expected": _reserved_kwarg_ann_defs[k],
                            },
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )

        # ------------------------------------------------------- 06
        # check for defaults supplied
        # ------------------------------------------------------- 06.01
        # extract default values ... from function definition
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
        # ------------------------------------------------------- 06.02
        # if default values are specified then make sure that same default values are
        # defined in the function
        for _rk, _default_value in _reserved_kwarg_default_values.items():
            # if reserved kwarg is defined in fn args then default value should match
            if _rk in _dec_fn_arg_names:
                # if default value is not supplied
                if _rk not in _default_value_pairs.keys():
                    e.code.CodingError(
                        msgs=[
                            f"You did not supply default value for kwarg `{_rk}`",
                            f"We expect you to supply default value `{_default_value}`",
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )
                # if default value is supplied iot should match
                if _default_value != _default_value_pairs[_rk]:
                    e.code.CodingError(
                        msgs=[
                            f"Incorrect default value for kwarg `{_rk}`",
                            f"We expect you to supply default value `{_default_value}`",
                            f"But instead found value `{_default_value_pairs[_rk]}`"
                            f"Please check function: ",
                            self.dec_fn_info,
                        ]
                    )

    def validate_on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ):
        """
        validate things that are new for every call to decorated method
        i.e. when the actual decorated method gets called
        """

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
        # check if mandatory kwargs are supplied
        for mk in self.LITERAL.mandatory_kwarg_names():
            if mk not in kwargs.keys():
                e.code.CodingError(
                    msgs=[
                        f"We expect mandatory kwarg {mk} to be supplied "
                        f"while calling decorated function ",
                        self.dec_fn_info,
                    ]
                )

        # ------------------------------------------------------- 03
        # if any reserved kwarg is supplied make sure to test if it was
        # provided in method definition ... note that passing kwargs happens at
        # runtime so this cannot be tested at code load time
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

        # ------------------------------------------------------- 04
        # check if store_name is available with for_hashable
        # todo: this happens everytime and to make it happen only once that is when
        #  for_hashable instance is created ... this needs to somehow moved to
        #  for_hashable.init_validate ... we will keep this separate as that will
        #  complicate `separation of concerns`
        if self.store_name not in for_hashable.stores.keys():
            e.code.CodingError(
                msgs=[
                    f"The store_name {self.store_name} is not provided by property "
                    f"`stores` of class {for_hashable.__class__}",
                    f"Please check method:",
                    self.dec_fn_info,
                ]
            )


# todo: depends on dapr state tracking (alternate to mlflow tags)
#   most likely we will dump this idea as having tag methods to HashableClass might
#   not be convenient ... but might be interesting to use to check status of operations
#   Most likely we will not use StorageHashable to save state but there will be some
#   sort of dapr telemetry that needs to be explored
class State(_Dec):
    """
    Will be used as a storage decorator that can save `storage.state.XYZ`
    when applied on HashableClass methods.
    """
    ...


# todo: do after stream module is supported ... i.e. pyarrow streaming tables
class Stream(_Dec):
    """
    Will be used as a storage decorator that can save `storage.stream.XYZ`
    when applied on HashableClass methods.
    """
    ...


class FileGroupMaker:
    """
    Special class whose instance we will pass to decorated method
    (using decorator @s.dec.FileGroup) so that the user can
    create `file_group.FileGroupFromPaths` instance
    """

    @property
    def exists(self) -> bool:
        _folder_exists = self.storage_path.exists() and self.storage_path.is_dir()
        _info_exists = \
            (self.parent_folder.path /
             f"{self.folder_name}{state.Suffix.info}").exists()
        _config_exists = \
            (self.parent_folder.path /
             f"{self.folder_name}{state.Suffix.config}").exists()

        if _folder_exists and _info_exists and _config_exists:
            return True
        elif (not _folder_exists) and (not _info_exists) and (not _config_exists):
            return False
        else:
            e.code.CodingError(
                msgs=[
                    f"Either all three must exists or nothing must exist",
                    {
                        "_folder_exists": _folder_exists,
                        "_info_exists": _info_exists,
                        "_config_exists": _config_exists,
                    }
                ]
            )
            raise

    def __init__(
        self, parent_folder: Folder, folder_name: str
    ):
        self.parent_folder = parent_folder
        self.folder_name = folder_name
        self.storage_path = parent_folder.path / folder_name

    def make_file_group(self, file_keys: t.List[str]) -> file_group.FileGroupFromPaths:
        return file_group.FileGroupFromPaths(
            parent_folder=self.parent_folder,
            folder_name=self.folder_name,
            keys=file_keys,
        )


class FileGroup(_Dec):
    """
    Will be used as a storage decorator that can save `storage.file_group.FileGroup`
    when applied on HashableClass methods.
    """

    class LITERAL(_Dec.LITERAL):
        file_group_maker = "file_group_maker"
        reserved_kwarg_names = [file_group_maker]
        reserved_kwarg_ann_defs = {file_group_maker: FileGroupMaker}
        reserved_kwarg_default_values = {file_group_maker: None}
        return_ann_def = file_group.FileGroupFromPaths

    def __init__(self, *, store_name: str = 'base'):
        super().__init__(store_name=store_name)

    def validate_on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ):
        # call super
        super().validate_on_call(for_hashable=for_hashable, **kwargs)

        # test if file_group_maker if supplied remains None as we will generate it and
        # user does not need to provide it
        try:
            _file_group_maker = kwargs["file_group_maker"]
            if _file_group_maker is not None:
                e.code.CodingError(msgs=[
                    f"Please do not supply kwargs `file_group_maker` as we will take "
                    f"care of supplying it ..."
                ])
        except KeyError:
            ...

    def on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ) -> file_group.FileGroupFromPaths:
        """
        Note that we do not override validate_on_call as there is nothing much to do there
        """
        # first we need to make file_group_maker
        _file_group_maker = FileGroupMaker(
            parent_folder=for_hashable.stores[self.store_name],
            folder_name=self.dec_fn_name
        )

        # update kwargs
        kwargs["file_group_maker"] = _file_group_maker

        # call the actual function
        return self.dec_fn(for_hashable, **kwargs)


@enum.unique
class _TableMode(enum.Enum):
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
    def mode_from_str(cls, mode: MODE_TYPE) -> "_TableMode":
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


class _TableOnCallReturn(t.NamedTuple):
    mode: _TableMode
    filters: t.Optional[table.FILTERS_TYPE]
    filter_expression: t.Optional[pds.Expression]
    mode_options: t.Optional[t.Dict[str, t.Any]]
    columns: t.Optional[t.List[str]]

    def process(
        self,
        for_hashable: m.HashableClass,
        store_dec: "Table",
        df_file: table.Table,
        **kwargs
    ) -> t.Union[bool, pa.Table]:
        """
        Process based on mode
        """
        # ------------------------------------------------------- 01
        if self.mode is _TableMode.read:
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
        elif self.mode is _TableMode.write:
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
                    value=store_dec.dec_fn(for_hashable, **kwargs),
                    yields=store_dec.yields,
                )
        # ------------------------------------------------------- 03
        elif self.mode is _TableMode.append:
            # noinspection PyTypeChecker
            return df_file.append(
                value=store_dec.dec_fn(for_hashable, **kwargs),
                yields=store_dec.yields,
            )
        # ------------------------------------------------------- 04
        elif self.mode is _TableMode.delete:
            return df_file.delete_(filters=self.filters)
        # ------------------------------------------------------- 05
        elif self.mode is _TableMode.exists:
            return df_file.exists(
                columns=self.columns,
                filter_expression=self.filter_expression,
                return_table=False
            )
        # ------------------------------------------------------- 06
        elif self.mode is _TableMode.read_write:
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
                    _yields = store_dec.yields
                    _value = store_dec.dec_fn(for_hashable, **kwargs)
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


class Table(_Dec):
    """
    Will be used as a storage decorator that can save `storage.table.Table`
    when applied on HashableClass methods.
    """

    class LITERAL(_Dec.LITERAL):
        mode = "mode"
        mode_options = "mode_options"
        partition_kwargs = "partition_kwargs"
        filters = "filters"
        columns = "columns"
        reserved_kwarg_names = [
            mode, mode_options, filters, columns
        ]
        reserved_kwarg_ann_defs = {
            mode: MODE_TYPE,
            filters: table.FILTERS_TYPE,
            mode_options: t.Dict[str, t.Any],
            columns: t.List[str],
        }
        reserved_kwarg_default_values = {
            filters: None,
            mode_options: None,
            columns: None,
        }
        return_ann_def = t.Union[bool, pa.Table]

    # noinspection PyUnusedLocal
    def __init__(
        self, *,
        store_name: str = 'base',
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
        # call super
        super().__init__(store_name=store_name)

    def on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ) -> t.Union[bool, pa.Table]:
        """
        Note that this method gets called everytime the decorated method is
        called.
        """
        # ------------------------------------------------------- 01
        # first validate things that are new for every call to decorated method
        # i.e. when this method gets called
        _on_call_ret_tuple = self.get_special_on_call_tuple(
            for_hashable, **kwargs
        )

        # ------------------------------------------------------- 02
        # get store_fields_folder the Folder that manages all Tables for
        # for_hashable
        _folder = for_hashable.stores[self.store_name]  # type: StoreFolder

        # ------------------------------------------------------- 03
        # get Table
        _item = self.dec_fn_name
        if _item in _folder.items.keys():
            _df_file = _folder.items[_item]  # type: table.Table
        else:
            # The Table is special Folder it takes string that is name as
            # function to create a sub-folder under _folder. Note that
            # for_hashable is known to _folder so _df_file does not need to
            # know it as it is known via parent_folder
            _df_file = table.Table(
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
            store_dec=self,
            df_file=_df_file,
            **kwargs
        )

        # ------------------------------------------------------- 05
        return _ret_table

    def get_special_on_call_tuple(
        self, for_hashable: m.HashableClass, **kwargs
    ) -> _TableOnCallReturn:
        """
        Note that we do some validations here instead of using validate_on_call as
        they are also used for building _TableOnCallReturn
        """

        # ------------------------------------------------------- 01
        # get mode ... need to fetch it earlier as it is important
        # check if mode is one of supported modes
        # Also if not instance of Mode then we make it here as it will be
        # used in validation that follows later
        _mode = kwargs[self.LITERAL.mode]
        if not isinstance(_mode, _TableMode):
            # note that this will raise error if invalid str
            _mode = _TableMode.mode_from_str(_mode)

        # ------------------------------------------------------- 02
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

        # ------------------------------------------------------- 03
        # related to filters and partition_cols
        # ------------------------------------------------------- 03.01
        # first get filters from partition cols related kwargs
        # noinspection PyTypeChecker
        _f_for_pivots = []  # type: table.FILTERS_TYPE
        if bool(self.partition_cols):
            for pk in self.partition_cols:
                if pk in kwargs.keys():
                    pkv = kwargs[pk]  # type: table.FILTER_VALUE_TYPE
                    # noinspection PyTypeChecker
                    _f_for_pivots.append((pk, "=", pkv))
        # then add some extra filters if user has provided
        _f_from_filters = kwargs.get(
            self.LITERAL.filters, []
        )  # type: table.FILTERS_TYPE
        if _f_from_filters is None:
            _f_from_filters = []
        # ------------------------------------------------------- 03.02
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
            # --------------------------------------------------- 03.02.01
            # if pivot only filters i.e. modes related to write and delete
            if _mode.is_write_or_delete_mode:
                # extra check not delete mode
                # + filters kwarg must not be supplied i.e. _f_from_filters
                #   should be empty
                # + all pivot columns must be specified
                if _mode is not _TableMode.delete:
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
                _filter_expression = table.bake_expression(
                    _elements=_f_all,
                    _err_msg=f"Filters used for mode {_mode} are not "
                             f"appropriate ....",
                    _columns_allowed=self.partition_cols,
                )
            # --------------------------------------------------- 03.02.02
            # when read related modes i.e. read and exists allow anything
            else:
                _filter_expression = table.bake_expression(
                    _elements=_f_all,
                    _err_msg=f"Filters used for mode {_mode} are not "
                             f"appropriate ....",
                    _columns_allowed=None,
                )

        # ------------------------------------------------------- 04
        # get mode options if supplied
        # todo: use in future if you want to do something more with mode like
        #  buffered reads .... wipe cache etc ...
        _mode_options = None  # type: t.Optional[t.Dict[str, t.Any]]
        if self.LITERAL.mode_options in kwargs.keys():
            _mode_options = \
                kwargs[self.LITERAL.mode_options]  # type: t.Dict[str, t.Any]

        # ------------------------------------------------------- 05
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
        return _TableOnCallReturn(
            mode=_mode,
            filters=_f_all,
            filter_expression=_filter_expression,
            mode_options=_mode_options,
            columns=_columns
        )

    def validate(self):
        """
        note that this is decorator, so you can afford to do a lot of validations
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

    def validate_dec_fn(self):

        # ------------------------------------------------------- 01
        # call super
        super().validate_dec_fn()

        # ------------------------------------------------------- 02
        # get function kwargs defined in the method
        _dec_fn_full_arg_spec = inspect.getfullargspec(self.dec_fn)
        _dec_fn_arg_names = _dec_fn_full_arg_spec.args[1:]  # leaves out first arg self
        # get some more vars
        _partition_cols = self.partition_cols

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

    def validate_on_call(
        self, for_hashable: m.HashableClass, **kwargs
    ):
        # Nothing to do as most of these validations are handled in
        # get_special_on_call_tuple()
        return super().validate_on_call(for_hashable, **kwargs)


def is_decorated(_fn) -> bool:
    if inspect.ismethod(_fn) or inspect.isfunction(_fn):
        return hasattr(_fn, _IS_DECORATED)
    else:
        return False
