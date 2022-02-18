"""
We do this tutorial in texipy
https://www.overleaf.com/learn/latex/TikZ_package
"""

from toolcraft.texipy import Document, Section, Color
from toolcraft.texipy import tikz


if __name__ == '__main__':
    _doc = Document(
        title="TikZ tutorial",
        author="Praveen Kulkarni",
        date="\\today",
        main_tex_file="../main.tex",
    )

    _doc.write(save_to_file="try.tex", make_pdf=True)