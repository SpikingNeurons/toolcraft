#! python

import pathlib
import shutil
import sys
import typing


# figures out package name
def _return_package_name(_package_name: str) -> str:
    tokens = _package_name.rsplit('-', maxsplit=1)
    pn_start, pn_end = tokens[0], tokens[1]
    if pn_end[0].isdigit():
        return pn_start
    else:
        return _return_package_name(pn_start)


# get the name of packages on the disk
def move_packages(pypi_root_dir: str):
    # current dir
    current_dir = pathlib.Path(__file__).parent

    # get all items in dir
    all_fs = current_dir.glob("*")

    # get only files
    fs = [
        f for f in all_fs
        if f.is_file() and
        f.name not in [
            'pip_detect_redundant_packages.py', 'pip_package_mover.py',
            'install_from_internal_repo.bat', 'install_from_local_dir.bat',
        ]
    ]

    # estimate package names
    for f in fs:
        # get package name
        package_name = _return_package_name(f.name)
        # the underscores need to be replaced (might not work for tar files)
        package_name = package_name.replace("_", "-")
        # make package name lower case
        package_name = package_name.lower()

        # make dirs for pypi
        pypi_dir = pathlib.Path(pypi_root_dir) / package_name
        pypi_dir.mkdir(exist_ok=True)

        # move packages in respective dirs
        dst_f = pypi_dir / f.name
        shutil.copy(str(f), str(dst_f))


print()
if len(sys.argv) != 2:
    raise Exception(
        f"Please call this script with an arg that indicates `pypi_root_dir`"
    )
_pypi_root_dir = sys.argv[1]
print(f"Moving packages to pypi_root_dir {_pypi_root_dir}")
move_packages(pypi_root_dir=_pypi_root_dir)
input("PRESS ANY KEY TO EXIT ...")
