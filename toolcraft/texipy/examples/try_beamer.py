"""
Replicate:
https://ctan.org/pkg/beamer?lang=en
https://ftp.agdsn.de/pub/mirrors/latex/dante/macros/latex/contrib/beamer/doc/beameruserguide.pdf
https://latex-beamer.com/quick-start/
"""


from toolcraft.texipy import Beamer, Section, Color, SubSection
from toolcraft.texipy import tikz


if __name__ == '__main__':

    _ppt = Beamer(
        theme="Goettingen",
        title="My Presentation",
        short_title="My Ppt",
        sub_title="With subtitle subtitle ...",
        author="\nPraveen Kulkarni\\inst{1,2}\n\\and\nPraveen Kulkarni\\inst{1}\n",
        short_author="P. Kulkarni et al.",
        date="\\today",
        institute="\n"
                  "\\inst{1}NXP Semiconductors Germany GmbH \n"
                  "\\and \n"
                  "\\inst{2}Radboud University, Nijmegen, Netherlands \n",
        symbols_file="symbols.tex",
        usepackage_file="usepackage.sty",
    )

    _ppt.write(save_to_file="try.tex", make_pdf=True)
