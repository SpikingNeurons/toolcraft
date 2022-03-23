

import dataclasses
import typing as t
import abc
import enum
import numpy as np

from .. import error as e
from .. import util
from .__base__ import LaTeX, Color, Font, Scalar, Positioning, TextAlignment


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

    def __call__(self, width: Scalar = None):
        if width is None:
            return self.value
        else:
            if self in [self.para_top, self.para_middle, self.para_bottom]:
                return f"{self.value}{{{width}}}"
            else:

    def __str__(self) -> str:
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
class Table(LaTeX):
    """
    https://www.overleaf.com/learn/latex/Tables
    """

    positioning: Positioning = None
    alignment: TextAlignment = None
    caption: str = None
    tabular_cols_fmt: TabularColsFmt = None
    tabular_pos: TabularPos = TabularPos.centered

    @property
    def open_clause(self) -> str:
        _ret = [
            f"% >> start table {'...' if self.label is None else self.label}",
            f"\\begin{{table}}{'' if self.positioning is None else self.positioning}%",
        ]
        if self.alignment is not None:
            _ret.append(f"{self.alignment}%")
        _ret.append("% >> start tabular")
        _columns_fmt = ""
        _ret.append(f"\\begin{{tabular}}[{self.tabular_pos}]{{{_columns_fmt}}}%")
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = ["% >> end tabular", "\\end{tabular}%"]
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}%")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}%")
        _ret += [
            f"% >> end table {'...' if self.label is None else self.label}",
            "\\end{table}%"
        ]
        return "\n".join(_ret)

    def __str__(self):
        if bool(self.items):
            # todo: address this issue later
            raise e.code.CodingError(
                msgs=["Do not call this twice as self.items will be populated again"]
            )

        # keep reference for _tikz ...
        # __str__ is like build, so we do these assignments here
        for _p in self.paths:
            # LaTeX parent class does not understand Path it only understands str or
            # subclasses of LaTeX
            self.items.append(str(_p))

        # return
        return super().__str__()

    def init_validate(self):
        # call super
        super().init_validate()
        if self.tabular_cols_fmt is None:
            raise e.validation.NotAllowed(
                msgs=[f"Please supply value for field `tabular_cols_fmt`"]
            )
