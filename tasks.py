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
import os
import pathlib
import platform
import shutil
import typing as t
import webbrowser

from pathlib import Path

from invoke import task


ROOT_DIR = Path(__file__).parent
TOX_DIR = ROOT_DIR.joinpath(".tox")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")
COVERAGE_REPORT = COVERAGE_DIR.joinpath("index.html")

# SPHINX_DIR = ROOT_DIR.joinpath(".sphinx")
# SPHINX_BUILD_DIR = SPHINX_DIR.joinpath(".build")
# SPHINX_INDEX = SPHINX_BUILD_DIR.joinpath("index.html")
# DOCUSAURUS_DIR = ROOT_DIR.joinpath(".website")
# NOTEBOOKS_DIR = ROOT_DIR.joinpath(".notebooks")
SCRIPTS_DIR = ROOT_DIR.joinpath("scripts")


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


@task
def pytest_cov(c):
    """
    Run pytest's and shows coverage report local dev machine ...
    """
    # todo: parallelize using https://pypi.org/project/pytest-xdist/
    #   already installed as test dependency
    # todo: Explore options for:
    #   pytest-cov
    #   pytest-xdist
    # todo: this works but takes time uncomment later
    _run(c, "pytest -s --cov=toolcraft --cov-append "
         "--cov-report=html tests")
    webbrowser.open(COVERAGE_REPORT.as_uri())


@task
def doc_preview(c):
    """
    Launches docs without building them. Useful for live editing.
    """
    _curr_dir = os.getcwd()
    _doc_dir = _curr_dir + "//website//"
    os.chdir(_doc_dir)
    _run(c, "npm start")


@task()
def bumpversion(c):
    ...
