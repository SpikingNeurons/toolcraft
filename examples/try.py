import fsspec
from fsspec.implementations.local import LocalFileSystem



if __name__ == "__main__":

    fs = LocalFileSystem()

    for _ in fs.glob(path="*.py"):
        print(_)