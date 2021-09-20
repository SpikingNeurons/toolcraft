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

"""
__author__ = """Praveen Kulkarni"""
__email__ = "praveenneuron@gmail.com"
__version__ = "0.1.3"
