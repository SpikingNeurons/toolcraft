"""
We do this tutorial in texipy
for official tikz pdf https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf
"""

from toolcraft.texipy import Document, Section, Color, SubSection
from toolcraft.texipy import tikz


def part_1_tut_0() -> tikz.TikZ:
    return tikz.TikZ(
        caption="Simple Figure", label="fig:sec1:simple"
    ).add_path(
        tikz.Path(
            style=tikz.Style(
                draw=tikz.DrawOptions(
                    color=Color.red, thickness=tikz.Thickness.thick,
                    rounded_corners=True,
                ),
            )
        ).connect(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(0))
        ).connect(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(2))
        ).connect(
            tikz.Point2D(tikz.Scalar(1), tikz.Scalar(3.25))
        ).connect(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(2))
        ).connect(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(0))
        ).connect(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(2))
        ).connect(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(2))
        ).connect(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(0))
        ).connect(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(0))
        )
    )


def part_1_tut_1():
    ...


def part_1_tut_2():
    ...


if __name__ == '__main__':

    _doc = Document(
        title="Till Tantau tutorials in TeXiPy",
        author="Praveen Kulkarni",
        date="\\today",
        main_tex_file="../main.tex",
    )

    _section_1 = Section(
        name="Tutorials by Till Tantau", label="sec1"
    )
    _section_1.add_item("Check https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf")

    _section_1_sub_1 = SubSection(
        name="Simple Figure", label="sec1:simple"
    ).add_item(item=part_1_tut_0())


    _doc.add_item(_section_1.add_item(_section_1_sub_1))



    _doc.write(save_to_file="try.tex", make_pdf=True)