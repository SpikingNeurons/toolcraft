

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Scalar, Positioning, FloatObjAlignment, Text, ParaPos, ParaBox


class ColumnFmt(enum.Enum):
    """
    https://en.wikibooks.org/wiki/LaTeX/Tables

    https://www.overleaf.com/learn/latex/Tables

    \\begin{tabular}[pos]{table spec}
       table content
    \\end{tabular}

    Deals with cols which defines the alignment and the borders of each column

    Tips:
    [1] In para mode you can use newline command
        \begin{tabular}{|p{2cm}|p{2cm}|}
        \hline
        Test & foo \newline bar \\
        ...

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
    # vertical line
    vertical_line = "|"
    # double vertical line
    double_vertical_line = "||"

    # The tabularx package requires the same arguments of tabular* but, in order to
    # let the table have the width specified by the user, it modifies the width of
    # certain columns instead of the space between columns. The columns that can be
    # stretched are identified by the alignment command X. This package requires the
    # array package.
    stretched = "X"

    # check; https://en.wikibooks.org/wiki/LaTeX/Tables
    #        @ and ! expressions
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
    #
    # Difference between @ and !
    #   The @{...} command kills the inter-column space and replaces it
    #   with whatever is between the curly braces. To keep the initial space,
    #   use !{...}. To add space, use @{\hspace{''width''}}
    insert = '@'
    insert_1 = '!'

    def __call__(
        self,
        width: Scalar = None,
        insert_before: str = None,
        insert_after: str = None,
        insert_text: str = None,
    ) -> str:
        """

        insert_before = ">"
        - can be placed before a command l, r, c, p, m or b and inserts ins before
          the content of the cell;
        - can also be used to format certain columns:
          it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
          \\mdseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily

        insert_after = "<"
        - can be placed before a command l, r, c, p, m or b and inserts ins before
          the content of the cell;
        - can also be used to format certain columns:
          it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
          \\mdseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily
        """
        # ------------------------------------------------------- 01
        # validation
        # ------------------------------------------------------- 01.01
        # if stretched i.e. X cannot use any __call__
        # if vertical line's no kwargs will be used
        e.validation.ShouldNotBeOneOf(
            value=self,
            values=[
                self.vertical_line, self.double_vertical_line,
            ],
            msgs=[
                "Do not use __call__ for this ColumnFmt"
            ]
        ).raise_if_failed()
        # ------------------------------------------------------- 01.02
        # width can only be used with only para columns
        if width is not None:
            if self not in [self.para_top, self.para_bottom, self.para_middle]:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"The width kwarg cannot be used with {self}"
                    ]
                )
        # ------------------------------------------------------- 01.03
        # check if insert_before or insert_after allowed
        if insert_after is not None or insert_before is not None:
            _allowed_insert_before_after = self in [
                self.centered, self.left_justified, self.right_justified,
                self.para_middle, self.para_top, self.para_bottom,
                self.stretched,
            ]
            if not _allowed_insert_before_after:
                raise e.code.NotAllowed(
                    msgs=[
                        f"Do not use kwargs `insert_before` or `insert_after` with {self}",
                        f"It can only be used with l, c, r, p, m, b (and even X)"
                    ]
                )
        # ------------------------------------------------------- 01.04
        # insert_text is to be used only for special inset and insert_1 column fmts
        if self in [self.insert, self.insert_1]:
            if insert_text is None:
                raise e.code.CodingError(
                    msgs=[
                        f"When using {self.insert} and {self.insert_1} please supply kwarg `insert_text`"
                    ]
                )

        # ------------------------------------------------------- 02
        # cook return
        _ret = ""
        # ------------------------------------------------------- 02.01
        # if insert_text
        # note this only triggers for inset and insert_1 based on above validation
        if insert_text is not None:
            return f"{self.value}{{{insert_text}}}"
        # ------------------------------------------------------- 02.02
        # for width ...
        if width is None:
            _ret += self.value
        else:
            _ret += f"{self.value}{{{width}}}"
        # ------------------------------------------------------- 02.03
        # insert_after and insert_before
        _insert_before = ""
        if insert_before is not None:
            _insert_before += f">{{{insert_before}}}\n"
        _insert_after = ""
        if insert_after is not None:
            _insert_after += f"\n<{{{insert_after}}}"
        _ret = _insert_before + _ret + _insert_after

        # ------------------------------------------------------- 03
        # return
        return _ret

    def __str__(self) -> str:
        if self in [
            self.vertical_line, self.double_vertical_line,
        ]:
            return self.value
        else:
            return self.__call__()

    @classmethod
    def enum_from_value(cls, _str: str) -> "ColumnFmt":
        for _s in _str.split("\n"):
            # handle || separately
            if _s[0:2] == "||":
                return cls.double_vertical_line
            # get start token
            _ss = _s[0:1]
            # this addresses tokes for insert before and after
            if _ss in [">", "<"]:
                continue
            else:
                for _ in cls:
                    if _.value == _ss:
                        return _
        raise e.validation.NotAllowed(
            msgs=[
                f"Cannot recognize string `{_str}`",
                "Should be one of:",
                [_.value for _ in cls]
            ]
        )


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
    value: t.Union[LaTeX, str, Text, ParaBox] = None
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
    t_cols_def: "TableColsDef" = None
    value: t.Union[LaTeX, str, Text, ParaBox] = None
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
        if self.t_cols_def is None:
            raise e.validation.NotAllowed(
                msgs=[f"please provide mandatory field t_cols_def"]
            )

    def generate(self) -> str:
        if bool(self._items):
            raise e.code.CodingError(
                msgs=[
                    f"Was expecting this to be empty ..."
                ]
            )

        _ret = f"\\multicolumn{{{self.num_cols}}}\n{self.t_cols_def}\n{{{self.value}}}"

        return _ret


@dataclasses.dataclass
class Row(LaTeX):

    # start new row (additional space may be specified after \\ using square brackets, such as \\[6pt])
    height: Scalar = None

    color: t.Union[Color, str] = None

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
        cls,
        items: t.List[t.Union[str, LaTeX, Text, ParaBox]],
        height: Scalar = None,
        color: t.Union[str, Color] = None,
    ) -> "Row":
        _ret = Row(height=height, color=color)
        for _ in items:
            _ret.add_item(_)
        return _ret

    def generate(self) -> str:
        _ret = ""
        if self.color is not None:
            _ret += f"\\rowcolor{{{self.color}}}  % color for row\n"
        _ret += " & ".join([str(_) for _ in self._items])
        return _ret


@dataclasses.dataclass
class TableColsDef(LaTeX):

    @property
    def use_single_line_repr(self) -> bool:
        return True

    @property
    def open_clause(self) -> str:
        return "{\n"

    @property
    def close_clause(self) -> str:
        return "\n}"

    @property
    def uses_stretched_fmt(self) -> bool:
        try:
            # noinspection PyUnresolvedReferences
            return self._uses_stretched_fmt
        except AttributeError:
            return False

    def init(self):
        # call super
        super().init()

        # some vars to track previous items
        # noinspection PyAttributeOutsideInit
        self._num_cols = 0

    def generate(self) -> str:
        return "\n".join("    " + str(_) for _ in self._items)

    def add_item(self, item: t.Union[str, ColumnFmt]) -> "TableColsDef":

        # this will end up testing if tem is legit
        _current_fmt = ColumnFmt.enum_from_value(str(item))

        # if stretched set internal var
        if _current_fmt is ColumnFmt.stretched:
            # noinspection PyAttributeOutsideInit
            self._uses_stretched_fmt = True

        # increment col count
        if _current_fmt in [
            ColumnFmt.vertical_line, ColumnFmt.double_vertical_line,
            ColumnFmt.insert, ColumnFmt.insert_1
        ]:
            super().add_item(f"% Column Def [---] for {_current_fmt}")
        else:
            super().add_item(f"% Column Def [{self._num_cols:03d}] for {_current_fmt}")
            self._num_cols += 1

        # if str has \n then make multiple add items
        # this is helpful for insert_before and insert_after
        _str_item = str(item)
        for _s in _str_item.split("\n"):
            super().add_item(_s)

        # return
        return self

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
    t_pos: ParaPos = ParaPos.centered
    t_width: t.Optional[Scalar] = None
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
        if self.t_cols_def._num_cols < 1:
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
                        f"The t_cols_def uses one or more {ColumnFmt.stretched}",
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
        if len(row) != self.t_cols_def._num_cols:
            raise e.validation.NotAllowed(
                msgs=[f"We only expect to have {self.t_cols_def._num_cols} items in "
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


