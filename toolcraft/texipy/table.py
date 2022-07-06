

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Font, Scalar, Positioning, FloatObjAlignment


class ColumnFmt(enum.Enum):
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
    # paragraph column with text vertically aligned at the top
    para_top = "p"
    # paragraph column with text vertically aligned in the middle
    # (requires array package)
    para_middle = "m"
    # paragraph column with text vertically aligned at the bottom
    # (requires array package)
    para_bottom = "b"
    # The tabularx package requires the same arguments of tabular* but, in order to
    # let the table have the width specified by the user, it modifies the width of
    # certain columns instead of the space between columns. The columns that can be
    # stretched are identified by the alignment command X. This package requires the
    # array package.
    stretched = "X"
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
    insert = "@"
    # insert before
    # - can be placed before a command l, r, c, p, m or b and inserts ins before
    #   the content of the cell;
    # - can also be used to format certain columns:
    #   it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
    #   \\mdseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily
    insert_before = ">"
    # insert after
    # - can be placed before a command l, r, c, p, m or b and inserts ins before
    #   the content of the cell;
    # - can also be used to format certain columns:
    #   it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
    #   \\mdseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily
    insert_after = "<"
    # vertical line
    vertical_line = "|"
    # double vertical line
    double_vertical_line = "||"

    @property
    def is_legit_column(self) -> bool:
        return self in [
            self.left_justified, self.centered, self.right_justified,
            self.para_top, self.para_middle, self.para_bottom,
            self.stretched,
        ]

    def __call__(self, width: Scalar = None, insert: str = None):
        # if vertical line's no kwargs will be used
        if self in [self.vertical_line, self.double_vertical_line, self.stretched]:
            if width is not None or insert is not None:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"no use for pass kwargs while using `ColumnFmt.{self.name}` "
                        f"as we need not parametrize it"
                    ]
                )

        # for inserts ...
        if self in [self.insert, self.insert_before, self.insert_after]:
            if insert is None:
                raise e.validation.NotAllowed(
                    msgs=[f"Please supply value for kwarg `text` while using {self}"]
                )
            if width is not None:
                raise e.validation.NotAllowed(
                    msgs=[f"Please do not supply kwarg `width` while using {self}"]
                )
            return f"{self.value}{{{insert}}}"

        # since self is not for `self.insert` we expect `insert` kwarg to be None
        if insert is not None:
            raise e.validation.NotAllowed(
                msgs=[f"insert kwarg is usable only for insert related stuff"]
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
        if self in [self.insert, self.insert_after, self.insert_before]:
            raise e.validation.NotAllowed(
                msgs=[f"When using tabular column {self} please specify `insert` kwarg "
                      f"by using __call__"]
            )
        return self.__call__()

    @classmethod
    def enum_from_value(cls, _str: str) -> "ColumnFmt":
        for _ in cls:
            if _.value == _str[0:1]:
                return _
        raise e.validation.NotAllowed(
            msgs=[
                f"Cannot recognize string `{_str}`",
                "Should be one of:",
                [_.value for _ in cls]
            ]
        )


class TablePos(enum.Enum):
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
    no_comments: bool = True  # this will avoid problems when in use_single_line_repr

    @property
    def allow_add_items(self) -> bool:
        return False

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        # to avoid but when adding multi-row cell in a row
        if self.no_comments:
            return ""
        else:
            return "\n"

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
    t_col_fmt: t.Union[ColumnFmt, str] = None
    value: t.Union[LaTeX, str] = None
    no_comments: bool = True  # this will avoid problems when in use_single_line_repr

    @property
    def allow_add_items(self) -> bool:
        return False

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        return ""

    def init_validate(self):
        # call super
        super().init_validate()

        # validate
        if self.num_cols is None:
            raise e.validation.NotAllowed(
                msgs=[f"please provide mandatory field num_cols"]
            )
        if self.t_col_fmt is None:
            raise e.validation.NotAllowed(
                msgs=[f"please provide mandatory field t_col_fmt"]
            )

        # validate t_col_fmt
        if isinstance(self.t_col_fmt, ColumnFmt):
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
    def use_single_line_repr(self) -> bool:
        return True

    @property
    def open_clause(self) -> str:
        return ""

    @property
    def close_clause(self) -> str:
        if self.height is None:
            _ret = " \\\\ "
        else:
            _ret = f" \\\\ [{self.height}] "
        return _ret

    def __len__(self):
        _ret = len(self._items)
        for _ in self._items:
            if isinstance(_, MultiColumnCell):
                _ret += (_.num_cols - 1)
        return _ret

    @classmethod
    def from_list(
        cls, items: t.List[t.Union[str, LaTeX]], height: Scalar = None
    ) -> "Row":
        _ret = Row(height=height)
        for _ in items:
            _ret.add_item(_)
        return _ret

    def generate(self) -> str:
        return " & ".join([str(_) for _ in self._items])


@dataclasses.dataclass
class TableColsDef(LaTeX):

    @property
    def use_single_line_repr(self) -> bool:
        return True

    @property
    def open_clause(self) -> str:
        return "{"

    @property
    def close_clause(self) -> str:
        return "}"

    def init(self):
        # call super
        super().init()

        # some vars to track previous items
        # noinspection PyAttributeOutsideInit,PyTypeChecker
        self._previous_fmt = None  # type: ColumnFmt
        # noinspection PyAttributeOutsideInit
        self.uses_stretched_fmt = False
        # noinspection PyAttributeOutsideInit
        self.num_cols = 0

    def generate(self) -> str:
        return "".join([str(_) for _ in self._items])

    def add_item(self, item: t.Union[str, ColumnFmt]) -> "TableColsDef":
        # get vars for current
        _current_fmt = ColumnFmt.enum_from_value(str(item))

        # if there were some items already added then do some validations
        if bool(self._items):
            if self._previous_fmt is ColumnFmt.insert_before:
                if not _current_fmt.is_legit_column:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Previous item added was for {ColumnFmt.insert_before}",
                            f"So we expect it to follow with legit column"
                        ]
                    )
            if _current_fmt is ColumnFmt.insert_after:
                if not self._previous_fmt.is_legit_column:
                    raise e.validation.NotAllowed(
                        msgs=[
                            f"Current item is for {ColumnFmt.insert_after} so we "
                            f"expect the previous item to be legit column",
                        ]
                    )

        # assign internal vars
        # noinspection PyAttributeOutsideInit
        self._previous_fmt = _current_fmt

        # set uses_stretched_fmt
        # noinspection PyAttributeOutsideInit
        self.uses_stretched_fmt = _current_fmt is ColumnFmt.stretched

        # increment col count
        if _current_fmt.is_legit_column:
            self.num_cols += 1

        # return ... note that we convert to str as Enums are not acceptable
        # noinspection PyTypeChecker
        return super().add_item(str(item))

    @classmethod
    def from_list(cls, items: t.List[t.Union[str, ColumnFmt]]) -> "TableColsDef":
        _ret = TableColsDef()
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
      \\RequirePackage{array}  useful for paragraph columns ... see TabularColsFmt
      \\RequirePackage{booktabs}  useful for professional line bars and looks
      \\RequirePackage{tabularx}  useful for auto sizing columns
      \\RequirePackage{ctable}  useful for ...
      \\RequirePackage{makecell}  useful for formatting table cell e.g. \\thead

    Also make sure you set this globally .. for vertical centering text in X column
    This is because the default is bottom ..
    # todo: find better ways later ... this doesn't seem to work though
    \\renewcommand\\tabularxcolumn[1]{m{#1}}

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
    t_pos: TablePos = TablePos.centered
    t_width: Scalar = None
    t_cols_def: TableColsDef = None

    # https://tex.stackexchange.com/questions/10863/is-there-a-way-to-slightly-shrink-a-table-including-font-size-to-fit-within-th
    # alternates adjustbox
    scale: t.Tuple[float, float] = None

    @property
    def is_auto_stretchable(self) -> bool:
        return self.type in ['*', 'X']

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
                f"\\begin{{table}}"
                f"{'' if self.positioning is None else self.positioning}",
            ]

        # add alignment
        if self.alignment is not None:
            _ret.append(f"{self.alignment}")

        # add caption and label ... on top for table
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}")

        # make width
        _width = ""
        if self.t_width is not None:
            _width = f"{{{self.t_width}}}"

        # add scalebox
        if self.scale is not None:
            _ret.append(f"\\scalebox{{{self.scale[0]}}}[{self.scale[1]}]\n{{")

        # add main table str
        _ret.append(
            f"\\begin{{{self.latex_type}}}"
            f"{_width}"
            f"[{self.t_pos}]"
            f"\n{self.t_cols_def}")

        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = [
            f"\\end{{{self.latex_type}}}",
        ]
        if self.scale is not None:
            _ret.append("}")
        if self.type != 'array':
            _ret += [
                "\\end{table}"
            ]
        return "\n".join(_ret)

    def init(self):
        # call super
        super().init()

        # there should be minimum one col present
        if self.t_cols_def.num_cols < 1:
            raise e.validation.NotAllowed(
                msgs=[
                    "Please specify at-least one legit column in `self.t_cols_def` ...",
                    "Did you miss to add items to it ???"
                ]
            )

    def init_validate(self):
        # call super
        super().init_validate()

        # should not be None
        if self.t_cols_def is None:
            raise e.validation.NotAllowed(
                msgs=[f"Please supply value for field `t_cols_fmt`"]
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

        # allow column format stretched i.e. X for type=='X'
        if self.t_cols_def.uses_stretched_fmt:
            if self.type != 'X':
                raise e.validation.NotAllowed(
                    msgs=[
                        f"YThe t_cols_def uses one or more {ColumnFmt.stretched}",
                        f"This is only allowed when table type is 'X' i.e. tabularx",
                    ]
                )

        # specify t_width when table is stretchable
        if self.is_auto_stretchable:
            if self.t_width is None:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"Please specify `t_width` as table is auto stretchable ..."
                    ]
                )

    def add_row(self, row: Row):
        if len(row) != self.t_cols_def.num_cols:
            raise e.validation.NotAllowed(
                msgs=[f"We only expect to have {self.t_cols_def.num_cols} items in "
                      f"row but instead we found {len(row)}"]
            )
        self.add_item(item=row)

    def add_hline(self):
        self.add_item(item="\\hline")

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
        self.add_item(item=f"\\cline{{{n}-{m}}}")

    def add_toprule(self, thickness: Scalar = None):
        """
        Offered by packages `booktabs` and `ctable`
        To be used instead of `add_hline`
        Must be used for first line and is thicker than others
        """
        _thickness = ""
        if thickness is not None:
            _thickness = f"[{thickness}]"
        self.add_item(item=f"\\toprule{_thickness}")

    def add_midrule(self, thickness: Scalar = None):
        """
        Offered by packages `booktabs` and `ctable`
        To be used instead of `add_hline`
        """
        _thickness = ""
        if thickness is not None:
            _thickness = f"[{thickness}]"
        self.add_item(item=f"\\midrule{_thickness}")

    def add_cmidrule(self, n: int, m: int, thickness: Scalar = None):
        """
        Offered by packages `booktabs` and `ctable`
        To be used instead of `add_cline`
        """
        if m < n or n <= 0:
            raise e.validation.NotAllowed(
                msgs=[
                    "Select n and m to be positive non-zero numbers and n<=m",
                    "Found", dict(n=n, m=m),
                ]
            )
        _thickness = ""
        if thickness is not None:
            _thickness = f"[{thickness}]"
        self.add_item(item=f"\\cmidrule{{{n}-{m}}}{_thickness}")

    def add_bottomrule(self, thickness: Scalar = None):
        """
        Offered by packages `booktabs` and `ctable`
        To be used instead of `add_hline`
        Must be used for last line and is thicker than others
        """
        _thickness = ""
        if thickness is not None:
            _thickness = f"[{thickness}]"
        self.add_item(item=f"\\bottomrule{_thickness}")


