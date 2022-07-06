"""
https://www.overleaf.com/learn/latex/Beamer
"""
import dataclasses
import abc
import typing as t
import pathlib

from . import LaTeX
from .. import error as e
from .. import logger
from .. import util
from . import helper

_LOGGER = logger.get_logger()


@dataclasses.dataclass
class _AtBegin(LaTeX, abc.ABC):

    # the text that will be shown for starred beamer sections (beamer._Sec)
    starred_text: str = None

    @property
    def command(self) -> str:
        return self.__class__.__name__

    @property
    def open_clause(self) -> str:
        _starred_txt = ""
        if self.starred_text is not None:
            _starred_txt = self.starred_text
        return f"\\{self.command}[{_starred_txt}]{{"

    @property
    def close_clause(self) -> str:
        return "}"


@dataclasses.dataclass
class AtBeginSection(_AtBegin):
    ...


@dataclasses.dataclass
class AtBeginSubsection(_AtBegin):
    ...


@dataclasses.dataclass
class AtBeginSubsubsection(_AtBegin):
    ...


@dataclasses.dataclass
class _Sec(LaTeX, abc.ABC):
    """
    Refer: 10.2 Adding Sections and Subsections

    todo: read section 8.4 Restricting the Slides of a Frame ... to improve mode field usage ....
      useful to generate slides for printing or lecturing ...

    """
    name: str = None
    short_name: str = None
    starred: bool = False
    mode: str = None

    @property
    def command(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def open_clause(self) -> str:
        _mode = ""
        if self.mode is not None:
            _mode = f"<{self.mode}>"

        _short_name = ""
        if self.starred:
            _short_name = "*"
        if self.short_name is not None:
            _short_name = f"[{self.short_name}]"

        _ret = f"\\{self.command}{_mode}{_short_name}{{{self.name}}}"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}"

        return _ret

    @property
    def close_clause(self) -> str:
        return ""

    def init_validate(self):
        if self.starred:
            if self.short_name is not None:
                raise e.validation.NotAllowed(
                    msgs=["In starred mode you cannot use short name "]
                )


@dataclasses.dataclass
class Section(_Sec):
    ...


@dataclasses.dataclass
class SubSection(_Sec):
    ...


@dataclasses.dataclass
class SubSubSection(_Sec):
    ...


@dataclasses.dataclass
class Beamer(LaTeX):

    # refer: https://latex-beamer.com/tutorials/beamer-themes/
    theme: t.Literal[
        'default', 'Darmstadt', 'Malmoe', 'AnnArbor', 'Dresden', 'Marburg', 'Antibes', 'Frankfurt', 'Montpellier',
        'Bergen', 'Goettingen', 'PaloAlto', 'Berkeley', 'Hannover', 'Pittsburgh', 'Berlin', 'Ilmenau', 'Rochester',
        'Boadilla', 'JuanLesPins', 'Singapore', 'CambridgeUS', 'Luebeck', 'Szeged', 'Copenhagen', 'Madrid', 'Warsaw',
    ] = "Berkeley"

    # refer:
    aspect_ratio: t.Literal[1610, 169, 149, 54, 43, 32] = 169

    title: str = None
    short_title: str = None
    sub_title: str = None
    author: str = None
    short_author: str = None
    institute: str = None
    short_institute: str = None
    date: str = None
    # bib_file: str = None
    # logo: ... # 3. Add a logo in Beamer https://latex-beamer.com/quick-start/

    # https://tex.stackexchange.com/questions/137022/how-to-insert-page-number-in-beamer-navigation-symbols
    # figure out how to have options to modify template
    add_to_beamer_template: str = "\n".join(
        [
            # "\\usepackage[english]{babel}",
            # "\\usepackage[utf8]{inputenc}",
            # "\\setbeamercolor{structure}{fg=teal}",
            "\\usetheme[left]{Goettingen}",
            # "\\setbeamercolor{navigation symbols}{fg=green, bg=blue!50}",
            # "\\setbeamercolor{palette sidebar secondary}{fg=yellow,bg=blue}",
            # "\\setbeamercolor{section in sidebar shaded}{fg=red,bg=black}",
            # "\\setbeamercolor{footline}{fg=teal}",
            # "\\setbeamertemplate{itemize items}[square]",
            # "\\setbeamertemplate{enumerate items}[square]",
            "\\setbeamercolor{background canvas}{bg=blue!5!white}",
            # "\\setbeamercolor{palette sidebar primary}{bg=green!25!blue,fg=white}",
            # "\\setbeamercolor{section in sidebar shaded}{fg=green!20!black,bg=blue!20}",
            # "\\setbeamercolor{structure canvas}{bg=green}"
            "\\setbeamerfont{footline}{series=\\bfseries}",
            "\\addtobeamertemplate{navigation symbols}{}{",
            "\\usebeamerfont{footline}",
            "\\usebeamercolor[fg]{footline}",
            "\\hspace{1em}",
            "\\raisebox{1.5pt}[0pt][0pt]{\\insertframenumber/\\inserttotalframenumber}",
            "}",
            # "\\setbeamercolor{structure}{fg=red}\n",
        ]
    )

    symbols_file: str = "symbols.tex"
    usepackage_file: str = "usepackage.sty"

    at_begin_section: AtBeginSection = None
    at_begin_subsection: AtBeginSubsection = None
    at_begin_subsubsection: AtBeginSubsubsection = None

    @property
    @util.CacheResult
    def labels(self) -> t.List[str]:
        return []

    @property
    def open_clause(self) -> str:
        _ret = []

        if self.add_to_beamer_template is not None:
            _ret.append(
                self.add_to_beamer_template
            )

        # if self.bib_file is not None:
        #     # https://github.com/FedericoTartarini/youtube-beamer-tutorial/blob/%234-bibliography/main.tex
        #     _ret.append("\\usepackage[backend=biber, style=authoryear]{biblatex}")
        #     _ret.append("\\usepackage{biblatex}")
        #     _ret.append(f"\\addbibresource{{{self.bib_file}}}")
        #     _ret.append("\\AtBeginBibliography{\\small}")
        #     ...

        # _tt.append(f"\\usetheme[left]{{{self.theme}}}")
        if self.title is not None:
            _title = "\\title"
            if self.short_title is not None:
                _title += f"[{self.short_title}]"
            _title += f"{{{self.title}}}"
            _ret.append(_title)
        if self.sub_title is not None:
            _ret.append(f"\\subtitle{{{self.sub_title}}}")
        if self.author is not None:
            _auth = "\\author"
            if self.short_author is not None:
                _auth += f"[{self.short_author}]"
            _auth += f"{{{self.author}}}"
            _ret.append(_auth)
        if self.institute is not None:
            _inst = "\\institute"
            if self.short_institute is not None:
                _inst += f"[{self.short_institute}]"
            _inst += f"{{{self.institute}}}"
            _ret.append(_inst)
        if self.date is not None:
            _ret.append(f"\\date{{{self.date}}}")

        # at begin .... related stuff
        if self.at_begin_section is not None:
            _ret += [str(self.at_begin_section)]
        if self.at_begin_subsection is not None:
            _ret += [str(self.at_begin_subsection)]
        if self.at_begin_subsubsection is not None:
            _ret += [str(self.at_begin_subsubsection)]

        # begin document
        _ret += ["\\begin{document}"]

        # make title page frame ... todo: we keep this always .... if needed disable later
        _ret += [
            "\\begin{frame}\n\\titlepage\n\\end{frame}",
        ]

        # return
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        return "\\end{document}"

    def init_validate(self):
        super().init_validate()
        if self.label is not None:
            raise e.code.CodingError(
                msgs=[f"No need to set label for {self.__class__}"]
            )

    def init(self):
        super().init()
        if self._parent is not None:
            raise e.code.CodingError(
                msgs=[f"No need to set _parent for {self.__class__}"]
            )
        # noinspection PyAttributeOutsideInit
        self._parent = self

        # handle symbols_file
        if not pathlib.Path(self.symbols_file).exists():
            _LOGGER.warning(
                msg=f"The configured symbols file {self.symbols_file} is "
                    f"not on disk so using creating default file ...")
            pathlib.Path(self.symbols_file).touch()

        # handle usepackage_file ... we always overwrite with our default file
        if pathlib.Path(self.usepackage_file).exists():
            pathlib.Path(self.usepackage_file).unlink()
        pathlib.Path(self.usepackage_file).write_text(
            (pathlib.Path(__file__).parent / "usepackage.sty").read_text()
        )

    def write(
        self,
        save_to_file: str,
        make_pdf: bool = False,
    ):
        # ----------------------------------------------- 01
        # make document
        _all_lines = [
            # f"% Generated on {datetime.datetime.now().ctime()}",
            "",
            f"\\documentclass[aspectratio={self.aspect_ratio}]{{beamer}}",
            f"\\usepackage{{{self.usepackage_file.split('.')[0]}}}",
            f"\\input{{{self.symbols_file.split('.')[0]}}}",
            "",
            str(self),
            "",
        ]

        # ----------------------------------------------- 02
        _save_to_file = pathlib.Path(save_to_file)
        _save_to_file.write_text("\n".join(_all_lines))

        # ----------------------------------------------- 03
        # make pdf if requested
        if make_pdf:
            helper.make_pdf_with_pdflatex(
                tex_file=_save_to_file,
                pdf_file=_save_to_file.parent /
                         (_save_to_file.name.split(".")[0] + ".pdf"),
                # clean=True,
            )


@dataclasses.dataclass
class Frame(LaTeX):

    """
    todo: read section 8.4 Restricting the Slides of a Frame ....
      useful to generate slides for printing or lecturing ...
    """

    title: str = None
    allow_frame_breaks: bool = False
    no_frame_numbering: bool = False
    mode: str = None  # todo: read Restricting the Slides of a Frame

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
        _mode = ""
        if self.mode is not None:
            _mode = f"<{self.mode}>"
        _ret = f"\\begin{{frame}}{_options}{_mode}\n"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}\n"
        if self.title is not None:
            _ret += f"\\frametitle{{{self.title}}}"
        return _ret

    @property
    def close_clause(self) -> str:
        return "\\end{frame}"


@dataclasses.dataclass
class TableOfContents(Frame):
    """
    TableOfContents geared for Beamer ... for normal TableOfContents implement separately
    """
    # frame related
    title: str = "Outline"
    no_frame_numbering: bool = True

    # _toc_options check section 10.5 Adding a Table of Contents
    current_section: bool = False  # shorthand for sectionstyle=show/shaded,subsectionstyle=show/show/shaded
    current_subsection: bool = False  # shorthand for subsectionstyle=show/shaded
    first_section: int = None  # specifies which section should be numbered as section “1.”
    hide_all_subsections: bool = False  # shorthand for subsectionstyle=hide .. causes all subsections to be hidden
    hide_other_subsections: bool = False  # shorthand for subsectionstyle=show/show/hide .. causes the subsections of sections other than the current one to be hidden
    last_section: int = None  # specifies which section should be last
    # pasrt={}  todo: do this later
    pause_sections: bool = False  # This is useful if you wish to show the table of contents in an incremental way.
    pause_subsections: bool = False
    # sections={⟨overlay specification⟩} causes only the sections mentioned in the ⟨overlay specification⟩
    # to be shown. For example, sections={<2-4| handout:0>} causes only the second, third, and fourth section
    # to be shown in the normal version, todo: later
    # "show/hide" sectionstyle=
    # ⟨style for current section⟩/
    # ⟨style for other sections⟩
    section_style: str = None
    # "shaded/show/hide" subsectionstyle=
    # ⟨style for current subsection⟩/
    # ⟨style for other subsections in current section⟩/
    # ⟨style for subsections in other sections⟩
    subsection_style: str = None
    # "shaded/shaded/show/hide" subsubsectionstyle=
    # ⟨style for current subsubsection⟩/
    # ⟨style for other subsubsections in current subsection⟩/
    # ⟨style for subsubsections in other subsections in current section⟩/
    # ⟨style for subsubsections in other subsections in other sections⟩
    subsubsection_style: str = None

    @property
    def allow_add_items(self) -> bool:
        """
        This is specialized frame to hold table of content so we do not allow to add items
        """
        return False

    @property
    def open_clause(self) -> str:

        # get from super
        _ret = super().open_clause

        # tableofcontents with options ...
        _toc = "\\tableofcontents"
        _toc_options = []
        if self.current_section:
            _toc_options.append("currentsection")
        if self.current_subsection:
            _toc_options.append("currentsubsection")
        if self.first_section is not None:
            _toc_options.append(f"firstsection={self.first_section}")
        if self.hide_all_subsections:
            _toc_options.append("hideallsubsections")
        if self.hide_other_subsections:
            _toc_options.append("hideothersubsections")
        if self.last_section is not None:
            _toc_options.append(f"lastsection={self.first_section}")
        # part=⟨part number⟩ todo later
        if self.pause_sections:
            _toc_options.append("pausesections")
        if self.pause_subsections:
            _toc_options.append("pausesubsections")
        # sections={⟨overlay specification⟩} ... todo later
        if self.section_style is not None:
            _toc_options.append(f"sectionstyle={self.section_style}")
        if self.subsection_style is not None:
            _toc_options.append(f"subsectionstyle={self.subsection_style}")
        if self.subsubsection_style is not None:
            _toc_options.append(f"subsubsectionstyle={self.subsubsection_style}")
        if bool(_toc_options):
            _toc += "[" + ",".join(_toc_options) + "]"
        else:
            _toc += "[]"
        _ret += _toc + "\n"

        # return
        return _ret


@dataclasses.dataclass
class _SecPage(Frame):
    """
    Check 10.2 Adding Sections and Subsections

    todo: dont know how to use below things
        The following commands are useful for this template:
        • \insertsection inserts the title of the current section.
        • \insertsectionnumber inserts the current section number.

    todo: hangs up pdflatex .... but text files gets generated
    """

    @property
    def command(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def allow_add_items(self) -> bool:
        """
        This is specialized frame to display section page
        todo: maybe you can allow more items here .. do when you need
        """
        return False

    @property
    def open_clause(self) -> str:
        # get from super
        _ret = super().open_clause

        # add the respective command
        _ret += f"\\{self.command}"

        # return
        return _ret


@dataclasses.dataclass
class SectionPage(_SecPage):
    ...


@dataclasses.dataclass
class SubSectionPage(_SecPage):
    ...


@dataclasses.dataclass
class Bibliography(Frame):

    style: str = "plain"
    file: pathlib.Path = None
    allow_frame_breaks: bool = True
    no_frame_numbering: bool = True

    @property
    def allow_add_items(self) -> bool:
        return False

    def generate(self) -> str:

        # add the respective command
        _ret = f"\\bibliographystyle{{{self.style}}}\n"

        # file
        _ret += f"\\bibliography{{{self.file.as_posix()}}}"

        # return
        return _ret

    def init_validate(self):

        # call super
        super().init_validate()

        # test file
        if self.file is None:
            raise e.validation.NotAllowed(
                msgs=["Please set mandatory field `file`"]
            )
        if not self.file.exists():
            raise e.validation.NotAllowed(
                msgs=[f"Cannot find `bib` file {self.file} on the disk ..."]
            )

