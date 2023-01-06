"""
Eventually this will evolve to TeXiPy ...

todo: Adds ASGI server support using Uvicorn of Hypercorn
  needed so that make pdf can be called as and when any file changes
  Have a design which can augment toolcraft.job or have separate module called
  toolcraft.server

Aim:
+ Get these tutorials covered
  https://www.overleaf.com/learn/latex/Tutorials
  + Priority figures and tables
"""

from . import helper
from .__base__ import *
from .symbol import Command, Glossary, Acronym, make_symbols_tex_file
from . import beamer
from . import tikz
from . import table
