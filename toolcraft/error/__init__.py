"""
todo: just like typer.Abort() we will implement errors taht can eb raised so that we
  need to explicitly type raise at end of error

todo: support rich things like
  syntax: for code with errors https://rich.readthedocs.io/en/stable/syntax.html
  layout: make columns for showing text diff https://rich.readthedocs.io/en/stable/layout.html
"""
from . import code, io, validation
