"""
Eventually this will evolve to TeXiPy ...

Aim:
+ Get these tutorials covered
  https://www.overleaf.com/learn/latex/Tutorials
  + Priority figures and tables
"""

from . import helper, table, tikz
from .__base__ import (
    Chapter,
    Color,
    Document,
    Fa,
    FloatObjAlignment,
    Font,
    FontSize,
    Paragraph,
    Part,
    Positioning,
    Scalar,
    Section,
    SubParagraph,
    SubSection,
    SubSubSection,
)
from .symbol import Acronym, Command, Glossary, make_symbols_tex_file
