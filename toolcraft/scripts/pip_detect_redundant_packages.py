#! python

import pathlib
import shutil
import sys

if len(sys.argv) != 2:
    raise Exception(
        f"Please call this script with an arg that indicates `pypi_root_dir`"
    )

pypi_root_dir = sys.argv[1]

# get all items in dir
all_fs = pathlib.Path(pypi_root_dir).glob("*")

# get only files
dirs = [d for d in all_fs if d.is_dir()]

# skip somethings
dirs = [d for d in dirs]

# header
print()
print("--------------------------------------------------------")
print("Multiple versions if any will be displayed below ... !!!")
print("--------------------------------------------------------")
print()

# detect multiple versions in a package
print()
for d in dirs:
    fs = [f for f in d.glob("*")]
    if len(fs) > 1:
        print()
        print(f"package: {d.name}")
        for f in fs:
            print(f"          > {f.name}")

print()
print()
print("--------------------------------------------------------")
print("--------------------------------------------------------")
input("PRESS ANY KEY TO EXIT ...")
print()
