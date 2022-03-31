"""
This module will hold thing like
\\newcommand
\\glossary
"""

import dataclasses
import typing as t
import pathlib
import inspect
import abc
import datetime

from toolcraft import error as e


@dataclasses.dataclass
class Symbol(abc.ABC):

    def __post_init__(self):
        self._var_name = None
        self.init_validate()
        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...

    def __str__(self):
        raise e.code.CodingError(
            msgs=[f"Please implement this in child class {self.__class__}"]
        )

    @abc.abstractmethod
    def latex_def(self) -> str:
        ...


@dataclasses.dataclass
class Acronym(Symbol):
    """
    Refer: https://www.overleaf.com/learn/latex/Glossaries
    """
    short_name: str
    full_name: str

    @property
    def short(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\acrshort{{{self._var_name}}}"

    @property
    def long(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\acrlong{{{self._var_name}}}"

    @property
    def full(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\acrfull{{{self._var_name}}}"

    def __str__(self):
        # to be used by python code ...
        return self.short

    def latex_def(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        _lines = [
            f"\\newacronym"
            f"{{{self._var_name}}}{{{self.short_name}}}{{{self.full_name}}}",
            f"\\newcommand*{{\\{self._var_name}}}{{{self.short}~}}",
            f"\\newcommand*{{\\{self._var_name + 'F'}}}{{{self.full}~}}",
            f"\\newcommand*{{\\{self._var_name + 'L'}}}{{{self.long}~}}",
        ]
        return "\n".join(_lines)


@dataclasses.dataclass
class Glossary(Symbol):
    """
    Refer: https://www.overleaf.com/learn/latex/Glossaries
    """
    name: str
    description: str
    make_cap: bool = False
    make_pl: bool = False
    make_cappl: bool = False

    @property
    def normal(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\gls{{{self._var_name}}}"

    @property
    def cap(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\Gls{{{self._var_name}}}"

    @property
    def pl(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\glspl{{{self._var_name}}}"

    @property
    def cappl(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\Glspl{{{self._var_name}}}"

    @property
    def desc(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\glsdesc{{{self._var_name}}}"

    def __str__(self):
        # to be used by python code ...
        return self.normal

    def latex_def(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        _lines = [
            f"\\newglossaryentry{{{self._var_name}}}",
            "{",
            f"    name={self.name},",
            f"    description={{{self.description}}}",
            "}",
            f"\\newcommand*{{\\{self._var_name}}}{{{self.normal}~}}",
            f"\\newcommand*{{\\{self._var_name+'Desc'}}}{{{self.desc}~}}",
        ]
        if self.make_cap:
            _lines += \
                [f"\\newcommand*{{\\{self._var_name.capitalize()}}}{{{self.cap}~}}"]
        if self.make_pl:
            _lines += \
                [f"\\newcommand*{{\\{self._var_name + 'Pl'}}}{{{self.pl}~}}"]
        if self.make_cappl:
            _lines += \
                [f"\\newcommand*"
                 f"{{\\{self._var_name.capitalize() + 'Pl'}}}{{{self.cappl}~}}"]
        return "\n".join(_lines)


@dataclasses.dataclass
class Command(Symbol):
    """
    Refer: https://en.wikibooks.org/wiki/LaTeX/Macros
    \\newcommand{name}[num_args][default]{definition}

    todo: if you want more flexibility
      newcommand only supports one optional argument ... for multiple optional arguments
      use newcommandx ot python in latex
      https://tex.stackexchange.com/questions/29973/more-than-one-optional-argument-for-newcommand
    """
    long: bool = False
    num_args: int = 0
    default_value: str = None
    latex: str = None

    def __post_init__(self):
        super().__post_init__()

        if self.latex is None:
            raise e.validation.NotAllowed(
                msgs=["Please assign mandatory field `latex`"]
            )

        if self.default_value is not None:
            if self.num_args == 0:
                raise e.validation.NotAllowed(
                    msgs=["Please update num_args as you are using default values"]
                )

    def __str__(self):
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\{self._var_name}"

    def __call__(self, *args) -> str:
        # some validation for usage of call
        if self.num_args == 0:
            raise e.validation.NotAllowed(
                msgs=[f"Command {self} does not support args"]
            )
        if self.default_value is None:
            if len(args) != self.num_args:
                raise e.validation.NotAllowed(
                    msgs=[f"Command {self} expect {self.num_args} args"]
                )
        else:
            if len(args) not in [self.num_args, self.num_args-1]:
                raise e.validation.NotAllowed(
                    msgs=[f"Command {self} expect {self.num_args} "
                          f"or {self.num_args-1} args"]
                )

        # make str to be used with python
        _ret = str(self)
        if self.default_value is not None:
            if len(args) == self.num_args:
                _ret += f"[{args[0]}]"
                for arg in args[1:]:
                    _ret += f"{{{arg}}}"
            else:
                for arg in args:
                    _ret += f"{{{arg}}}"
        else:
            for arg in args:
                _ret += f"{{{arg}}}"

        # return
        return _ret

    def latex_def(self) -> str:
        _cmd = "\\newcommand"
        if not self.long:
            _cmd += "*"
        _cmd += f"{{{self}}}"
        if self.num_args != 0:
            _cmd += f"[{self.num_args}]"
        if self.default_value is not None:
            _cmd += f"[{self.default_value}]"
        _cmd += f"{{{self.latex}~}}"
        return _cmd


def make_symbols_tex_file():
    _frame = inspect.stack()[1]
    _mod = inspect.getmodule(_frame[0])
    _tex_file = pathlib.Path(_frame.filename)
    _tex_file = _tex_file.parent / _tex_file.name.replace(".py", ".tex")

    _tex_lines = [
        # f"% >> generated on {datetime.datetime.now().ctime()}",
        "% Remember to add this before \\begin{document}..",
        "% \\usepackage[acronym]{glossaries}%",
        "% \\makeglossaries%",
        "% Remember to add this before \\end{document}..",
        "% \\clearpage",
        "% \\printglossary[type=\\acronymtype]",
        "% \\printglossary",
        "",
    ]
    for _ in dir(_mod):
        _v = getattr(_mod, _)
        if isinstance(_v, Symbol):
            # noinspection PyProtectedMember
            if _v._var_name is None:
                if _.find("_") != -1:
                    raise e.code.CodingError(
                        msgs=[
                            f"We do not support _ as latex does not allow that i"
                            f"n command names rename the module variable "
                            f"{_} in module {_mod}"
                        ]
                    )
                _v._var_name = _
                if _.lower() != _:
                    raise e.code.CodingError(
                        msgs=[
                            f"Please do not use capital letters",
                            f"Rename {_} to {_.lower()}"
                        ]
                    )
            _tex_lines.append(
                _v.latex_def()
            )
            _tex_lines.append("")

    _tex_file.write_text(
        "\n".join(_tex_lines)
    )
