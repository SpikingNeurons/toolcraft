import dataclasses
import typing as t
import pathlib
import datetime
import abc
import enum

from . import helper
from .. import logger
from .. import util
from .. import error as e

_LOGGER = logger.get_logger()


class Font(enum.Enum):
    """
    todo: figure out other options later
    """
    italic = "\\itshape"
    footnotesize = "\\footnotesize"

    def __str__(self) -> str:
        return self.value


class Color(enum.Enum):
    """

    Refer:
    https://www.overleaf.com/learn/latex/TikZ_package
    https://www.overleaf.com/learn/latex/Using_colours_in_LaTeX

    As noted in the xcolor package documentation, the following named colours
    are always available without needing to load any package options.
    Additional named colours can be accessed via the following xcolor package options:
        dvipsnames: loads 68 named colours (CMYK)
        svgnames: loads 151 named colours (RGB)
        x11names: loads 317 named colours (RGB)
    Example: \\usepackage[dvipsnames]{xcolor}

    `\\usepackage{xcolor}` is anyway loaded and no need to load it explicitly
        we have 19 colors below available

    """
    # setting ⟨color⟩ to none disables filling/drawing locally
    none = "none"

    red = "red"
    green = "green"
    blue = "blue"
    cyan = "cyan"
    magenta = "magenta"

    yellow = "yellow"
    black = "black"
    gray = "gray"
    white = "white"
    darkgray = "darkgray"

    lightgray = "lightgray"
    brown = "brown"
    lime = "lime"
    olive = "olive"
    orange = "orange"

    pink = "pink"
    purple = "purple"
    teal = "teal"
    violet = "violet"

    def __str__(self) -> str:
        return self.__call__()

    def __call__(self, intensity: t.Union[int, float] = None) -> str:
        if intensity is None:
            return self.value
        else:
            return f"{self.value}!{intensity}"


class FontSize(enum.Enum):
    """
    Refer https://texblog.org/2012/08/29/changing-the-font-size-in-latex/

    todo: currently inline is implemented ... later implement as environment too
    """
    Huge = "\\Huge"
    huge = "\\huge"
    LARGE = "\\LARGE"
    Large = "\\Large"
    large = "\\large"
    normalsize = "\\normalsize"  # (default)
    small = "\\small"
    footnotesize = "\\footnotesize"
    scriptsize = "\\scriptsize"
    tiny = "\\tiny"

    def __str__(self):
        return self.value

    def __call__(self, text: str) -> str:
        return f"{{{self} {text}}}"


class Fa(enum.Enum):
    """
    Options supported by \\usepackage{fontawesome5}
    All fonts: http://mirrors.ibiblio.org/CTAN/fonts/fontawesome5/doc/fontawesome5.pdf
    """
    check = "\\faCheck"
    times = "\\faTimes"
    check_circle = "\\faCheckCircle"
    times_circle = "\\faTimesCircle"

    # not part of fontawesome but still makes sense here
    ldots = "\\ldots"  # for horizontal dots on the line
    cdots = "\\cdots"  # for horizontal dots above the line
    vdots = "\\vdots"  # for vertical dots
    ddots = "\\ddots"  # for diagonal dots

    def __str__(self):
        return self.value

    def __call__(self, color: Color) -> str:
        return f"{{\\color{{{color}}} {self}}}"


class Scalar(t.NamedTuple):
    """
    Also referred as <dimension> in latex docs

    Units:
    pt: a point is approximately 1/72.27 inch, that means about 0.0138 inch or
        0.3515 mm (exactly point is defined as 1/864 of American printer’s foot that
        is 249/250 of English foot)
    mm: a millimeter
    cm:	a centimeter
    in:	inch
    ex:	roughly the height of an 'x' (lowercase) in the current font
        (it depends on the font used)
    em:	roughly the width of an 'M' (uppercase) in the current font
        (it depends on the font used)
    mu:	math unit equal to 1/18 em, where em is taken from the math symbols family
    sp:	so-called "special points", a low-level unit of measure where 65536sp=1pt
    bp: ...
    dd: ...
    pc: ...

    We also support special lengths as units
    baselineskip:   Vertical distance between lines in a paragraph
    columnsep:	    Distance between columns
    columnwidth:	The width of a column
    evensidemargin:	Margin of even pages, commonly used in two-sided documents such as books
    linewidth:	    Width of the line in the current environment.
    oddsidemargin:	Margin of odd pages, commonly used in two-sided documents such as books
    paperwidth:	    Width of the page
    paperheight:	Height of the page
    parindent:	    Paragraph indentation
    parskip:	    Vertical space between paragraphs
    tabcolsep:	    Separation between columns in a table (tabular environment)
    textheight:	    Height of the text area in the page
    textwidth:	    Width of the text area in the page
    topmargin:	    Length of the top margin
    """
    value: t.Union[int, float]
    unit: t.Literal[
        '',
        'pt', 'mm', 'cm', 'in', 'ex', 'em', 'mu', 'sp',
        'bp', 'dd', 'pc',
        # special lengths
        'baselineskip', 'columnsep', 'columnwidth', 'evensidemargin', 'linewidth',
        'oddsidemargin', 'paperwidth', 'paperheight', 'parindent', 'parskip',
        'tabcolsep', 'textheight', 'textwidth', 'topmargin',
    ] = ''

    def __str__(self):
        if self.unit == 'textwidth':
            if self.value in [1, 1.0]:
                return f"\\{self.unit}"
            else:
                return f"{self.value}\\{self.unit}"
        else:
            return f"{self.value}{self.unit}"

    def __mul__(self, other: t.Union[int, float, "Scalar"]) -> "Scalar":
        if isinstance(other, Scalar):
            if other.unit != self.unit:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Units should match ...", dict(self=self.unit, other=other.unit)
                    ]
                )
            other = other.value
        return Scalar(
            value=self.value * other, unit=self.unit
        )

    def __add__(self, other: t.Union[int, float, "Scalar"]) -> "Scalar":
        if isinstance(other, Scalar):
            if other.unit != self.unit:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Units should match ...", dict(self=self.unit, other=other.unit)
                    ]
                )
            other = other.value
        return Scalar(
            value=self.value + other, unit=self.unit
        )

    def __sub__(self, other: t.Union[int, float, "Scalar"]) -> "Scalar":
        if isinstance(other, Scalar):
            if other.unit != self.unit:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Units should match ...", dict(self=self.unit, other=other.unit)
                    ]
                )
            other = other.value
        return Scalar(
            value=self.value - other, unit=self.unit
        )

    def __truediv__(self, other: t.Union[int, float, "Scalar"]) -> "Scalar":
        if isinstance(other, Scalar):
            if other.unit != self.unit:
                raise e.validation.NotAllowed(
                    msgs=[
                        "Units should match ...", dict(self=self.unit, other=other.unit)
                    ]
                )
            other = other.value
        return Scalar(
            value=self.value / other, unit=self.unit
        )


class FloatObjAlignment(enum.Enum):
    """

    todo: support things like \\small

    useful for aligning floating objects like
      - tabular inside table environment
      - tikzpicture inside figure environment ...

    https://www.overleaf.com/learn/latex/Text_alignment
    """
    centering = "\\centering"
    raggedright = "\\raggedright"
    raggedleft = "\\raggedleft"

    def __str__(self) -> str:
        return self.value


@dataclasses.dataclass
class Positioning:
    """
    Positioning for figures and tables

    https://www.overleaf.com/learn/latex/Positioning_of_Figures
    https://www.overleaf.com/learn/latex/Positioning_images_and_tables
    """
    # Will place the here approximately.
    here: bool = False
    # Position at the top of the page.
    top: bool = False
    # Position at the bottom of the page.
    bottom: bool = False
    # Put in a special page, for tables only.
    special_float_page: bool = False
    # Override internal LATEX parameters.
    override: bool = False
    # Place at this precise location, pretty much like h!.
    strict_here: bool = False  # needs \\usepackage{float}

    def __str__(self):
        _ret = ""

        if self.here:
            _ret += "h"
        if self.top:
            _ret += "t"
        if self.bottom:
            _ret += "b"
        if self.special_float_page:
            _ret += "p"
        if self.strict_here:
            _ret += "H"
        # this should be last
        if self.override:
            _ret += "!"

        if _ret == "":
            return _ret
        else:
            return "[" + _ret + "]"


@dataclasses.dataclass
class LaTeX(abc.ABC):
    label: str = None

    @property
    @util.CacheResult
    def _items(self) -> t.List[t.Union["LaTeX", str]]:
        return []

    @property
    def allow_add_items(self) -> bool:
        return True

    @property
    @abc.abstractmethod
    def open_clause(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def close_clause(self) -> str:
        ...

    @property
    def depth(self) -> int:
        if id(self) == id(self._parent):
            return 1
        else:
            return self._parent.depth + 1

    @property
    def use_single_line_repr(self) -> bool:
        return False

    @property
    def doc(self) -> t.Union["Document", "Beamer"]:
        if id(self) == id(self._parent):
            if isinstance(self, (Document, Beamer)):
                return self
            else:
                raise e.code.CodingError(
                    msgs=[f"Dis you set parent with wrong class {self.__class__} ???"]
                )
        else:
            return self._parent.doc

    def __post_init__(self):

        # if self.items is None:
        #     self.items = []

        self.init_validate()
        self.init()

    def __str__(self) -> str:
        # assign _doc to any items first ...
        for _ in self._items:
            if not isinstance(_, str):
                if _.label is not None:
                    e.validation.ShouldNotBeOneOf(
                        value=_.label, values=self.doc.labels,
                        msgs=[
                            f"Please use a unique label ..."
                        ]
                    ).raise_if_failed()
                    self.doc.labels.append(_.label)

        # create str
        _sta = f"% {'>>' * self.depth} {self.__class__.__name__} .. START \n"
        _end = f"% {'<<' * self.depth} {self.__class__.__name__} .. END \n"
        if self.allow_add_items:
            _close_clause = self.close_clause
            if _close_clause != "":
                _close_clause += "\n"
            if self.use_single_line_repr:
                return f"\n" + \
                       _sta + \
                       self.open_clause + \
                       self.generate() + \
                       _close_clause + \
                       _end
            else:
                return f"\n" + \
                       _sta + \
                       self.open_clause + \
                       f"\n% {'--' * self.depth} \n" + \
                       self.generate() + \
                       f"\n% {'--' * self.depth} \n" + \
                       _close_clause + \
                       _end
        else:
            # if not self.use_single_line_repr:
            #     raise e.code.CodingError(
            #         msgs=["was expecting to repr to be single line ... implement if you want this"]
            #     )
            return f"\n" + \
                   _sta + \
                   self.open_clause + \
                   self.generate() + \
                   self.close_clause + "\n" + \
                   _end

    def add_item(self, item: t.Union[str, "LaTeX"]) -> "LaTeX":
        if not self.allow_add_items:
            raise e.code.NotAllowed(
                msgs=[f"You are not allowed to use `add_items` method for class "
                      f"{self.__class__}"]
            )
        if isinstance(item, LaTeX):
            if item._parent is None:
                item._parent = self
            else:
                raise e.code.CodingError(
                    msgs=["We expect _parent of item not to be set ..."]
                )
        self._items.append(item)
        return self

    def init_validate(self):
        ...

    def init(self):
        # noinspection PyTypeChecker,PyAttributeOutsideInit
        self._parent = None  # type: LaTeX

        # if any dataclass field is instance of subclass of LaTeX then assign self._doc
        for f in dataclasses.fields(self):
            _v = getattr(self, f.name)
            if isinstance(_v, LaTeX):
                if _v._parent is None:
                    _v._parent = self
                else:
                    raise e.code.CodingError(
                        msgs=["mst be set by add_item or init method ..."]
                    )

    def generate(self) -> str:
        return "\n".join([str(_) for _ in self._items])


@dataclasses.dataclass
class BeamerTableOfContentsFrame(LaTeX):
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
                   "\\begin{frame}\n"
        else:
            _ret = "\\begin{frame}\n"

        # add other frame settings
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}\n"
        if self.title is not None:
            _ret += f"\\frametitle{{{self.title}}}\n"

        # tableofcontents with options ...
        _toc = "\\tableofcontents["
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
        _toc = _toc + ",".join(_toc_options) + "]\n"
        _ret += _toc

        # add final clause
        if self.current_section or self.current_sub_section:
            _ret += "\\end{frame}}"
        else:
            _ret += "\\end{frame}"

        # return
        return _ret

    @property
    def close_clause(self) -> str:
        return ""


@dataclasses.dataclass
class BeamerFrame(LaTeX):

    title: str = None

    @property
    def open_clause(self) -> str:
        _ret = "\\begin{frame}\n"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}\n"
        if self.title is not None:
            _ret += f"\\frametitle{{{self.title}}}"
        return _ret

    @property
    def close_clause(self) -> str:
        return "\\end{frame}"


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
    # logo: ... # 3. Add a logo in Beamer https://latex-beamer.com/quick-start/

    # https://tex.stackexchange.com/questions/137022/how-to-insert-page-number-in-beamer-navigation-symbols
    # figure out how to have options to modify template
    add_to_beamer_template: str = \
        "\n" \
        "\\addtobeamertemplate{navigation symbols}{}{\n" \
        "\\usebeamerfont{footline}\n" \
        "\\usebeamercolor[fg]{footline}\n" \
        "\\hspace{1em}\n" \
        "\\raisebox{1.5pt}[0pt][0pt]{\\insertframenumber/\\inserttotalframenumber\n}" \
        "}\n" \
        "\\setbeamercolor{footline}{fg=blue}\n" \
        "\\setbeamerfont{footline}{series=\\bfseries}\n" \
        "\\setbeamertemplate{itemize items}[square]\n" \
        "\\setbeamertemplate{enumerate items}[square]\n"

    symbols_file: str = "symbols.tex"
    usepackage_file: str = "usepackage.sty"

    @property
    @util.CacheResult
    def labels(self) -> t.List[str]:
        return []

    @property
    def open_clause(self) -> str:
        _tt = []
        _tt.append(f"\\usetheme{{{self.theme}}}")
        if self.add_to_beamer_template is not None:
            _tt.append(
                self.add_to_beamer_template
            )
        if self.title is not None:
            _title = "\\title"
            if self.short_title is not None:
                _title += f"[{self.short_title}]"
            _title += f"{{{self.title}}}"
            _tt.append(_title)
        if self.sub_title is not None:
            _tt.append(f"\\subtitle{{{self.sub_title}}}")
        if self.author is not None:
            _auth = "\\author"
            if self.short_author is not None:
                _auth += f"[{self.short_author}]"
            _auth += f"{{{self.author}}}"
            _tt.append(_auth)
        if self.institute is not None:
            _inst = "\\institute"
            if self.short_institute is not None:
                _inst += f"[{self.short_institute}]"
            _inst += f"{{{self.institute}}}"
            _tt.append(_inst)
        if self.date is not None:
            _tt.append(f"\\date{{{self.date}}}")
        _ret = _tt + ["\\begin{document}"]
        _ret += [
            "\\begin{frame}\n\\titlepage\n\\end{frame}",
        ]
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
            helper.make_pdf(
                tex_file=_save_to_file,
                pdf_file=_save_to_file.parent /
                         (_save_to_file.name.split(".")[0] + ".pdf"),
            )


@dataclasses.dataclass
class Document(LaTeX):

    title: str = None
    short_title: str = None
    author: str = None
    short_author: str = None
    institute: str = None
    short_institute: str = None
    date: str = None

    main_tex_file: t.Union[None, str] = "../main.tex"
    symbols_file: str = "symbols.tex"
    usepackage_file: str = "usepackage.sty"

    # tikz_externalize_folder: t.Optional[str] = "texipy/_tikz_cache/"
    tikz_externalize_folder: t.Optional[str] = None
    label: None = None

    @property
    @util.CacheResult
    def labels(self) -> t.List[str]:
        return []

    @property
    def open_clause(self) -> str:
        _tt = []
        if self.title is not None:
            _title = "\\title"
            if self.short_title is not None:
                _title += f"[{self.short_title}]"
            _title += f"{{{self.title}}}"
            _tt.append(_title)
        if self.author is not None:
            _auth = "\\author"
            if self.short_author is not None:
                _auth += f"[{self.short_author}]"
            _auth += f"{{{self.author}}}"
            _tt.append(_auth)
        if self.institute is not None:
            _inst = "\\institute"
            if self.short_institute is not None:
                _inst += f"[{self.short_institute}]"
            _inst += f"{{{self.institute}}}"
            _tt.append(_inst)
        if self.date is not None:
            _tt.append(f"\\date{{{self.date}}}")
        _ret = _tt + ["\\begin{document}"]
        if bool(_tt):
            _ret += ["\\maketitle"]
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

        # if main tex file not on disk automatically reset to None
        if self.main_tex_file is not None:
            if not pathlib.Path(self.main_tex_file).exists():
                _LOGGER.warning(
                    msg=f"Main text file {self.main_tex_file} is "
                        f"not on disk so using default setting")
                self.main_tex_file = None

        # handle symbols_file
        if not pathlib.Path(self.symbols_file).exists():
            _LOGGER.warning(
                msg=f"The configured symbols file {self.symbols_file} is "
                    f"not on disk so using creating default file ...")
            pathlib.Path(self.symbols_file).touch()

        # handle usepackage_file
        if not pathlib.Path(self.usepackage_file).exists():
            _LOGGER.warning(
                msg=f"The configured usepackage file {self.usepackage_file} is "
                    f"not on disk so using creating default file ...")
            pathlib.Path(self.usepackage_file).touch()
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
            "\\documentclass{article}"
            if self.main_tex_file is None else
            f"\\documentclass[{self.main_tex_file}]{{subfiles}}",
            ("" if self.main_tex_file is None else "% ") +
            f"\\usepackage{{{self.usepackage_file.split('.')[0]}}}",
            ("" if self.main_tex_file is None else "% ") +
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
            helper.make_pdf(
                tex_file=_save_to_file,
                pdf_file=_save_to_file.parent /
                         (_save_to_file.name.split(".")[0] + ".pdf"),
            )


@dataclasses.dataclass
class ChAndSec(LaTeX, abc.ABC):
    name: str = None

    @property
    def command(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def open_clause(self) -> str:
        _ret = f"\\{self.command}{{{self.name}}}"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}"
        return _ret

    @property
    def close_clause(self) -> str:
        return ""


@dataclasses.dataclass
class Section(ChAndSec):
    ...


@dataclasses.dataclass
class SubSection(ChAndSec):
    ...


@dataclasses.dataclass
class SubSubSection(ChAndSec):
    ...


@dataclasses.dataclass
class Paragraph(ChAndSec):
    ...


@dataclasses.dataclass
class SubParagraph(ChAndSec):
    ...


@dataclasses.dataclass
class Part(ChAndSec):
    """
    Note that \\part and \\chapter are only available in report and
    book document classes.
    """
    ...


@dataclasses.dataclass
class Chapter(ChAndSec):
    """
    Note that \\part and \\chapter are only available in report and
    book document classes.
    """
    ...
