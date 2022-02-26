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
    """
    value: t.Union[int, float]
    unit: t.Literal['', 'pt', 'mm', 'cm', 'ex', 'em', 'bp', 'dd', 'pc', 'in'] = ''

    def __str__(self):
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


@dataclasses.dataclass
class LaTeX(abc.ABC):
    label: str = None

    @property
    @util.CacheResult
    def items(self) -> t.List[t.Union["LaTeX", str]]:
        return []

    @property
    def use_new_lines(self) -> bool:
        return True

    @property
    @abc.abstractmethod
    def open_clause(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def close_clause(self) -> str:
        ...

    def __post_init__(self):

        # if self.items is None:
        #     self.items = []

        self.init_validate()
        self.init()

    def __str__(self) -> str:
        if self.use_new_lines:
            return self.open_clause + "%\n\n" + \
                   self.generate() + "\n\n" + \
                   self.close_clause + "%"
        else:
            return self.open_clause + self.generate() + self.close_clause + "%"

    def add_item(self, item: t.Union[str, "LaTeX"]) -> "LaTeX":
        if self._doc is not None:
            item._doc = self._doc
        self.items.append(item)
        return self

    def init_validate(self):
        ...

    def init(self):
        # noinspection PyTypeChecker,PyAttributeOutsideInit
        self._doc = None  # type: Document

    def generate(self) -> str:
        _ret = []
        for _ in self.items:
            if not isinstance(_, str):
                if _._doc is None:
                    _._doc = self._doc
                else:
                    if id(_._doc) != id(self._doc):
                        raise e.code.CodingError(
                            msgs=["Different instances of _doc found ... "
                                  "there must be only one"]
                        )
                if _.label is not None:
                    e.validation.ShouldNotBeOneOf(
                        value=_.label, values=self._doc.labels,
                        msgs=[
                            f"Please use a unique label ..."
                        ]
                    ).raise_if_failed()
                    self._doc.labels.append(_.label)
            _ret.append(str(_))
        return "\n".join(_ret)


@dataclasses.dataclass
class Document(LaTeX):

    title: t.Union[str, None] = None
    author: t.Union[str, None] = None
    date: t.Union[str, None] = None

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
            _tt.append(f"\\title{{{self.title}}}%")
        if self.author is not None:
            _tt.append(f"\\author{{{self.author}}}%")
        if self.date is not None:
            _tt.append(f"\\date{{{self.date}}}%")
        if bool(_tt):
            _tt = ["% >> title related"] + _tt + [""]
        _ret = _tt + ["% >> begin document", "\\begin{document}%", ]
        if bool(_tt):
            _ret += ["\\maketitle"]
        return "\n".join(_ret)

    @property
    def close_clause(self) -> str:
        return "% >> end document\n\\end{document}"

    def init_validate(self):
        super().init_validate()
        if self.label is not None:
            raise e.code.CodingError(
                msgs=[f"No need to set label for {self.__class__}"]
            )

    def init(self):
        super().init()
        if self._doc is not None:
            raise e.code.CodingError(
                msgs=[f"No need to set doc for {self.__class__}"]
            )
        # noinspection PyAttributeOutsideInit
        self._doc = self  # as this is Document class

        # if main tex file not on disk automatically reset to None
        if self.main_tex_file is not None:
            if not pathlib.Path(self.main_tex_file).exists():
                _LOGGER.warning(
                    msg=f"Main text file {self.main_tex_file} is "
                        f"not on disk so using default setting")
                self.main_tex_file = None

    def write(
        self,
        save_to_file: str,
        make_pdf: bool = False,
    ):
        # ----------------------------------------------- 01
        # make document
        _all_lines = [
            f"% >> generated on {datetime.datetime.now().ctime()}",
            "",
            "% >> init",
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
        _ret = f"% >> {self.command}: `{self.name}` start " \
               f"\n\\{self.command}{{{self.name}}}"
        if self.label is not None:
            _ret += f"\\label{{{self.label}}}"
        return _ret

    @property
    def close_clause(self) -> str:
        return f"% >> {self.command}: `{self.name}` end ..."


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
