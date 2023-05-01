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
+ Nice pdf for NN figures
  https://mkofinas.github.io/tikz_tutorial.pdf
"""

from . import helper
from .__base__ import *
from .base import Command, Glossary, Acronym, Symbol, make_symbols_tex_file
from . import beamer
from . import tikz
from . import tikz_cd
from . import table
