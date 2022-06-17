"""
Replicate:
https://ctan.org/pkg/beamer?lang=en
https://ftp.agdsn.de/pub/mirrors/latex/dante/macros/latex/contrib/beamer/doc/beameruserguide.pdf
https://latex-beamer.com/quick-start/
"""


from toolcraft.texipy import Beamer, Section, Color, SubSection, BeamerFrame, BeamerTableOfContentsFrame
from toolcraft.texipy import tikz


if __name__ == '__main__':

    _ppt = Beamer(
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
        item=BeamerTableOfContentsFrame(
            title="Outline", hide_all_subsections=False,
        )
    )

    _ppt.add_item(item=BeamerFrame(title="First Frame", label="first_frame").add_item("This is first frame ..."))

    _ppt.write(save_to_file="try.tex", make_pdf=True)
