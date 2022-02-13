import dataclasses
import typing as t
import pathlib
import datetime
import abc
import enum

from . import helper
from .. import logger
from .. import error as e

_LOGGER = logger.get_logger()


class Thickness(enum.Enum):
    """
    Refer:
    https://www.overleaf.com/learn/latex/TikZ_package
    """
    ultra_thin = "ultra thin"
    very_thin = "very thin"
    thin = "thin"
    thick = "thick"
    very_thick = "very thick"
    ultra_thick = "ultra thick"


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

    def for_draw(
        self, intensity: t.Union[int, float] = None,
        opacity: t.Union[int, float] = None
    ) -> str:
        _ret = f"draw={self(intensity=intensity)}"
        if opacity is not None:
            _ret += f",draw opacity={opacity}"
        return _ret

    def for_fill(
        self, intensity: t.Union[int, float] = None,
        opacity: t.Union[int, float] = None
    ) -> str:
        _ret = f"fill={self(intensity=intensity)}"
        if opacity is not None:
            _ret += f",fill opacity={opacity}"
        return _ret


class Scalar(t.NamedTuple):
    """
    Also referred as <dimension> in latex docs
    """
    value: t.Union[int, float]
    unit: t.Literal['', 'pt', 'mm', 'cm', 'ex', 'em', 'bp', 'dd', 'pc', 'in'] = '',

    def __str__(self):
        return f"{self.value}{self.unit}"


@dataclasses.dataclass
class LaTeX(abc.ABC):
    items: t.List[t.Union[str, "LaTeX"]]

    @property
    def preambles(self) -> t.List[str]:
        _ret = []
        for _ in self.items:
            if not isinstance(_, str):
                for _p in _.preambles:
                    if _p not in _ret:
                        _ret.append(_p)
        return _ret

    @property
    def preamble_configs(self) -> t.List[str]:
        _ret = []
        for _ in self.items:
            if not isinstance(_, str):
                for _c in _.preamble_configs:
                    if _c not in _ret:
                        _ret.append(_c)
        return _ret

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

    def __str__(self) -> str:
        if self.use_new_lines:
            return self.open_clause + "%\n\n" + \
                   self.generate() + "\n\n" + \
                   self.close_clause + "%"
        else:
            return self.open_clause + self.generate() + self.close_clause + "%"

    def init_validate(self):
        ...

    def generate(self) -> str:
        _ret = []
        for _ in self.items:
            _ret.append(str(_))
            if isinstance(_, str):
                _ret.append("")
        return "\n".join(_ret)


@dataclasses.dataclass
class Document(LaTeX):

    title: t.Union[str, None] = None
    author: t.Union[str, None] = None
    date: t.Union[str, None] = None

    main_tex_file: t.Union[None, str] = None

    @property
    def preambles(self) -> t.List[str]:
        _preamble_document_class = "\\documentclass"
        _preamble_document_class += "{article}" if self.main_tex_file is None else \
            f"[{self.main_tex_file}]{{subfiles}}"
        _ret = [_preamble_document_class] + super().preambles
        return _ret

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
        if self.main_tex_file is not None:
            if not pathlib.Path(self.main_tex_file).exists():
                _LOGGER.warning(msg=f"Main text file {self.main_tex_file} is "
                                 f"not on disk so using default setting")
                self.main_tex_file = None

    def write(
        self,
        save_to_file: str,
        make_pdf: bool = False,
    ):
        # ----------------------------------------------- 01
        # make document class preamble
        # ----------------------------------------------- 02
        # make preamble
        _preambles = [f"{_p}%" for _p in self.preambles]
        # ----------------------------------------------- 03
        # make commands
        _preamble_configs = [f"{_pc}%" for _pc in self.preamble_configs]
        # ----------------------------------------------- 04
        # write
        _all_lines = [
            f"% >> generated on {datetime.datetime.now().ctime()}", "",
            "% >> preambles", *_preambles, "",
            "% >> preamble configs", *_preamble_configs, "",
            str(self), "",
        ]
        _save_to_file = pathlib.Path(save_to_file)
        _save_to_file.write_text("\n".join(_all_lines))
        # ----------------------------------------------- 05
        # make pdf if requested
        if make_pdf:
            helper.make_pdf(
                tex_file=_save_to_file,
                pdf_file=_save_to_file.parent /
                         (_save_to_file.name.split(".")[0] + ".pdf")
            )


@dataclasses.dataclass
class Section(LaTeX):

    name: str = "section name"

    @property
    def label(self) -> str:
        return "sec:" + self.name.replace(" ", "_").lower()

    @property
    def open_clause(self) -> str:
        return f"% >> section `{self.name}` start " \
               f"\n\\section{{{self.name}}}\\label{{{self.label}}}"

    @property
    def close_clause(self) -> str:
        return f"% >> section `{self.name}` end ..."
