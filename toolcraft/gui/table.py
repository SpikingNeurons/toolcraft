import dataclasses
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from . import COLOR_TYPE
from . import _auto
from .. import error as e
from .. import util


@dataclasses.dataclass
class Column(_auto.TableColumn):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"


@dataclasses.dataclass
class Cell(_auto.TableCell):

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"


@dataclasses.dataclass
class Row(_auto.TableRow):

    # noinspection PyMethodOverriding
    def __call__(self):
        """
        This will add cells based on columns in parent table
        """
        # noinspection PyUnresolvedReferences
        _num_columns = len(self.parent.columns)
        if bool(self.children):
            e.code.CodingError(
                msgs=[
                    "must be empty when being called for first time",
                    "you cannot call this for multiple times as cells "
                    "will be added only once"
                ]
            )
        for _ in range(_num_columns):
            self.add_child(widget=Cell())

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"


@dataclasses.dataclass
class Table(_auto.Table):
    # ...
    rows: t.Union[int, t.List[Row]] = None

    # ...
    columns: t.Union[int, t.List[t.Union[str, Column]]] = None

    @property
    @util.CacheResult
    def children(self) -> t.List[Row]:
        # noinspection PyTypeChecker
        return self.rows

    def __call__(self, item: Row):

        # we also need to add cells in row
        if isinstance(item, Row):
            # this will add cells based on number of columns
            item()
        else:
            e.code.ShouldNeverHappen(msgs=[])

        # call super to add in children
        _ret = super().__call__(item)

        # return
        return _ret

    def __getitem__(
        self, item: t.Union[int, t.Tuple[int, int]]
    ) -> t.Union[Row, Column, Cell]:
        """
        When:
          + item is int
            + returns TableRow
          + item is (int, int)
            + returns TableCell
          + item is (:, int)
            + returns TableColumn
        """
        if isinstance(item, int):
            return self.rows[item]
        elif isinstance(item, tuple):
            if item[0] == slice(None, None, None):
                return self.columns[item[1]]
            else:
                return self.rows[item[0]][item[1]]
        else:
            e.code.CodingError(msgs=[f"Unknown type {type(item)}"])
            raise

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"

    def init_validate(self):
        # call super
        super().init_validate()

        # check mandatory fields
        if self.rows is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `rows`"
                ]
            )
        if self.columns is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `columns`"
                ]
            )

    def init(self):
        # -------------------------------------------------- 01
        # call super
        super().init()

        # -------------------------------------------------- 02
        # make columns list
        if isinstance(self.columns, int):
            _num_columns = self.columns
            self.__dict__['columns'] = []
            assert self.columns == []
            for _ in range(_num_columns):
                # noinspection PyUnresolvedReferences
                self.columns.append(TableColumn())
        elif isinstance(self.columns, list):
            _num_columns = len(self.columns)
            _backup_cols = self.columns
            self.__dict__['columns'] = []
            assert self.columns == []
            for _c in _backup_cols:
                if isinstance(_c, str):
                    self.columns.append(Column(label=_c))
                elif isinstance(_c, Column):
                    self.columns.append(_c)
                else:
                    e.code.ShouldNeverHappen(msgs=[])
                    raise
        else:
            e.code.ShouldNeverHappen(msgs=[])
            raise

        # -------------------------------------------------- 03
        # do things for columns that we do when add_child is called
        _c: Column
        for _c in self.columns:
            # ---------------------------------------------- 03.01
            # should not be built
            if _c.is_built:
                e.code.NotAllowed(
                    msgs=[
                        "The column should not be built ..."
                    ]
                )
            # ---------------------------------------------- 03.02
            # set internals
            _c.internal.parent = self
            _c.internal.root = self.root

        # -------------------------------------------------- 04
        # make rows list
        if isinstance(self.rows, int):
            _num_rows = self.rows
            self.__dict__['rows'] = []
            assert id(self.rows) == id(self.children)
            for _ in range(_num_rows):
                self(Row())
        elif isinstance(self.rows, list):
            _num_rows = len(self.rows)
            _backup_rows = self.rows
            self.__dict__['rows'] = []
            assert id(self.rows) == id(self.children)
            for _r in _backup_rows:
                if isinstance(_r, Row):
                    self(_r)
                else:
                    e.code.ShouldNeverHappen(msgs=[])
                    raise
        else:
            e.code.ShouldNeverHappen(msgs=[])
            raise

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # build columns first
        for _c in self.columns:
            _c.build()

        # call super to add children i.e. nothing but rows
        assert id(self.children) == id(self.rows)
        super().build_post_runner(hooked_method_return_value=hooked_method_return_value)

    @classmethod
    def table_from_dict(
        cls, input_dict: t.Dict,
    ) -> "Table":
        from .. import gui
        _rows = list(input_dict.keys())
        _columns = ["\\"] + list(input_dict[_rows[0]].keys())
        _table = Table(
            rows=len(_rows), columns=_columns,
        )
        for _rid, _r in enumerate(_rows):
            for _cid, _c in enumerate(_columns):
                if _c == "\\":
                    _table[_rid, _cid](
                        gui.widget.Text(default_value=f"{_r}")
                    )
                else:
                    _table[_rid, _cid](
                        gui.widget.Text(default_value=f"{input_dict[_r][_c]}")
                    )
        return _table

    def set_row_color(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.set_table_row_color
        """
        internal_dpg.set_table_row_color(self.dpg_id, row, color)

    def unset_row_color(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.unset_table_row_color
        """
        internal_dpg.unset_table_row_color(self.dpg_id, row)

    def highlight_cell(self, row: int, col: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_cell
        """
        internal_dpg.highlight_table_cell(self.dpg_id, row, col, color)

    def unhighlight_cell(self, row: int, col: int):
        """
        Refer:
        >>> dpg.unhighlight_table_cell
        """
        internal_dpg.unhighlight_table_cell(self.dpg_id, row, col)

    def is_cell_highlight(self, row: int, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_cell_highlight
        """
        return internal_dpg.is_table_cell_highlight(self.dpg_id, row, col)

    def highlight_column(self, col: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_column
        """
        internal_dpg.highlight_table_column(self.dpg_id, col, color)

    def unhighlight_column(self, col: int):
        """
        Refer:
        >>> dpg.unhighlight_table_column
        """
        internal_dpg.unhighlight_table_column(self.dpg_id, col)

    def is_column_highlight(self, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_column_highlight
        """
        return internal_dpg.is_table_column_highlight(self.dpg_id, col)

    def highlight_row(self, row: int, color: COLOR_TYPE):
        """
        Refer:
        >>> dpg.highlight_table_row
        """
        internal_dpg.highlight_table_row(self.dpg_id, row, color)

    def unhighlight_row(self, row: int):
        """
        Refer:
        >>> dpg.unhighlight_table_row
        """
        internal_dpg.unhighlight_table_row(self.dpg_id, row)

    def is_row_highlight(self, row: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_row_highlight
        """
        return internal_dpg.is_table_row_highlight(self.dpg_id, row)
