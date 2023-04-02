import dataclasses
import os
import typing as t
import pathlib
import datetime
import abc
import enum

from .. import logger
from .. import util
from .. import error as e

from . import helper
from . import base

_LOGGER = logger.get_logger()
TLaTeX = t.TypeVar('TLaTeX', bound='LaTeX')

TextType = t.Union[str, "Text", "Icon"]

# noinspection PyUnreachableCode
if False:
    from . import beamer
    from . import tikz


class TextFmt(enum.Enum):
    strikeout = "\\sout"  # requires \usepackage[normalem]{ulem}
    italic = "\\itshape"

    def __str__(self) -> str:
        return self.value

    def __call__(self, text: str) -> str:
        return f"{self}{{{text}}}"


class ParaPos(enum.Enum):
    """
    https://www.overleaf.com/learn/latex/Tables

    \\begin{tabular}[pos]{cols}
     table content
    \\end{tabular}

    Also used by
    https://en.wikibooks.org/wiki/LaTeX/Tables
    \\parbox[position]{width}{text}

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
class ParaBox:
    """
    \\parbox[position]{width}{text}

    The newlines n para box can be achieved via \\
    """
    text: t.Union[str, "Text"]
    centering: bool = False
    width: "Scalar" = None
    position: ParaPos = None

    def __str__(self) -> str:
        _ret = "\\parbox"
        if self.position is not None:
            _ret += f"[{self.position}]"
        if self.width is not None:
            _ret += f"{{{self.width}}}"
        _text = str(self.text)
        if self.centering:
            _text = "\\centering " + _text
        _ret += f"{{{_text}}}"
        return _ret


class Text:
    """
    Refer here for fonts and sizes
    + https://www.overleaf.com/learn/latex/Font_sizes%2C_families%2C_and_styles
    """

    def __init__(self, text: t.Union[str, base.Base, "Icon"], no_text_cmd: bool = False):
        self.no_text_cmd = no_text_cmd
        self.text = text

    def __str__(self) -> str:
        if self.no_text_cmd:
            return str(self.text)
        else:
            return f"\\text{{{self.text}}}"

    def strikeout(self) -> "Text":
        self.text = f"\\sout{{{self.text}}}"
        return self

    def bold(self) -> "Text":
        self.text = f"\\textbf{{{self.text}}}"
        return self

    def italic(self) -> "Text":
        self.text = f"\\textit{{{self.text}}}"
        return self

    def emphasis(self) -> "Text":
        self.text = f"\\emph{{{self.text}}}"
        return self

    def color(self, color: t.Union["Color", str]) -> "Text":
        self.text = f"\\textcolor{{{color}}}{{{self.text}}}"
        return self

    def size(self, size: "FontSize") -> "Text":
        self.text = size(self.text)
        return self

    def in_math(self) -> "Text":
        self.text = "\\(" + str(self.text) + "\\)"
        return self


class Icon(enum.Enum):
    """
    Check zotero or online pdf at https://ctan.org/pkg/fontawesome5
    Click "Package Documentation"

    Options supported by \\usepackage{fontawesome5}
    All fonts: http://mirrors.ibiblio.org/CTAN/fonts/fontawesome5/doc/fontawesome5.pdf

    Section 5: Dingbats: Useful for making bullets in itemized list
    https://math.uoregon.edu/wp-content/uploads/2014/12/compsymb-1qyb3zd.pdf
    """

    fa_hammer = enum.auto()
    fa_check = enum.auto()
    fa_times = enum.auto()
    fa_check_circle = enum.auto()
    fa_times_circle = enum.auto()
    fa_thumbs_down = enum.auto()
    fa_thumbs_up = enum.auto()
    fa_meh = enum.auto()
    fa_pen = enum.auto()
    fa_seedling = enum.auto()
    fa_arrow_alt_circle_down = enum.auto()

    dots = enum.auto()
    ldots = enum.auto()
    cdots = enum.auto()
    vdots = enum.auto()
    ddots = enum.auto()

    # https://mirror.informatik.hs-fulda.de/tex-archive/macros/latex/required/psnfss/psnfss2e.pdf
    ding_cmark = enum.auto()
    ding_xmark = enum.auto()
    ding_cmarkb = enum.auto()
    ding_xmarkb = enum.auto()

    @property
    def latex_cmd(self) -> str:
        _cmd = self.name
        if _cmd.startswith("fa_"):
            _new_cmd = "fa"
            for _ in _cmd.split("_")[1:]:
                _new_cmd += _.capitalize()
            _cmd = _new_cmd
        elif _cmd.startswith("ding_"):
            if _cmd == "ding_cmark":
                _cmd = "ding{51}"
            elif _cmd == "ding_cmarkb":
                _cmd = "ding{52}"
            elif _cmd == "ding_xmark":
                _cmd = "ding{55}"
            elif _cmd == "ding_xmarkb":
                _cmd = "ding{56}"
            else:
                raise e.code.CodingError(msgs=[f"Unknown {_cmd}"])
        else:
            ...
        return "\\" + _cmd

    def as_text(self, no_text_cmd: bool = True) -> Text:
        return Text(self.latex_cmd, no_text_cmd=no_text_cmd)

    def __str__(self) -> str:
        return self.latex_cmd


class Font(enum.Enum):
    """
    todo: figure out other options later
    """
    italic = "\\itshape"

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

    @property
    def is_special_length(self) -> bool:
        return self.unit in [
            'baselineskip', 'columnsep', 'columnwidth', 'evensidemargin', 'linewidth',
            'oddsidemargin', 'paperwidth', 'paperheight', 'parindent', 'parskip',
            'tabcolsep', 'textheight', 'textwidth', 'topmargin',
        ]

    def __str__(self):
        if self.is_special_length:
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
    no_comments: bool = False

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
    def doc(self) -> t.Union["Document", "beamer.Beamer"]:
        from . import beamer
        if id(self) == id(self._parent):
            if isinstance(self, (Document, beamer.Beamer)):
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
            if not isinstance(_, (str, Text, ParaBox, Icon, base.Base)):
                if _.label is not None:
                    e.validation.ShouldNotBeOneOf(
                        value=_.label, values=self.doc.labels,
                        msgs=[
                            f"Please use a unique label ..."
                        ]
                    ).raise_if_failed()
                    self.doc.labels.append(_.label)

        # create str
        if self.no_comments:
            _sta, _end = "", ""
        else:
            _sta = f"% {'>>' * self.depth} {self.__class__.__name__} .. START \n"
            if self.close_clause == "":
                _end = f"% {'<<' * self.depth} {self.__class__.__name__} .. END"
            else:
                _end = f"\n% {'<<' * self.depth} {self.__class__.__name__} .. END"
        if self.allow_add_items:
            if self.use_single_line_repr:
                return _sta + \
                       self.open_clause + \
                       self.generate() + \
                       self.close_clause + \
                       _end
            else:
                _gen = self.generate()
                if _gen != "":
                    _gen += "\n"
                return _sta + self.open_clause + \
                       f"\n% {'--' * self.depth} \n" + \
                       _gen + \
                       f"% {'--' * self.depth} \n" + \
                       self.close_clause + \
                       _end
        else:
            # if not self.use_single_line_repr:
            #     raise e.code.CodingError(
            #         msgs=["was expecting to repr to be single line ... implement if you want this"]
            #     )
            return _sta + \
                   self.open_clause + \
                   self.generate() + \
                   self.close_clause + \
                   _end

    def add_item(self, item: t.Union[str, "LaTeX", Text]) -> TLaTeX:
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

        # handle usepackage_file ... we always overwrite with our default file
        pathlib.Path(self.usepackage_file).unlink()
        pathlib.Path(self.usepackage_file).write_text(
            (pathlib.Path(__file__).parent / "usepackage.sty").read_text()
        )

    def add_item(self, item: t.Union[str, "LaTeX", Text]) -> "Document":
        return super().add_item(item)

    def write(
        self,
        save_to_file: str,
        make_pdf: bool = False,
        clean: bool = False,
    ):
        # ----------------------------------------------- 01
        # save to file
        _save_to_file = pathlib.Path(save_to_file)
        # dot dot token
        _num_save_to_file_parents = len(save_to_file.split("/")) - 1
        _dot_dot_token = "//".join([".."]*_num_save_to_file_parents) + "//"
        # make document
        _all_lines = [
            # f"% Generated on {datetime.datetime.now().ctime()}",
            "",
            "\\documentclass{article}"
            if self.main_tex_file is None else
            f"\\documentclass[{self.main_tex_file}]{{subfiles}}",
            ("" if self.main_tex_file is None else "% ") +
            f"\\usepackage{{{_dot_dot_token + self.usepackage_file.split('.')[0]}}}",
            ("" if self.main_tex_file is None else "% ") +
            f"\\input{{{_dot_dot_token + self.symbols_file.split('.')[0]}}}",
            "",
            str(self),
            "",
        ]

        # ----------------------------------------------- 02
        _save_to_file.parent.mkdir(exist_ok=True)
        _save_to_file.write_text("\n".join(_all_lines))

        # ----------------------------------------------- 03
        # make pdf if requested
        if make_pdf:
            helper.make_pdf_with_pdflatex(
                tex_file=_save_to_file,
                pdf_file=_save_to_file.parent /
                         (_save_to_file.name.split(".")[0] + ".pdf"),
                clean=clean,
            )


@dataclasses.dataclass
class IncludeGraphics(LaTeX):
    """
    todo: Lot more options to be supported from here
        https://latexref.xyz/_005cincludegraphics.html
    """

    width: Scalar = None
    angle: t.Union[int, float] = None
    # todo: add check for image present on disk
    image_path: str = None

    @property
    def use_single_line_repr(self) -> bool:
        return True

    @property
    def open_clause(self) -> str:
        _ops = []
        if self.width is not None:
            _ops += [f"width={self.width}"]
        if self.angle is not None:
            _ops += [f"angle={self.angle}"]
        return f"\\includegraphics[{','.join(_ops)}]"

    @property
    def close_clause(self) -> str:
        return f"{{{self.image_path}}}"

    def init_validate(self):
        super().init_validate()
        if self.image_path is None:
            raise e.validation.NotAllowed(
                msgs=["Field image_path is mandatory"]
            )


@dataclasses.dataclass
class Figure(LaTeX):
    positioning: Positioning = None
    alignment: FloatObjAlignment = None
    caption: str = None

    # To scale graphics ...
    # https://tex.stackexchange.com/questions/13460/scalebox-knowing-how-much-it-scales
    # https://tex.stackexchange.com/questions/4338/correctly-scaling-a-tikzpicture
    # Other options adjustbox, resizebox
    scale: t.Tuple[float, float] = None

    @property
    def open_clause(self) -> str:
        _ret = [
            f"\\begin{{figure}}{'' if self.positioning is None else self.positioning}",
        ]
        if self.alignment is not None:
            _ret.append(f"{self.alignment}")
        # add scalebox
        if self.scale is not None:
            _ret.append(f"\\scalebox{{{self.scale[0]}}}[{self.scale[1]}]\n{{")
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = []
        if self.scale is not None:
            _ret.append("}")
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}")
        _ret += [
            f"\\end{{figure}}"
        ]
        return "\n".join(_ret)

    def add_item(self, item: t.Union["tikz.TikZ", "SubFigure", IncludeGraphics]) -> "Figure":
        from . import tikz

        # test item
        e.validation.ShouldBeInstanceOf(
            value=item, value_types=(tikz.TikZ, SubFigure, IncludeGraphics),
            msgs=[f"Only certain item types are allowed in {Figure}"],
        ).raise_if_failed()

        # call super to add item
        return super().add_item(item=item)


@dataclasses.dataclass
class SubFigure(LaTeX):
    positioning: Positioning = None
    alignment: FloatObjAlignment = None
    caption: str = None
    width: float = None

    @property
    def open_clause(self) -> str:
        _ret = [
            f"\\begin{{subfigure}}{'' if self.positioning is None else self.positioning}{{{self.width}\\textwidth}}",
        ]
        if self.alignment is not None:
            _ret.append(f"{self.alignment}")
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        _ret = []
        if self.caption is not None:
            _ret.append(f"\\caption{{{self.caption}}}")
        if self.label is not None:
            _ret.append(f"\\label{{{self.label}}}")
        _ret += [
            f"\\end{{subfigure}}"
        ]
        return "\n".join(_ret)

    def init_validate(self):
        # call super
        super().init_validate()

        # check
        if self.width is None:
            raise e.validation.NotAllowed(msgs=["Please supply value for width field"])

    def add_item(self, item: t.Union["tikz.TikZ", "SubFigure", IncludeGraphics]) -> "SubFigure":
        from . import tikz

        # test item
        e.validation.ShouldBeInstanceOf(
            value=item, value_types=(tikz.TikZ, SubFigure, IncludeGraphics),
            msgs=[f"Only certain item types are allowed in {SubFigure}"],
        ).raise_if_failed()

        # call super to add item
        return super().add_item(item=item)




@dataclasses.dataclass
class List(LaTeX):
    """
    https://latex-tutorial.com/tutorials/lists/

    todo: Add bullet styles support https://latex-tutorial.com/bullet-styles/
          Currently using str's
    """
    type: t.Literal['itemize', 'enumerate', 'description'] = 'itemize'
    items: t.Union[
        t.List[t.Union[TextType, "List"]],
        t.List[t.Tuple[TextType, TextType]]
    ] = None

    @property
    def allow_add_items(self) -> bool:
        return False

    @property
    def open_clause(self) -> str:
        _ret = f"\\begin{{{self.type}}}\n"
        return _ret

    def generate(self) -> str:
        _ret = ""
        for _item in self.items:
            if isinstance(_item, str):
                _ret += f"\\item {_item}\n"
            elif isinstance(_item, List):
                if _item._parent is not None:
                    raise e.code.CodingError(
                        msgs=["Was expecting lis to not have parent"]
                    )
                _item._parent = self
                _ret += str(_item)
            elif isinstance(_item, tuple):
                # refer for styles https://latex-tutorial.com/bullet-styles/
                _bullet_style, _value = _item
                _ret += f"\\item[{_bullet_style}] {_value}\n"
            else:
                raise e.code.ShouldNeverHappen(msgs=[])
        return _ret

    @property
    def close_clause(self) -> str:
        return f"\\end{{{self.type}}}"

    def init_validate(self):
        if self.items is None:
            raise e.validation.NotAllowed(
                msgs=["Please supply mandatory field items"]
            )


@dataclasses.dataclass
class _ChAndSec(LaTeX, abc.ABC):
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
class Section(_ChAndSec):
    ...


@dataclasses.dataclass
class SubSection(_ChAndSec):
    ...


@dataclasses.dataclass
class SubSubSection(_ChAndSec):
    ...


@dataclasses.dataclass
class Paragraph(_ChAndSec):
    ...


@dataclasses.dataclass
class SubParagraph(_ChAndSec):
    ...


@dataclasses.dataclass
class Part(_ChAndSec):
    """
    Note that \\part and \\chapter are only available in report and
    book document classes.
    """
    ...


@dataclasses.dataclass
class Chapter(_ChAndSec):
    """
    Note that \\part and \\chapter are only available in report and
    book document classes.
    """
    ...
