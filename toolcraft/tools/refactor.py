"""
Tool that will do powerful refactoring.

todo: register with tools.Tool later

todo: refer toolcraft.error._script

"""
import re
_SEARCH_REGEX = "e\.io\.[\s\S]*?\)"
_STR_OR_FILE_OR_FOLDER = """
def save_pickle(py_obj, file_path: pathlib.Path):
    # raise error if needed
    e.io.FileMustNotBeOnDiskOrNetwork(
        path=file_path, msgs=[]
    ).raise_if_failed()
def save_pickle(py_obj, file_path: pathlib.Path):
    # raise error if needed
    e.io.FileMustNotBeOnDiskOrNetwork(
        path=file_path, msgs=[]
    ).raise_if_failed()
"""


if __name__ == '__main__':
    ...
    # _iter = re.finditer(pattern=_SEARCH_REGEX, string=_STR_OR_FILE_OR_FOLDER)
    #
    # # this gives points to insert
    # for _ in _iter:
    #     print(_.span()[1])
