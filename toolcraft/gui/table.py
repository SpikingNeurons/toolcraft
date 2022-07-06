import dataclasses
import typing as t
import dearpygui.dearpygui as dpg
# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg

from . import __base__
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
    """
    todo: for now we are forcing to have Cell in each row ...
      this is not necessary ... update if we want blank rows ... for now we assume
      that it can stretch table dynamically
    """

    @property
    def restrict_children_type(self) -> t.List[t.Type[Cell]]:
        return [Cell]

    @property
    def parent(self) -> "Table":
        # noinspection PyTypeChecker
        return super().parent

    def __getitem__(self, item: int) -> Cell:
        # noinspection PyTypeChecker
        return self.children.get(item)

    # noinspection PyMethodOverriding
    def __call__(self):
        """
        This will add cells based on columns in parent table
        """
        # noinspection PyUnresolvedReferences
        _num_columns = len(self.parent.columns)
        if bool(self.children):
            raise e.code.CodingError(
                msgs=[
                    "must be empty when being called for first time",
                    "you cannot call this for multiple times as cells "
                    "will be added only once"
                ]
            )
        for _ in range(_num_columns):
            super().__call__(widget=Cell())

    def on_enter(self):
        raise e.code.CodingError(
            msgs=[
                f"Although {Row} is ContainerWidget we block using with context as "
                f"the cells will be already created for and hence instead use "
                f"indexing i.e., use __getitem__"
            ]
        )

    def on_exit(self, exc_type, exc_val, exc_tb):
        raise e.code.CodingError(
            msgs=[
                f"Although {Row} is ContainerWidget we block using with context as "
                f"the cells will be already created for and hence instead use "
                f"indexing i.e., use __getitem__"
            ]
        )

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"


@dataclasses.dataclass
class Table(_auto.Table):
    # ...
    rows: t.List[Row] = None

    # ...
    columns: t.List[Column] = None

    @property
    def restrict_children_type(self) -> t.List[t.Type[Row]]:
        return [Row]

    def __call__(self, widget: Row, before: Row = None):

        # we also need to add cells in row
        if isinstance(widget, Row):
            # this will add cells based on number of columns
            widget()

        # call super to add in children
        _ret = super().__call__(widget, before)

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
                return self.children.get(item[0])[item[1]]
        else:
            raise e.code.CodingError(msgs=[f"Unknown type {type(item)}"])

    def init_validate(self):
        # call super
        super().init_validate()

        # make sure that column is supplied
        if self.columns is None:
            raise e.code.CodingError(
                msgs=[
                    f"Please supply mandatory field `columns` ..."
                ]
            )

    def init(self):
        # -------------------------------------------------- 01
        # call super
        super().init()

        # -------------------------------------------------- 02
        # do things for columns that we do when add_child is called
        _c: Column
        for _c in self.columns:
            # ---------------------------------------------- 02.01
            # should not be built
            if _c.is_built:
                raise e.code.NotAllowed(
                    msgs=[
                        "The column should not be built ..."
                    ]
                )
            # ---------------------------------------------- 02.02
            # set internals
            _c.internal.parent = self

        # -------------------------------------------------- 03
        # now call rows so that they add self to themselves
        if bool(self.rows):
            for _r in self.rows:
                _r.internal.parent = self
                self(_r)

        # -------------------------------------------------- 04
        # rows are managed by children so we hack this to remove reference to Rows
        # todo: instead of using hack have block access via __getattr__ and raise warning ... for now this will suffice
        #   ... also pycharm stops type hinting when __getattr__ is overridden :(
        self.__dict__['rows'] = None

    @classmethod
    def yaml_tag(cls) -> str:
        return f"gui.table.{cls.__name__}"

    def build_post_runner(
        self, *, hooked_method_return_value: t.Union[int, str]
    ):
        # call super
        # Note ancestry
        #   > MovableContainerWidget > (ContainerWidget, MovableWidget) > Widget > Dpg
        # We want to bypass `ContainerWidget.build_post_runner` to account for adding
        #   `Column` as they are not treated as `children`
        super(
            __base__.Widget, self
        ).build_post_runner(hooked_method_return_value=hooked_method_return_value)

        # the columns will not be handled by children mechanism as it is fixed so
        # we build it here
        for _c in self.columns:
            _c.build()

        # now as layout is completed and build for this widget is completed,
        # now it is time to render children
        for child in self.children.values():
            child.build()

    @classmethod
    def table_from_literals(
        cls, rows: int, cols: t.Union[int, t.List[str]],
    ) -> "Table":

        # make cols
        _cols = []
        if isinstance(cols, int):
            for _ in range(cols):
                _cols.append(Column())
        elif isinstance(cols, list):
            for _ in cols:
                _cols.append(Column(label=_))
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown type {type(cols)}"])

        # make rows
        _rows = []
        if isinstance(rows, int):
            for _ in range(rows):
                _rows.append(Row())
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"Unknown type {type(cols)}"])

        return Table(rows=_rows, columns=_cols)

    @classmethod
    def table_from_dict(
        cls, input_dict: t.Dict,
    ) -> "Table":
        from .. import gui
        _rows = list(input_dict.keys())
        _columns = ["\\"] + list(input_dict[_rows[0]].keys())
        _table = cls.table_from_literals(
            rows=len(_rows), cols=_columns,
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

    def unset_row_color(self, row: int):
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

    def is_cell_highlighted(self, row: int, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_cell_highlighted
        """
        return internal_dpg.is_table_cell_highlighted(self.dpg_id, row, col)

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

    def is_column_highlighted(self, col: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_column_highlighted
        """
        return internal_dpg.is_table_column_highlighted(self.dpg_id, col)

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

    def is_row_highlighted(self, row: int) -> bool:
        """
        Refer:
        >>> dpg.is_table_row_highlighted
        """
        return internal_dpg.is_table_row_highlighted(self.dpg_id, row)
