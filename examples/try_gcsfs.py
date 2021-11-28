from pyarrow import fs
local = fs.LocalFileSystem()
from fsspec.implementations.arrow import ArrowFSWrapper
local_fsspec = ArrowFSWrapper(local)

local_fsspec.mkdir("./test")
local_fsspec.touch("./test/file.txt")
xx = local_fsspec.ls("./test/")

print(xx)
