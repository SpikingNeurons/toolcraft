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
import toml
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
    _run(c, "pytest -s --cov=toolcraft --cov-append " "--cov-report=html tests")
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


@task(
    help={
        'show_version': 'Display current version',
        'alpha': 'Make alpha release',
        'beta': 'Make beta release',
        'patch': 'Make patch release',
        'minor': 'Make minor release',
        'major': 'Make major release',
        'dry_run': "Only test and do not modify files",
        'bump_into': "When bumping from stable release specify release type "
                     "which is one of 'alpha', 'beta' or 'stable'. "
                     "Only useful along with --major, --minor and --patch "
                     "option and when current version is stable",
    }
)
def bump(
    c, show_version=False,
    alpha=False, beta=False, patch=False, minor=False, major=False,
    dry_run=False, bump_into='alpha',
):
    """
    Handle bumping versions for toolcraft library.
    Version style
      >> {major}.{minor}.{patch}{release_type}{release_num}
        release_type is one of ['a', 'b']
      >> {major}.{minor}.{patch}
    """
    # ------------------------------------------------- 01
    # Format is:
    #   >> {major}.{minor}.{patch}{release}{num}\
    #
    # Easy way to test `bump2version`
    #   bump2version --no-configured-files --dry-run --verbose
    #     --current-version 0.1.2 --new-version 0.1.2a2 xyz

    # ------------------------------------------------- 02
    # detect current version
    _curr_ver = \
        toml.load("pyproject.toml")['tool']['poetry']['version'].split(".")
    _major, _minor, _patch = \
        int(_curr_ver[0]), int(_curr_ver[1]), _curr_ver[2]
    _release_type = None
    _release_num = None
    if _patch.find("a") > -1:
        _release_type = "a"
        _release_num = int(_patch.split("a")[1])
        _patch = int(_patch.split("a")[0])
    elif _patch.find("b") > -1:
        _release_type = "b"
        _release_num = int(_patch.split("b")[1])
        _patch = int(_patch.split("b")[0])
    else:
        _patch = int(_patch)

    # ------------------------------------------------- 03
    # show version
    if show_version:
        print(
            "Current version is",
            {
                "major": _major,
                "minor": _minor,
                "patch": _patch,
                "release_type": _release_type,
                "release_num": _release_num,
            }
        )
        return

    # ------------------------------------------------- 04
    # figure out new version
    # ------------------------------------------------- 04.01
    # if alpha release
    if alpha:
        if _release_type is None:
            _patch += 1
            _release_type = "a"
            _release_num = 0
        elif _release_type == "a":
            _release_num += 1
        elif _release_type == "b":
            raise Exception(
                "Current release is in beta so alpha release is not possible"
            )
        else:
            raise Exception("Should not happen ...")
    # ------------------------------------------------- 04.02
    # if beta release
    elif beta:
        if _release_type is None:
            _patch += 1
            _release_type = "b"
            _release_num = 0
        elif _release_type == "a":
            _release_type = "b"
            _release_num = 0
        elif _release_type == "b":
            _release_num += 1
        else:
            raise Exception("Should not happen ...")
    # ------------------------------------------------- 04.03
    # if patch release
    elif patch:
        if _release_type is None:
            _patch += 1
            if bump_into == "alpha":
                _release_type = "a"
                _release_num = 0
            elif bump_into == "beta":
                _release_type = "b"
                _release_num = 0
            elif bump_into == "stable":
                ...
            else:
                raise Exception(
                    "Arg --bump-into can be one of "
                    "['alpha', 'beta', 'stable']. "
                    f"Found {bump_into}"
                )
        elif _release_type in ["a", "b"]:
            _release_type = None
            _release_num = None
        else:
            raise Exception("Should not happen ...")
    # ------------------------------------------------- 04.04
    # if minor release
    elif minor:
        if _release_type is None:
            _minor += 1
            _patch = 0
            if bump_into == "alpha":
                _release_type = "a"
                _release_num = 0
            elif bump_into == "beta":
                _release_type = "b"
                _release_num = 0
            elif bump_into == "stable":
                ...
            else:
                raise Exception(
                    "Arg --bump-into can be one of "
                    "['alpha', 'beta', 'stable']. "
                    f"Found {bump_into}"
                )
        elif _release_type in ["a", "b"]:
            raise Exception(
                f"The current version {_curr_ver} is in alpha or beta. "
                f"So please patch current version for stable release "
                f"before considering next minor release ..."
            )
        else:
            raise Exception("Should not happen ...")
    # ------------------------------------------------- 04.05
    # if major release
    elif major:
        if _release_type is None:
            _major += 1
            _minor = 0
            _patch = 0
            if bump_into == "alpha":
                _release_type = "a"
                _release_num = 0
            elif bump_into == "beta":
                _release_type = "b"
                _release_num = 0
            elif bump_into == "stable":
                ...
            else:
                raise Exception(
                    "Arg --bump-into can be one of "
                    "['alpha', 'beta', 'stable']. "
                    f"Found {bump_into}"
                )
        elif _release_type in ["a", "b"]:
            raise Exception(
                f"The current version {_curr_ver} is in alpha or beta. "
                f"So please patch current version for stable release "
                f"before considering next major release ..."
            )
        else:
            raise Exception("Should not happen ...")
    # ------------------------------------------------- 04.06
    else:
        raise Exception(
            "You did not supply any options ..."
        )

    # ------------------------------------------------- 05
    if _release_type is None:
        _release_type = ''
    if _release_num is None:
        _release_num = ''
    _new_ver = f"{_major}.{_minor}.{_patch}{_release_type}{_release_num}"
    _bump_command = f"bump2version --verbose --new-version " \
                    f"{'--dry-run' if dry_run else ''} " \
                    f"{_new_ver} xyz"
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("Bump command", _bump_command)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    _run(c, _bump_command)



