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
        items=[
            Section(
                name="Introduction",
                items=[
                    tikz.TikZ(items=[]).draw_circle(
                        x=0, y=3, radius=10, draw=Color.red, fill=Color.green,
                        thickness=tikz.Thickness.very_thick
                    ).draw_circle(
                        x=3, y=3, radius=10, draw=Color.red, fill=Color.green,
                        thickness=tikz.Thickness.very_thick
                    )
                ]
            )
        ],
        main_tex_file="../main.tex",
    )

    _doc.write(save_to_file="try.tex", make_pdf=True)