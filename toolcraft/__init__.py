"""
Top-level package for toolcraft.

Resolving __version__
  + This cannot be hardcoded also the external setup files are not shipped so
    we use this solution
    https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
  + Read the discussion here as to why this is so tedious
    https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
  + Note that bump2version tends to modify the string so always use poetry

todo: find a way to get info in `pyproject.toml` to update this file so we
  have project info inside the code.
  + This needs to be automated and the source code should be updated here
    before release happens. This is done by bump2version but poetry doesnt
    seem to support it .... doing this will allow us to get packaging
    information inside code.
  + Or else we have to rely on importlib which has some packaging info when
    poetry packaged it...
  + Watch this space and do if needed
  + See the author and email info here ... it looks ugly to update it ...
  + We might want it as in sphinx documentation we can access this variables

todo: tiangolo has come up with elegant plugin
  + https://github.com/tiangolo/poetry-version-plugin
  + track it and update it when there is more stable and widely adopted solution
  + Also see debate at
    + https://github.com/python-poetry/poetry/issues/4299
  + Also see this comment from poetry guys
    + https://github.com/python-poetry/poetry/issues/144#issuecomment-392299465

todo: Also refer
  https://guild.ai/
  https://github.com/ml-tooling/ml-workspace

todo: asyncio (https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor)
  + for io bound use concurrent.futures.ThreadPoolExecutor()
  + for cpu bound use concurrent.futures.ProcessPoolExecutor()


"""
__author__ = """Praveen Kulkarni"""
__email__ = "praveenneuron@gmail.com"
__version__ = "0.1.4a21"

from . import settings
from . import logger
from . import error
from . import util
from . import marshalling
from . import parallel
from . import storage
from . import ml
from . import job
from . import richy
from . import texipy

if settings.DPG_WORKS:
    # as some rules use dpg
    from . import gui

# decorate undecorated and hence rule check

# todo: when using toolcraft in interactive mode enable this
# Rich may be installed in the REPL so that Python data structures are automatically
# pretty printed with syntax highlighting.
# This makes the toolcraft console UI colorful in interactive mode
# from rich import pretty
# pretty.install()
