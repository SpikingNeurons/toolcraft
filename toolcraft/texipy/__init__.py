"""
Eventually this will evolve to TeXiPy ...

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
