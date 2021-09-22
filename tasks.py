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
import os
import git
import github
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

_GIT = git.Git()
_GIT_LOCAL_REPO = git.Repo()
# todo: make this more secure. Is this recommended??
#    This keeps env variable exposed
_GITHUB = github.Github(
    login_or_token=os.environ.get('PK_PYGITHUB_TOKEN_PK', None)
)
# we will not do authentication as this is public repo
# _GITHUB = github.Github()
_GH_REMOTE_REPO = _GITHUB.get_repo('SpikingNeurons/toolcraft')


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
        'tag': 'The tag that you want to delete. '
               'Default is to use tag based on current version of repo.'
    }
)
def del_tag(c, tag=None):
    """
    Delete the specified tag locally as well as remotely.
    """
    # resolve tag
    if tag is None:
        tag = \
            toml.load("pyproject.toml")['tool']['poetry']['version']
        tag = 'v' + tag

    # get repo instance
    _repo = git.Repo()

    # delete tag locally
    # _run(c, f"git tag -d {tag}")
    git.Tag.delete(_repo, tag)

    # delete on remote origin
    # _run(c, f"git push --delete origin {tag}")
    _repo.remote('origin').push(refspec=[f":{tag}"])


@task(
    help={
        'new_tag': 'Dont use directly. Will be consumed from bump',
    }
)
def changelog(c, new_tag=None):
    """
    Generates changelog and saves it to CHANGELOG.md
    The logs cover the commit message on main branch from the last known
    stable tag.
    """
    # todo: Convert this blog with GitPython and PyGithub to python (blog ideas)
    # Refer: https://blogs.sap.com/2018/06/22/generating-release-notes-from-git-commit-messages-using-basic-shell-commands-gitgrep/

    # get tags
    _tags = sorted(
        _GIT_LOCAL_REPO.tags, key=lambda _: _.commit.committed_datetime)
    _tag_names = [_.name for _ in _tags]
    _last_stable_tag_name = [
        _ for _ in _tag_names
        if _ != 'log' and _.find('a') == -1 and _.find('b') == -1
    ][-1]

    # NOTE: this is with git but note that we lack the github owner
    #   so we will use github instead :(
    # [USING GIT]
    # get commits from last stable location
    # for _commit in \
    #     _GIT_LOCAL_REPO.iter_commits(rev=f'{_last_stable_tag_name}..HEAD'):
    #     print(_commit, type(_commit))
    # Also more raw way
    # refer https://git-scm.com/docs/pretty-formats
    # _commits = _git.log(
    #     f'{_last_stable_tag_name}..HEAD',
    #     '--pretty=format:"%h [ %ad ] @%al : %s"', '--date=short',
    # )
    # with github we use this api
    # https://docs.github.com/en/rest/reference/repos#commits
    # https://docs.github.com/en/rest/reference/repos#compare-two-commits
    # [USING GITHUB]
    _commits = \
        _GH_REMOTE_REPO.compare(
            base=_last_stable_tag_name, head=None or 'HEAD'
        ).commits
    _changelog_list = [
        f"## Changelog for {_last_stable_tag_name} >> {new_tag}",
        ""
    ]
    for _commit in _commits:
        _commit_str = \
            f"+ " \
            f"{_commit.sha[:7]} " \
            f"[ {_commit.committer.updated_at.strftime('%Y-%m-%d')} ] " \
            f"@{_commit.committer.login} : " \
            f"{_commit.commit.message}"
        _changelog_list.append(_commit_str)

    # make changelog
    _changelog = "\n".join(_changelog_list)

    # if show then display and return
    if new_tag is None:
        print(_changelog)
        return

    # write to file
    _changelog_file = pathlib.Path("CHANGELOG.md")
    _changelog_file.write_text(_changelog)

    # commit file
    _run(c, "git add CHANGELOG.md")
    _run(c, f'git commit -m '
            f'"[bot] Update changelog to reflect commits '
            f'from {_last_stable_tag_name} to {new_tag}"')


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
    dry_run=False, bump_into=None,
):
    """
    Handle bumping versions for toolcraft library.

    Version style:
      >> {major}.{minor}.{patch}{release_type}{release_num}
        release_type is one of ['a', 'b']
      >> {major}.{minor}.{patch}

    Behaviour:
      Five options for bumping:
        - alpha, beta, patch, minor, major
      When current version is in alpha
        calling alpha will increment release_num
        calling beta will make release_num=0 and release_type=beta
        calling patch will make it stable
        calling minor will raise error (you need to patch for making it stable)
        calling major will raise error (you need to patch for making it stable)
      When current version is in beta
        calling alpha will raise error as you cannot move backward
        calling beta will increment release_num
        calling patch will make it stable
        calling minor will raise error (you need to patch for making it stable)
        calling major will raise error (you need to patch for making it stable)
      When current version is stable
        with patch, minor, major make sure to use --bump-into option
          bump-into is one of 'alpha'. 'beta' or 'stable' (default 'alpha')
        calling alpha will raise error
        calling beta will raise error
      When current version in alpha or beta then you need to patch to get
        into stable release, before updating wither patch, minor or major

      Examples:
        When current release is stable
          >> invoke bump --dry-run --patch --bump-into alpha
        When current release is alpha or beta
          >> To make release stable
            >> invoke bump --dry-run --patch
          >> To increment alpha
            >> invoke bump --dry-run --alpha
          >> To move to beta
            >> invoke bump --dry-run --beta
    """
    # ------------------------------------------------- 01
    # Format is:
    #   >> {major}.{minor}.{patch}{release}{num}\
    #
    # Easy way to test `bump2version`
    #   bump2version --no-configured-files --dry-run --verbose
    #     --current-version 0.1.2 --new-version 0.1.2a2 xyz
    #
    # invoke bump --dry-run --patch --bump-into stable

    # ------------------------------------------------- 02
    # detect current version
    _curr_ver = \
        toml.load("pyproject.toml")['tool']['poetry']['version']
    _splits = _curr_ver.split(".")
    _major, _minor, _patch = \
        int(_splits[0]), int(_splits[1]), _splits[2]
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
            raise Exception(
                "The current version is stable. So please use either --patch, "
                "--minor or --major option along with --bump-into option"
            )
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
            raise Exception(
                "The current version is stable. So please use either --patch, "
                "--minor or --major option along with --bump-into option"
            )
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
    # estimate new tag
    if _release_type is None:
        _release_type = ''
    if _release_num is None:
        _release_num = ''
    _new_ver = f"v{_major}.{_minor}.{_patch}{_release_type}{_release_num}"
    _bump_command = f"bump2version --no-tag " \
                    f"--verbose " \
                    f"{'--dry-run' if dry_run else ''} " \
                    f"--current-version {_curr_ver} " \
                    f"--new-version {_new_ver} xyz"

    # ------------------------------------------------- 06
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("The bump command:", _bump_command)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    _run(c, _bump_command)
    _run(c, "git push")
    print()
    print()

    # ------------------------------------------------- 07
    # update changelog
    changelog(c, new_tag=_new_ver)
    _run(c, "git push")

    # ------------------------------------------------- 08
    # create release with gh
    _is_pre_release = _new_ver.find("a") != -1 or _new_ver.find("b") != -1
    _gh_release_command = \
        f"gh release create {_new_ver} " \
        f"{'--prerelease' if _is_pre_release else ''} " \
        f"--draft " \
        f"--target main " \
        f"--notes-file CHANGELOG.md " \
        f"--title '[bot] Releasing {_new_ver}' " \
        # f"--discussion-category 'General' " \

    # ------------------------------------------------- 07
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("The gh release command:", _gh_release_command)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    _run(c, _gh_release_command)
    print()
    print()

    # ------------------------------------------------- 09
    # print("We will run below commands to see and push newly created tags:")
    # print("  >>  git tag -n")
    # print("  >>  git push --tags")
    # _run(c, "git tag -n")
    # _run(c, "git push --tags")



