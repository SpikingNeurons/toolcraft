

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Font, Scalar, Positioning, FloatObjAlignment


class TabularColsFmt(enum.Enum):
    """
    https://www.overleaf.com/learn/latex/Tables

    \\begin{tabular}[pos]{cols}
     table content
    \\end{tabular}

    Deals with cols which defines the alignment and the borders of each column
    """
    # left-justified column
    left_justified = "l"
    # centred column
    centered = "c"
    # right-justified column
    right_justified = "r"
    # vertical line
    vertical_line = "|"
    # double vertical line
    double_vertical_line = "||"
    # paragraph column with text vertically aligned at the top
    para_top = "p"
    # paragraph column with text vertically aligned in the middle
    # (requires array package)
    para_middle = "m"
    # paragraph column with text vertically aligned at the bottom
    # (requires array package)
    para_bottom = "b"
    # @{text}
    #   - Insert the text `text` in every line of the table between the columns
    #     where it appears.
    #   - This command eliminates the space that is automatically inserted between
    #     the columns.
    #   - If some horizontal space is needed between text and the columns, it can be
    #     inserted with the command \hspace{}.
    #   - The command \extraspace\fill in a tabular* environment extends the space
    #     between the columns where it appears in order to let the table have the
    #     width defined by the user.
    #   - In order to eliminate the space that is automatically inserted between two
    #     columns it is possible to use the empty command @{}.
    #   - This might help for working with tabular*
    #     @{\extracolsep{\fill}}
    #   - To eliminate space on left of first column or right of last column
    #     @{} can be useful.
    #     \\begin{tabular}{@{}lp{6cm}@{}}
    #        ...
    #     \\end{tabular}
    text = "@"

    @property
    def is_legit_column(self) -> bool:
        return self in [
            self.left_justified, self.centered, self.right_justified,
            self.para_top, self.para_middle, self.para_bottom,
        ]

    def __call__(self, width: Scalar = None, text: str = None):
        # for text ...
        if self is self.text:
            if text is None:
                raise e.validation.NotAllowed(
                    msgs=[f"Please supply value for kwarg `text`"]
                )
            if width is not None:
                raise e.validation.NotAllowed(
                    msgs=[f"Please do not supply kwarg `width`"]
                )
            return f"@{{{text}}}"
        else:
            if text is not None:
                raise e.validation.NotAllowed(
                    msgs=[f"text kwarg is usable only for {self.text}"]
                )

        # for width ...
        if width is None:
            return self.value
        else:
            if self in [self.para_top, self.para_middle, self.para_bottom]:
                return f"{self.value}{{{width}}}"
            else:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"The width kwarg cannot be used with {self}"
                    ]
                )

    def __str__(self) -> str:
        if self is self.text:
            raise e.validation.NotAllowed(
                msgs=[f"When using tabular column {self} please specify `text` kwarg "
                      f"by using __call__"]
            )
        return self.__call__()


class TabularPos(enum.Enum):
    """
    https://www.overleaf.com/learn/latex/Tables

    \\begin{tabular}[pos]{cols}
     table content
    \\end{tabular}

    Deals with pos which handles Vertical position od table
    """
    # the line at the top is aligned with the text baseline
    top = "t"
    # the line at the bottom is aligned with the text baseline
    bottom = "b"
    # the table is centred to the text baseline
    centered = "c"  # also default

    def __str__(self) -> str:
        return self.value


@dataclasses.dataclass
class MultiRowCell(LaTeX):
    """
    NOTE: you need to have `multirow` package
    As \\multicolumn allows to have cells on more than one column, the \\multirow
    command allows to have cells on more than one row. This command requires the
    package multirow.
    \\multirow can be used in two different ways:
        \\multirow{row}*{text} creates a cell that contains the `text` text and
        extends on `row` rows and has an undefined width;
        \\multirow{row}{larg}*{testo} creates a cell that contains the `text` text and
        extends on `row` rows and has a width equal to `larg`;
    """

    num_rows: int = None
    width: Scalar = None
    value: t.Union[LaTeX, str] = None

    @property
    def use_new_lines(self) -> bool:
        return False

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        return ""

    @property
    def allow_add_items(self) -> bool:
        return False

    def init_validate(self):
        # call super
        super().init_validate()

        # validate
        if self.num_rows is None:
            raise e.validation.NotAllowed(
                msgs=[f"please provide mandatory field num_rows"]
            )

    def generate(self) -> str:
        if bool(self._items):
            raise e.code.CodingError(
                msgs=[
                    f"Was expecting this to be empty ..."
                ]
            )

        _width = ""
        if self.width is not None:
            _width = f"{{{self.width}}}"

        _ret = f"\\multirow{{{self.num_rows}}}{_width}*{{{self.value}}}"

        return _ret


@dataclasses.dataclass
class MultiColumnCell(LaTeX):

    num_cols: int = None
    t_col_fmt: t.Union[TabularColsFmt, str] = None
    value: t.Union[LaTeX, str] = None

    @property
    def use_new_lines(self) -> bool:
        return False

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        return ""

    @property
    def allow_add_items(self) -> bool:
        return False

    def init_validate(self):
        # call super
        super().init_validate()

        # validate
        if self.num_cols is None:
            raise e.validation.NotAllowed(
                msgs=[f"please provide mandatory field num_cols"]
            )

        # validate t_col_fmt
        if isinstance(self.t_col_fmt, TabularColsFmt):
            if not self.t_col_fmt.is_legit_column:
                raise e.validation.NotAllowed(
                    msgs=[f"Only legit column format can be specified ... "
                          f"found {self.t_col_fmt}"]
                )

    def generate(self) -> str:
        if bool(self._items):
            raise e.code.CodingError(
                msgs=[
                    f"Was expecting this to be empty ..."
                ]
            )

        _ret = f"\\multicolumn{{{self.num_cols}}}{{{self.t_col_fmt}}}{{{self.value}}}"

        return _ret


@dataclasses.dataclass
class Row(LaTeX):

    height: Scalar = None

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        if self.height is None:
            _ret = " \\\\ "
        else:
            _ret = f" \\\\ [{self.height}]"
        return _ret

    def __len__(self):
        _ret = len(self._items)
        for _ in self._items:
            if isinstance(_, MultiColumnCell):
                _ret += (_.num_cols - 1)
        return _ret

    @classmethod
    def from_list(cls, items: t.List[str, LaTeX]) -> "Row":
        _ret = Row()
        for _ in items:
            _ret.add_item(_)
        return _ret


@dataclasses.dataclass
class Table(LaTeX):
    """
    https://www.overleaf.com/learn/latex/Tables

    Note that we prefer default `tabular`, `tabular*` and `array` environments ...
      Apart from that we will use `booktabs` package for some special formatting.
      We will not use other packages like `tabularx` but then auto adjusting column
      sizes needs to be handled by us

    Note we assume that you have added below packages
      (see Zotero/Latex for manual)
      \\RequirePackage{array}%  useful for paragraph columns ... see TabularColsFmt
      \\RequirePackage{booktabs}%  useful for professional line bars and looks
      \\RequirePackage{tabularx}%  useful for auto sizing columns

    type:
      'normal'
        \\begin{tabular}[pos]{ cols}
        rows
        \\end{tabular}
      'array'
        \\begin{array}[pos]{ cols}
        rows
        \\end{array}
      '*'
        \\begin{tabular*}{width}[pos]{ cols}
        rows
        \\end{tabular*}
      'X'
        \\begin{tabularx}{width}[pos]{ cols}
        rows
        \\end{tabularx}

    todo: support these global settings in `usepackage.sty` or may be within
      table locally ...
      It can be done via >>> \\setlength{\\tabcolsep}{3em}
      https://tex.stackexchange.com/questions/16519/adding-space-between-columns-in-a-table
      \\tabcolsep is half of the width of the space between the columns of the tabular
      and tabular* environments.
      \\arraycolsep is half of the width of the space between the columns of the array
      environments.
      \\doublerulesep is the space between double lines (\\hline\\hline).
    """

    positioning: Positioning = None
    alignment: FloatObjAlignment = None
    caption: str = None
    type: t.Literal['normal', 'array', '*', 'X'] = 'X'
    t_pos: TabularPos = TabularPos.centered
    t_width: Scalar = None
    t_cols_fmt: t.List[t.Union[TabularColsFmt, str]] = None

    @property
    def latex_type(self) -> str:

        # make table type
        _type = self.type
        if _type == 'normal':
            _type = 'tabular'
        elif _type == 'array':
            _type = 'array'
        elif _type == '*':
            _type = 'tabular*'
        elif _type == 'X':
            _type = 'tabularx'
        else:
            raise e.code.ShouldNeverHappen(msgs=[f"type {_type} is not supported"])

        # return
        return _type

    @property
    def open_clause(self) -> str:
        # make _ret container
        if self.type == 'array':
            _ret = []
        else:
            _ret = [
                f"% >> start table {'...' if self.label is None else self.label}",
                f"\\begin{{table}}"
                f"{'' if self.positioning is None else self.positioning}%",
            ]

        # add alignment
        if self.alignment is not None:
            _ret.append(f"{self.alignment}%")

        # add comment
        _ret.append(f"% >> start {self.latex_type}")

        # make width
        _width = ""
        if self.t_width is not None:
            _width = f"{{{self.t_width}}}"

        # add main table str
        _ret.append(
            f"\\begin{{{self.latex_type}}}{_width}[{self.t_pos}]{{{self.t_cols_fmt}}}%")

        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = [
            f"% >> end {self.latex_type}", f"\\end{{{self.latex_type}}}%",
        ]
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}%")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}%")
        if self.type != 'array':
            _ret += [
                f"% >> end table {'...' if self.label is None else self.label}",
                "\\end{table}%"
            ]
        return "\n".join(_ret)

    def __str__(self):
        if bool(self._items):
            # todo: address this issue later
            raise e.code.CodingError(
                msgs=["Do not call this twice as self.items will be populated again"]
            )

        # keep reference for _tikz ...
        # __str__ is like build, so we do these assignments here
        for _p in self.paths:
            # LaTeX parent class does not understand Path it only understands str or
            # subclasses of LaTeX
            self._items.append(str(_p))

        # return
        return super().__str__()

    def init(self):
        # call super
        super().init()

        # auto figure out num columns
        # noinspection PyAttributeOutsideInit
        self._num_cols = len([_ for _ in self.t_cols_fmt if _.is_legit_column])

    def init_validate(self):
        # call super
        super().init_validate()

        # should not be None
        if self.t_cols_fmt is None:
            raise e.validation.NotAllowed(
                msgs=[f"Please supply value for field `tabular_cols_fmt`"]
            )

        # will support later
        # todo: support when needed
        e.validation.ShouldNotBeEqual(
            value1=self.type, value2='array',
            msgs=["We will support this type later ..."]
        ).raise_if_failed()

        # width must be None for certain types
        if self.t_width is not None:
            e.validation.ShouldBeOneOf(
                value=self.type, values=['*', 'X'],
                msgs=["width is not supported for this type ... keep it None"]
            ).raise_if_failed()

    def add_item(self, item: t.Union[str, "LaTeX"]) -> "LaTeX":
        if isinstance(item, Row):
            raise e.code.NotAllowed(
                msgs=["Please use add_row method instead of add_item for adding Row"]
            )
        return super().add_item(item)

    def add_row(self, row: Row):
        if len(row) != self._num_cols:
            raise e.validation.NotAllowed(
                msgs=[f"We only expect to have {self._num_cols} items in row but "
                      f"instead we found {len(row)}"]
            )
        self.add_item(item=row)

    def add_hline(self):
        self.add_item(item="\\hline%")

    def add_cline(self, n: int, m: int):
        """
        draws a horizontal line from the left of column n up to the
        right of the column m
        """
        if m < n or n <= 0:
            raise e.validation.NotAllowed(
                msgs=[
                    "Select n and m to be positive non-zero numbers and n<=m",
                    "Found", dict(n=n, m=m),
                ]
            )
        self.add_item(item=f"\\cline{{{n}-{m}}}%")


