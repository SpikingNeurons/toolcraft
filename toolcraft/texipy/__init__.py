"""
Eventually this will evolve to TeXiPy ...

Aim:
+ Get these tutorials covered
  https://www.overleaf.com/learn/latex/Tutorials
  + Priority figures and tables
"""

from . import helper
from .__base__ import Font, Color, Scalar, Document, Section, SubSection, \
    SubSubSection, Part, Paragraph, SubParagraph, Chapter, Fa, FontSize, \
    Positioning, FloatObjAlignment, Beamer
from .symbol import Command, Glossary, Acronym, make_symbols_tex_file
from . import tikz
from . import table
