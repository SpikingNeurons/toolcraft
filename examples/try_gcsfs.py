from pyarrow import fs
local = fs.LocalFileSystem()
from fsspec.implementations.arrow import ArrowFSWrapper
from fsspec.implementations.github import GithubFileSystem
from fsspec.gui import FileSelector

local_fsspec = ArrowFSWrapper(local)

local_fsspec = GithubFileSystem(org='SpikingNeurons', repo='toolcraft')

print(local_fsspec.ls(path="/"))

