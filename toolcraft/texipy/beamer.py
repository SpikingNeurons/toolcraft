"""
https://www.overleaf.com/learn/latex/Beamer
"""
from . import LaTeX, Beamer
import dataclasses


@dataclasses.dataclass
class TableOfContents(LaTeX):
    """
    TableOfContents geared for Beamer ... for normal TableOfContents implement separately
    """

    title: str = "Outline"
    hide_all_subsections: bool = False
    pause_sections: bool = False
    current_section: bool = False
    current_sub_section: bool = False

    # https://tex.stackexchange.com/questions/11100/beamer-atbeginsection-and-insertsubsectionnavigation
    section_style: str = None  # "show//hide"
    sub_section_style: str = None  # "hide//show//hide"

    @property
    def allow_add_items(self) -> bool:
        """
        This is specialized frame to hold table of content so we do not allow to add items
        """
        return False

    @property
    def open_clause(self) -> str:

        # add \AtBeginSubsection[]
        if self.current_section or self.current_sub_section:
            _ret = "\\AtBeginSubsection[]{\n" \
                   "\\begin{frame}[noframenumbering]\n"
        else:
            _ret = "\\begin{frame}[noframenumbering]\n"

        # add other frame settings
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}\n"
        if self.title is not None:
            _ret += f"\\frametitle{{{self.title}}}\n"

        # tableofcontents with options ...
        _toc = "\\tableofcontents"
        _toc_options = []
        if self.hide_all_subsections:
            _toc_options.append("hideallsubsections")
        if self.pause_sections:
            _toc_options.append("pausesections")
        if self.current_section:
            _toc_options.append("currentsection")
        if self.current_sub_section:
            _toc_options.append("currentsubsection")
        if self.section_style is not None:
            _toc_options.append(f"sectionstyle={self.section_style}")
        if self.sub_section_style is not None:
            _toc_options.append(f"subsectionstyle={self.sub_section_style}")
        if bool(_toc_options):
            _toc += "[" + ",".join(_toc_options) + "]"
        else:
            _toc += "[]"
        _ret += _toc

        # add final clause
        if self.current_section or self.current_sub_section:
            _ret += "\n\\end{frame}}"
        else:
            _ret += "\n\\end{frame}"

        # return
        return _ret

    @property
    def close_clause(self) -> str:
        return ""


@dataclasses.dataclass
class Frame(LaTeX):

    title: str = None
    allow_frame_breaks: bool = False
    no_frame_numbering: bool = False

    @property
    def open_clause(self) -> str:
        # frame options
        _options = []
        if self.allow_frame_breaks:
            _options.append("allowframebreaks")
        if self.no_frame_numbering:
            _options.append("noframenumbering")
        if bool(_options):
            _options = "[" + ",".join(_options) + "]"
        else:
            _options = ""

        # frame
        _ret = f"\\begin{{frame}}{_options}\n"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}\n"
        if self.title is not None:
            _ret += f"\\frametitle{{{self.title}}}"
        return _ret

    @property
    def close_clause(self) -> str:
        return "\\end{frame}"

