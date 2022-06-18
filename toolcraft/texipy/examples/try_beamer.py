"""
Replicate:
https://ctan.org/pkg/beamer?lang=en
https://ftp.agdsn.de/pub/mirrors/latex/dante/macros/latex/contrib/beamer/doc/beameruserguide.pdf
https://latex-beamer.com/quick-start/
"""


from toolcraft.texipy import Section, Color, SubSection, List
from toolcraft.texipy import tikz, beamer
import try_table, try_tikz, try_document


if __name__ == '__main__':

    _ppt = beamer.Beamer(
        theme="Goettingen",
        title="My Presentation",
        short_title="My Ppt",
        sub_title="With subtitle subtitle ...",
        author="\nPraveen Kulkarni\\inst{1,2}\n\\and\nFirstname Lastname\\inst{1}\n",
        short_author="P. Kulkarni et al.",
        date="June 21, 2022",
        institute="\n"
                  "\\inst{1}Organization One \n"
                  "\\and \n"
                  "\\inst{2}Organization Two \n",
        symbols_file="symbols.tex",
        usepackage_file="usepackage.sty",
    )

    _ppt.add_item(
        item=beamer.TableOfContents(
            title="Outline", hide_all_subsections=False,
        )
    )

    # _ppt.add_item(
    #     item=beamer.TableOfContents(
    #         title="Outline", hide_all_subsections=False, current_section=True,
    #     )
    # )

    # ------------------------------------------------ add all sections
    _section_1 = Section(
        label="sec1", name="Section One ..."
    )
    _section_2 = Section(
        label="sec2", name="Section Two ..."
    )
    _ppt.add_item(_section_1).add_item(_section_2)

    # ------------------------------------------------ add all section 1
    _frame_1 = beamer.Frame(
        title="List1", label="list"
    ).add_item(
        item=List(
            type='itemize',
            items=[
                "Apple", "Mango", ("$\\blacksquare$", "Papaya"),
                # List(type='enumerate', items=["Apple", "Mango", "Orange"]),
                "Orange"
            ]
        )
    )
    _section_1.add_item(item=_frame_1)

    # ------------------------------------------------ add all section 2
    _section_2_1 = SubSection(label="sec2:tikz", name="Section Two ... TikZ")
    _section_2_2 = SubSection(label="sec2:table", name="Section Two ... Table")
    _section_2.add_item(_section_2_1).add_item(_section_2_2)
    _section_2_1.add_item(
        beamer.Frame(
            title="TikZ figure", label="tikz"
        ).add_item(
            item=try_tikz.make_complicated_figure()
        )
    )
    _section_2_2.add_item(
        beamer.Frame(
            title="Table", label="table"
        ).add_item(
            item=try_table.make_table()
        )
    )

    # ------------------------------------------------ write
    _ppt.write(save_to_file="try.tex", make_pdf=True)
