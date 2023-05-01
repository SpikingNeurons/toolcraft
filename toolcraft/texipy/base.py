"""
This module will hold thing like
\\newcommand
\\ossary
"""

import dataclasses
import typing as t
import pathlib
import inspect
import abc
import re
import datetime

from toolcraft import error as e

# noinspection PyUnreachableCode
if False:
    from . import TextType


@dataclasses.dataclass
class Base(abc.ABC):

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
class Acronym(Base):
    """
    Refer: https://www.overleaf.com/learn/latex/Glossaries
    """
    short_name: "TextType"
    full_name: "TextType"

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
            f"\\newcommand*{{\\{self._var_name}}}{{{self.short}}}",
            f"\\newcommand*{{\\{self._var_name + 'F'}}}{{{self.full}}}",
            f"\\newcommand*{{\\{self._var_name + 'L'}}}{{{self.long}}}",
        ]
        return "\n".join(_lines)


@dataclasses.dataclass
class Glossary(Base):
    """
    http://tug.ctan.org/macros/latex/contrib/glossaries/glossariesbegin.pdf
    Refer: https://www.overleaf.com/learn/latex/Glossaries
    """
    # the name key indicates how the term should appear in the list of entries (glossary)
    name: "TextType"
    # description of glossary
    description: "TextType" = None
    # default uses name ... but if you want it to be different in text then change this
    text: "TextType" = None
    # This defaults to the value of the text key with an “s” appended,
    # but if this is incorrect, just use the plural key to override it
    plural: "TextType" = None

    @property
    def normal(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\gls{{ge{self._var_name}}}"

    @property
    def cap(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\Gls{{ge{self._var_name}}}"

    @property
    def pl(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\glspl{{ge{self._var_name}}}"

    @property
    def cappl(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\Glspl{{ge{self._var_name}}}"

    @property
    def desc(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\glsdesc{{ge{self._var_name}}}"

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
            f"\\newglossaryentry{{ge{self._var_name}}}",
            "{",
            f"    name={self.name},",
            f"    description={{{self.description}}}",
        ]
        if self.text is not None:
            _lines += [
                f"    text={{{self.text}}}",
            ]
        if self.plural is not None:
            _lines += [
                f"    plural={self.plural}",
            ]
        _lines += [
            "}",
        ]

        # todo: remove eventually
        if self.description == "":
            raise Exception("do not set description to empty string ")

        if self.description is not None:
            _lines += [f"\\newcommand*{{\\{self._var_name+'Desc'}}}{{{self.desc}}}", ]

        _lines += [
            f"\\newcommand*{{\\{self._var_name}}}{{{self.normal}}}",
            f"\\newcommand*{{\\{self._var_name.capitalize()}}}{{{self.cap}}}",
            f"\\newcommand*{{\\{self._var_name + 's'}}}{{{self.pl}}}",
            f"\\newcommand*{{\\{self._var_name.capitalize() + 's'}}}{{{self.cappl}}}",
        ]
        return "\n".join(_lines)


@dataclasses.dataclass
class Command(Base):
    """
    Refer: https://en.wikibooks.org/wiki/LaTeX/Macros
    \\newcommand{name}[num_args][default]{definition}

    todo: if you want more flexibility
      newcommand only supports one optional argument ... for multiple optional arguments
      use newcommandx ot python in latex
      https://tex.stackexchange.com/questions/29973/more-than-one-optional-argument-for-newcommand
    """
    num_args: int = 0
    default_value: str = None
    latex: "TextType" = None
    # https://tug.org/mail-archives/texhax/2005-March/003732.html
    # starred newcommand
    # setting this to True will not allow newlines and \\par
    long: bool = False

    @property
    def latex_in_math(self) -> str:
        return f"\\({str(self.latex)}\\)"

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

    def latex_def(self, math_mode: bool = False) -> str:
        from . import Text
        _cmd = "\\newcommand"
        if not self.long:
            _cmd += "*"
        _cmd += f"{{{self}}}"
        if self.num_args != 0:
            _cmd += f"[{self.num_args}]"
        if self.default_value is not None:
            _cmd += f"[{self.default_value}]"
        _latex = self.latex_in_math if math_mode else self.latex
        if isinstance(_latex, (Text, str)):
            _cmd += f"{{{str(_latex)}}}"
        else:
            raise e.code.ShouldNeverHappen(msgs=[])
        return _cmd


@dataclasses.dataclass
class Symbol(Command):
    """
    It is just a command with description tag generated like Glossary
    """
    # description of Symbol
    description: "TextType" = None

    @property
    def desc(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\{self._var_name+'Desc'}"

    @property
    def nm(self) -> str:
        if self._var_name is None:
            raise e.code.CodingError(
                msgs=["Should be assigned by now ...",
                      f"Did you forgot to call {make_symbols_tex_file}"]
            )
        # to be used by python code ...
        return f"\\{self._var_name+'NM'}"

    def init_validate(self):
        if self.latex.startswith("\\(") or self.latex.startswith("$"):
            raise e.code.NotAllowed(
                msgs=[f"This is {Symbol} class do not use the latex field in math mode"]
            )
        return super().init_validate()

    # noinspection PyMethodOverriding
    def latex_def(self) -> str:
        _lines = [
            super().latex_def(math_mode=True),
            super().latex_def(math_mode=False).replace("\\" + self._var_name, "\\" + self._var_name + "NM"),
        ]
        if self.description is not None:
            _lines += [f"\\newcommand*{{\\{self._var_name+'Desc'}}}{{{self.description}}}"]
        return "\n".join(_lines)


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
        if _ in [
            "label",
        ]:
            raise e.code.CodingError(
                msgs=[
                    f"Symbol {_!r} cannot be used as it is reserved by latex system"
                ]
            )
        _v = getattr(_mod, _)
        if isinstance(_v, Base):
            # noinspection PyProtectedMember
            if _v._var_name is None:
                if _.find("_") != -1:
                    raise e.code.CodingError(
                        msgs=[
                            f"We do not support _ as latex does not allow that "
                            f"in command names rename the module variable "
                            f"{_} in module {_mod}"
                        ]
                    )
                if bool(re.search(r'\d', _)):
                    raise e.code.CodingError(
                        msgs=[
                            f"We do not support numbers as latex does not "
                            f"allow that in command names rename the module "
                            f"variable {_} in module {_mod}"
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
