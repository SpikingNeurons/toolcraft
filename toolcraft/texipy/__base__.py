import dataclasses
import typing as t
import pathlib
import datetime
import abc

from . import helper
from .. import logger

_LOGGER = logger.get_logger()


@dataclasses.dataclass
class LaTeXOptions:
    ...


@dataclasses.dataclass
class LaTeX(abc.ABC):
    items: t.List[t.Union[str, "LaTeX"]]
    options: t.Optional[LaTeXOptions] = None

    @property
    def preambles(self) -> t.List[str]:
        return []

    @property
    def commands(self) -> t.List[str]:
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
        _ret = [_preamble_document_class]
        for _ in self.items:
            if not isinstance(_, str):
                for _p in _.preambles:
                    if _p not in _ret:
                        _ret.append(_p)
        return _ret

    @property
    def commands(self) -> t.List[str]:
        _ret = []
        for _ in self.items:
            if not isinstance(_, str):
                for _c in _.commands:
                    if _c not in _ret:
                        _ret.append(_c)
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
        _commands = [f"{_pc}%" for _pc in self.commands]
        # ----------------------------------------------- 04
        # write
        _all_lines = [
            f"% >> generated on {datetime.datetime.now().ctime()}", "",
            "% >> preambles", *_preambles, "",
            "% >> commands", *_commands, "",
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

    name: str

    @property
    def open_clause(self) -> str:
        return f"\\section{self.name}"

    @property
    def close_clause(self) -> str:
        pass