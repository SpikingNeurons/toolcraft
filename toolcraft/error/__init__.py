"""
todo: just like typer.Abort() we will implement errors taht can eb raised so that we
  need to explicitly type raise at end of error
"""

from .__base__ import CustomException
from . import code, io, validation
