

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Scalar, Positioning, FloatObjAlignment, Text, ParaPos, ParaBox


@dataclasses.dataclass
class ColumnFmt:
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

    insert_before = ">"
    - can be placed before a command l, r, c, p, m or b and inserts ins before
      the content of the cell;
    - can also be used to format certain columns:
      it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
      \\mgseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily

    insert_after = "<"
    - can be placed before a command l, r, c, p, m or b and inserts ins before
      the content of the cell;
    - can also be used to format certain columns:
      it is possible to use LATEX commands \\upshape, \\itshape, \\slshape, \\scshape,
      \\mgseries, \\bfseries, \\rmfamily, \\sffamily, and \\ttfamily
    """

    type: t.Literal['|', '||', 'l', 'c', 'r', 'p', 'm', 'b', 'X', '@', '!', ] = None
    width: Scalar = None
    # for 'X' mostly use "\\centering\\arraybackslash"
    insert_before: str = None
    insert_after: str = None
    insert_text: str = None

    def __post_init__(self):

        # ------------------------------------------------------- 01
        # validation
        # ------------------------------------------------------- 01.01
        # if stretched i.e. X cannot use any __call__
        # if vertical line's no kwargs will be used
        if self.type in ['|', '||', ]:
            if self.width is not None or self.insert_before is not None or self.insert_after is not None or self.insert_text is not None:
                raise e.validation.NotAllowed(
                    msgs=[f"While using column fmt {self.type} special options are not available"]
                )
        if self.type is None:
            raise e.validation.NotAllowed(msgs=["Field type is mandatory please supply"])
        # ------------------------------------------------------- 01.02
        # width can only be used with only para columns
        if self.width is not None:
            if self.type not in ['p', 'm', 'b', ]:
                raise e.validation.NotAllowed(
                    msgs=[
                        f"The width kwarg cannot be used with Column fmt {self.type}"
                    ]
                )
        # ------------------------------------------------------- 01.03
        # check if insert_before or insert_after allowed
        if self.insert_after is not None or self.insert_before is not None:
            _allowed_insert_before_after = self.type in [
                'c', 'l', 'r', 'p', 'm', 'b', 'X',
            ]
            if not _allowed_insert_before_after:
                raise e.code.NotAllowed(
                    msgs=[
                        f"Do not use fields `insert_before` or `insert_after` with column fmt {self.type}",
                        f"It can only be used with l, c, r, p, m, b (and even X)"
                    ]
                )
        # ------------------------------------------------------- 01.04
        # insert_text is to be used only for special insert and insert_1 column fmts
        if self.type in ['@', '!']:
            if self.insert_text is None:
                raise e.code.CodingError(
                    msgs=[
                        f"When using column fmt type {['@', '!']} please supply kwarg `insert_text`"
                    ]
                )
        else:
            if self.insert_text is not None:
                raise e.code.CodingError(
                    msgs=[
                        f"Field insert_text can only be used with column fmt type {['@', '!']}"
                    ]
                )

    def __str__(self):
        """
        for 'X' mostly use "\\centering\\arraybackslash"
        """
        # ------------------------------------------------------- 01
        # cook return
        _ret = ""
        # ------------------------------------------------------- 01.01
        if self.type in ['|', '||', ]:
            return self.type
        # ------------------------------------------------------- 01.01
        # if insert_text
        # note this only triggers for insert and insert_1 based on above validation
        if self.insert_text is not None:
            return f"{self.type}{{{self.insert_text}}}"
        # ------------------------------------------------------- 01.02
        # for width ...
        if self.width is None:
            _ret += self.type
        else:
            _ret += f"{self.type}{{{self.width}}}"
        # ------------------------------------------------------- 01.03
        # insert_after and insert_before
        _insert_before = ""
        if self.insert_before is not None:
            _insert_before += f">{{{self.insert_before}}}"
        _insert_after = ""
        if self.insert_after is not None:
            _insert_after += f"<{{{self.insert_after}}}"
        _ret = _insert_before + _ret + _insert_after

        # ------------------------------------------------------- 02
        # return
        return _ret

    @classmethod
    def vertical_line(cls) -> "ColumnFmt":
        # vertical line
        return ColumnFmt(type="|")

    @classmethod
    def double_vertical_line(cls) -> "ColumnFmt":
        # double vertical line
        return ColumnFmt(type="||")

    @classmethod
    def left_justified(cls,  insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # left-justified column
        return ColumnFmt(type='l', insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def centered(cls,  insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # centred column
        return ColumnFmt(type='c', insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def right_justified(cls,  insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # right-justified column
        return ColumnFmt(type='r', insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def para_top(cls,  width: Scalar = None, insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # paragraph column with text vertically aligned at the top
        return ColumnFmt(type='p', width=width, insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def para_middle(cls,  width: Scalar = None, insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # paragraph column with text vertically aligned in the middle (requires array package)
        return ColumnFmt(type='m', width=width, insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def para_bottom(cls,  width: Scalar = None, insert_before: str = None, insert_after: str = None) -> "ColumnFmt":
        # paragraph column with text vertically aligned at the bottom (requires array package)
        return ColumnFmt(type='b', width=width, insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def stretched(
        cls, insert_before: str = None, insert_after: str = None
    ) -> "ColumnFmt":
        # The tabularx package requires the same arguments of tabular* but, in order to
        # let the table have the width specified by the user, it modifies the width of
        # certain columns instead of the space between columns. The columns that can be
        # stretched are identified by the alignment command X. This package requires the
        # array package.
        return ColumnFmt(type="X", insert_before=insert_before, insert_after=insert_after)

    @classmethod
    def insert(cls, insert_text: str = None) -> "ColumnFmt":
        # check; https://en.wikibooks.org/wiki/LaTeX/Tables#@_and_!_expressions
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
        return ColumnFmt(type='@', insert_text=insert_text)

    @classmethod
    def insert_1(cls, insert_text: str = None) -> "ColumnFmt":
        # Difference between @ and !
        #   The @{...} command kills the inter-column space and replaces it
        #   with whatever is between the curly braces. To keep the initial space,
        #   use !{...}. To add space, use @{\hspace{''width''}}
        return ColumnFmt(type='!', insert_text=insert_text)


@dataclasses.dataclass
class MultiRowCell:
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

    num_rows: int
    width: Scalar = None
    value: t.Union[LaTeX, str, Text, ParaBox] = None

    def __str__(self) -> str:
        _width = ""
        if self.width is not None:
            _width = f"{{{self.width}}}"
        _ret = f"\\multirow{{{self.num_rows}}}{_width}*{{{self.value}}}"
        return _ret


@dataclasses.dataclass
class MultiColumnCell:
    num_cols: int
    t_cols_def: "TableColsDef"
    value: t.Union[LaTeX, str, Text, ParaBox] = ""

    def __str__(self) -> str:
        _ret = f"\\multicolumn{{{self.num_cols}}}{self.t_cols_def.single_line_repr_for_use_in_multi_col_cell()}{{{self.value}}}"
        return _ret


@dataclasses.dataclass
class TableColsDef:

    items: t.List[ColumnFmt] = None

    @property
    def uses_stretched_fmt(self) -> bool:
        for _fmt in self.items:
            if _fmt.type == 'X':
                return True
        return False

    def __post_init__(self):
        if self.items is None:
            raise e.validation.NotAllowed(msgs=["Field list is mandatory ..."])

    def __str__(self):
        _ret = []
        _num_cols = 0
        for _fmt in self.items:
            if _fmt.type in ['|', '||', '@', '!', ]:
                _ret.append(f"% Column Def [---] for {_fmt.type}")
            else:
                _ret.append(f"% Column Def [{_num_cols:03d}] for {_fmt.type}")
                _num_cols += 1
            _ret.append(str(_fmt))
        _ret = [f"     {_}" for _ in _ret]
        return "{\n" + "\n".join(_ret) + "\n}"

    def __len__(self):
        _num_cols = 0
        for _fmt in self.items:
            if _fmt.type in ['|', '||', '@', '!', ]:
                continue
            _num_cols += 1
        return _num_cols


    def single_line_repr_for_use_in_multi_col_cell(self):
        _ret = []
        for _fmt in self.items:
            _ret.append(str(_fmt))
        return "{" + "".join(_ret) + "}"


@dataclasses.dataclass
class Row(LaTeX):
    items: t.List[t.Union[str, LaTeX, Text, ParaBox]] = None
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
        _ret = len(self.items)
        for _ in self.items:
            if isinstance(_, MultiColumnCell):
                _ret += (_.num_cols - 1)
        return _ret

    def init_validate(self):
        super().init_validate()
        if self.items is None:
            raise e.validation.NotAllowed(
                msgs=["items field is mandatory, please supply"]
            )

    def generate(self):
        _ret = ""
        if self.color is not None:
            _ret += f"\\rowcolor{{{self.color}}}  % color for row\n"
        _ret += " &\n".join([f"     {_}" for _ in self.items])
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
        if len(self.t_cols_def) < 1:
            raise e.validation.NotAllowed(
                msgs=[
                    "Please specify at-least one legit column in `self.t_cols_def.items` ...",
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
        if len(row) != len(self.t_cols_def):
            raise e.validation.NotAllowed(
                msgs=[f"We only expect to have {len(self.t_cols_def)} items in "
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

    def add_cmidrule(self, n: int, m: int, thickness: Scalar = None, left_trim: Scalar = None, right_trim: Scalar = None):
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
        _trim = ""
        if left_trim is not None or right_trim is not None:
            _trim = "("
            if left_trim is not None:
                _trim += f"l{{{left_trim}}}"
            if right_trim is not None:
                _trim += f"r{{{right_trim}}}"
            _trim += ")"
        self.add_item(item=f"\\cmidrule{_thickness}{_trim}{{{n}-{m}}}")

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


