import typing as t
import pathlib
import subprocess
import errno

from .. import logger
from .. import error as e

_LOGGER = logger.get_logger()


def make_pdf_with_pdflatex(
    tex_file: pathlib.Path,
    pdf_file: pathlib.Path,
    clean: bool = False,
):
    """
    https://tex.stackexchange.com/questions/43325/citations-not-showing-up-in-text-and-bibliography

    To get toc and bibliography working we need below sequence ...
    For your compilation to work properly, you should compile in the following manner:
       pdflatex file.tex && bibtex file.aux && pdflatex file.tex && pdflatex file.tex

    Currently, only doing for pdflatex and for generic things need to rely on
    Refer:
    >>> import pylatex
    >>> pylatex.Document.generate_pdf
    """

    try:
        _check_output_kwargs = {'cwd': pdf_file.parent.as_posix()}

        print(">>>>>>>>>>>>>>>>>>>>>>>> Running pdflatex")
        _output = subprocess.run(
            ["pdflatex", tex_file.as_posix()], stderr=subprocess.STDOUT, **_check_output_kwargs)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", _output)
        print(">>>>>>>>>>>>>>>>>>>>>>>> Running bibtex")
        _output = subprocess.run(
            ["bibtex", tex_file.as_posix().replace("tex", "aux")], stderr=subprocess.STDOUT, **_check_output_kwargs)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", _output)
        print(">>>>>>>>>>>>>>>>>>>>>>>> Running pdflatex")
        _output = subprocess.run(
            ["pdflatex", tex_file.as_posix()], stderr=subprocess.STDOUT, **_check_output_kwargs)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", _output)
        print(">>>>>>>>>>>>>>>>>>>>>>>> Running pdflatex")
        _output = subprocess.run(
            ["pdflatex", tex_file.as_posix()], stderr=subprocess.STDOUT, **_check_output_kwargs)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", _output)

        if clean:
            for _ext in [
                'log', 'out', 'fls', 'fdb_latexmk', 'dvi',
                'auxlock', 'acn', 'glo', 'ist',
                # beamer related ...
                'snm', 'nav',
            ]:
                (
                    pdf_file.parent / pdf_file.name.replace(".pdf", f".{_ext}")
                ).unlink(missing_ok=True)

    except (IOError, OSError) as ex_:
        raise ex_


def make_pdf(
    tex_file: pathlib.Path,
    pdf_file: pathlib.Path,
    compiler: str = None,
    compiler_args: t.List = None,
    silent: bool = True,
    _second_run: bool = False,
):
    """
    Refer:
    >>> import pylatex
    >>> pylatex.Document.generate_pdf

    compiler: `str` or `None`
        The name of the LaTeX compiler to use. If it is None, PyLaTeX will
        choose a fitting one on its own. Starting with ``pdflatex`` and then
        ``latexmk``.
    compiler_args: `list` or `None`
        Extra arguments that should be passed to the LaTeX compiler. If
        this is None it defaults to an empty list.
    silent: bool
        Whether to hide compiler output
    """
    # -------------------------------------------- 01
    # some init
    if compiler_args is None:
        compiler_args = []
    if compiler is not None:
        compilers = ((compiler, []),)
    else:
        compilers = (
            ('pdflatex', []),
            ('latexmk',  ['--pdf']),
        )

    main_arguments = ['--interaction=nonstopmode', tex_file.as_posix()]

    check_output_kwargs = {'cwd': pdf_file.parent.as_posix()}

    for compiler, arguments in compilers:

        command = [compiler] + arguments + compiler_args + main_arguments

        try:
            output = subprocess.check_output(command,
                                             stderr=subprocess.STDOUT,
                                             **check_output_kwargs)
        except (OSError, IOError) as ex_:
            # Use FileNotFoundError when python 2 is dropped
            os_error = ex_

            if os_error.errno == errno.ENOENT:
                # If compiler does not exist, try next in the list
                continue
            raise e.code.NotAllowed(
                msgs=[ex_]
            )
        except subprocess.CalledProcessError as ex_:
            # For all other errors print the output and raise the error
            raise e.code.NotAllowed(
                msgs=[ex_.output.decode()]
            )
        else:
            if not silent:
                _LOGGER.info(msg=output.decode())

        if _second_run:
            ...
            # for _ext in [
            #     'log', 'out', 'fls', 'fdb_latexmk', 'dvi',
            #     'auxlock', 'acn', 'glo', 'ist',
            #     # beamer related ...
            #     'snm', 'nav',
            # ]:
            #     (
            #         pdf_file.parent / pdf_file.name.replace(".pdf", f".{_ext}")
            #     ).unlink(missing_ok=True)
        else:
            # so that toc is handled
            make_pdf(
                tex_file=tex_file, pdf_file=pdf_file, compiler=compiler, compiler_args=compiler_args,
                silent=silent, _second_run=True,
            )

        # Compilation has finished, so no further compilers have to be
        # tried
        break

    else:
        raise e.code.NotAllowed(
            msgs=[
                'We cannot find suitable LaTeX compiler ...',
                'Either specify a LaTex compiler '
                'or make sure you have latexmk or pdfLaTex installed.'
            ]
        )


def make_math(in_: str) -> str:
    return f"\\({in_}\\)"


def make_text(in_: str) -> str:
    return f"\\text{{{in_}}}"
