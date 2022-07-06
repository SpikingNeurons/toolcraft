"""
We do this tutorial in texipy
for official tikz pdf https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf

Visual tikz tutorials: http://tug.ctan.org/info/visualtikz/VisualTikZ.pdf
"""

from toolcraft.texipy import Document, Section, Color, SubSection
from toolcraft.texipy import tikz
import try_table, try_tikz, try_document


def part_1_tut_0() -> tikz.TikZ:
    return tikz.TikZ(
        caption="Simple Figure", label="fig:sec1:simple"
    ).add_path(
        tikz.Path(
            style=tikz.Style(
                draw=tikz.DrawOptions(
                    color=Color.red,
                    thickness=tikz.Thickness.thick,
                    rounded_corners=tikz.Scalar(5, 'pt'),
                ),
            )
        ).move_to(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(0))
        ).line_to(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(2))
        ).line_to(
            tikz.Point2D(tikz.Scalar(1), tikz.Scalar(3.25))
        ).line_to(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(2))
        ).line_to(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(0))
        ).line_to(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(2))
        ).line_to(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(2))
        ).line_to(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(0))
        ).line_to(
            tikz.Point2D(tikz.Scalar(2), tikz.Scalar(0))
        )
    )


def part_1_tut_1():
    _tikz = tikz.TikZ(
        caption="A Picture for Karl's Students", label="fig:sec1:karls_student"
    )
    _circle_path = tikz.Path(
        style=tikz.Style(
            shape=tikz.Circle(minimum_size=tikz.Scalar(2, 'pt'), inner_sep=tikz.Scalar(1, 'pt')),
            draw=tikz.DrawOptions(
                color=Color.gray,
            ),
            fill=tikz.FillOptions(
                color=Color.gray,
            ),
        )
    )
    for _x, _y in [(0, 0), (1, 1), (2, 1), (2, 0)]:
        _circle_path.move_to(
            to=tikz.Point2D(tikz.Scalar(_x), tikz.Scalar(_y))
        ).circle(
            radius=tikz.Scalar(2, 'pt')
        )
    _tikz.add_path(_circle_path)
    _tikz.add_path(
        tikz.Path(
            style=tikz.Style(draw=tikz.DrawOptions())
        ).move_to(
            tikz.Point2D(tikz.Scalar(0), tikz.Scalar(0))
        ).curve_to(
            to=tikz.Point2D(tikz.Scalar(2), tikz.Scalar(0)),
            control1=tikz.Point2D(tikz.Scalar(1), tikz.Scalar(1)),
            control2=tikz.Point2D(tikz.Scalar(2), tikz.Scalar(1)),
        )
    )
    return _tikz


def make_section_1(_doc):
    _section_1 = Section(
        name="Tutorials by Till Tantau", label="sec1"
    )
    _section_1.add_item("Check https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf")

    _section_1_tut_0 = SubSection(
        name="Simple Figure", label="sec1:simple"
    ).add_item(item=part_1_tut_0())

    _section_1_tut_1 = SubSection(
        name="A Picture for Karl's Students", label="sec1:karls_student"
    ).add_item(item=part_1_tut_1())

    _doc.add_item(_section_1.add_item(_section_1_tut_0).add_item(_section_1_tut_1))


def make_section_2(_doc):
    _section_2 = Section(
        name="Tutorials by Praveen Kulkarni", label="sec2"
    )

    # _section_2_tut_0 = SubSection(
    #     name="Using Table", label="sec2:table"
    # ).add_item(item=try_table.make_table())
    # _section_2.add_item(_section_2_tut_0)
    #
    # _section_2_tut_1 = SubSection(
    #     name="Using TikZ", label="sec2:tikz"
    # ).add_item(item=try_tikz.make_complicated_figure())
    # _section_2.add_item(_section_2_tut_1)

    _section_2_tut_2 = SubSection(
        name="Using List", label="sec2:list"
    )
    try_document.make_lists(_section_2_tut_2)
    _section_2.add_item(_section_2_tut_2)

    _doc.add_item(_section_2)


if __name__ == '__main__':

    # -------------------------------------------------------------------------
    _doc = Document(
        title="Till Tantau tutorials in TeXiPy",
        author="Praveen Kulkarni",
        date="\\today",
        main_tex_file="../main.tex",
        symbols_file="symbols.tex",
        usepackage_file="usepackage.sty",
    )

    # -------------------------------------------------------------------------
    # make_section_1(_doc)

    # -------------------------------------------------------------------------
    make_section_2(_doc)

    # -------------------------------------------------------------------------
    _doc.write(save_to_file="try.tex", make_pdf=True)
