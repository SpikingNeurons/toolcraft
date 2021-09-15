"""
Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke

We will gather all tools here in two categories
+ check and fix tools
+ only check tools

Maybe we will make class for these tools and group them together ... or else
make them more general and have own options (e.g. overwrite) and then
generalize them across all tools
"""
import pathlib
import platform
import shutil
import typing as t
import webbrowser
from pathlib import Path

from invoke import task

ROOT_DIR = Path(__file__).parent

TEST_DIR = ROOT_DIR.joinpath("tests")
SOURCE_DIR = ROOT_DIR.joinpath("toolcraft")
THINGS_TO_SCAN = f"tasks.py {SOURCE_DIR.name} {TEST_DIR.name}"

TOX_DIR = ROOT_DIR.joinpath(".tox")
COVERAGE_FILE = ROOT_DIR.joinpath(".coverage")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")
COVERAGE_REPORT = COVERAGE_DIR.joinpath("index.html")

# SPHINX_DIR = ROOT_DIR.joinpath(".sphinx")
# SPHINX_BUILD_DIR = SPHINX_DIR.joinpath(".build")
# SPHINX_INDEX = SPHINX_BUILD_DIR.joinpath("index.html")
# DOCUSAURUS_DIR = ROOT_DIR.joinpath(".website")
# NOTEBOOKS_DIR = ROOT_DIR.joinpath(".notebooks")
SCRIPTS_DIR = ROOT_DIR.joinpath("scripts")

SUPPORTED_PRE_COMMIT_TESTS = ["yapf", "black", "flake8", "autopep8"]


def _find(
    pattern: str,
    path: pathlib.Path,
    recursive: bool,
) -> t.List[pathlib.Path]:
    _ret = []
    if recursive:
        for _ in path.rglob(pattern):
            _ret.append(_)
    else:
        for _ in path.glob(pattern):
            _ret.append(_)
    return _ret


def _delete_file(file):
    try:
        file.unlink(missing_ok=True)
    except TypeError:
        # missing_ok argument added in 3.8
        try:
            file.unlink()
        except FileNotFoundError:
            pass


def _run(c, command):
    return c.run(command, pty=platform.system() != "Windows")


@task(help={"check": "Checks if source is formatted without applying changes"})
def yapf(c, check=False):
    """
    Format code with yapf
    """
    _options = "--recursive"

    if check:
        _options = f"{_options} --diff"
    else:
        _options = f"{_options} --in-place"

    # todo: enable later
    # _run(c, f"yapf {_options} -vv {THINGS_TO_SCAN}")


@task(
    help={
        "check": "Checks if source is in black format without applying changes",
    },
)
def black(c, check=False):
    """

    Format code with black
    """
    _options = ""

    if check:
        _options = "--check --diff --color"

    _run(c, f"black {_options} {THINGS_TO_SCAN}")


@task
def flake8(c):
    """
    Format code with flake8
    """
    ...
    # todo: throws lot of warnings ... will see how other tools can reformat
    #  on their own and at the end we will call this tool which just performs
    #  checks and does not fix it ...
    # _run(c, f"flake8 {THINGS_TO_SCAN}")


@task(help={"check": "Checks if source is formatted without applying changes"})
def autopep8(c, check=False):
    """
    Format code with autopep8
    """

    if check:
        _options = "--diff"
    else:
        _options = "--in-place"

    _run(c, f"autopep8 {_options} {THINGS_TO_SCAN}")


@task(
    help={
        "overwrite": "Check and apply changes",
        "test_type": f"Pre-commit task to perform. Should be one of "
        f"{SUPPORTED_PRE_COMMIT_TESTS}",
    },
)
def pre_commit_tests(c, overwrite=False, test_type=None):
    """
    Call pre-commit tests mostly dealing with formatting
    """
    # -------------------------------------------------- 01
    # validate
    if test_type is None:
        raise Exception(
            f"Please supply test_type with value which is one of "
            f"{SUPPORTED_PRE_COMMIT_TESTS}",
        )
    if test_type not in SUPPORTED_PRE_COMMIT_TESTS:
        raise Exception(
            f"The test_type={test_type} is not one of "
            f"{SUPPORTED_PRE_COMMIT_TESTS}",
        )

    # -------------------------------------------------- 02
    _check = not overwrite

    # -------------------------------------------------- 03
    if test_type == "yapf":
        yapf(c, _check)
    elif test_type == "black":
        black(c, _check)
    elif test_type == "flake8":
        flake8(c)
    elif test_type == "autopep8":
        autopep8(c)
    else:
        raise Exception("Should never happen ...")
