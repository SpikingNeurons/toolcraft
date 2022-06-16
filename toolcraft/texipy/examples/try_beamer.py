"""
Replicate:
https://ctan.org/pkg/beamer?lang=en
https://ftp.agdsn.de/pub/mirrors/latex/dante/macros/latex/contrib/beamer/doc/beameruserguide.pdf
"""


from toolcraft.texipy import Beamer, Section, Color, SubSection
from toolcraft.texipy import tikz


if __name__ == '__main__':

    _ppt = Beamer(
        theme="Boadilla",
        title="My Presentation",
        sub_title="With subtitle subtitle ...",
        author="Praveen Kulkarni",
        date="\\today",
        institute="My Organization",
        symbols_file="symbols.tex",
        usepackage_file="usepackage.sty",
    )

    _ppt.write(save_to_file="try.tex", make_pdf=True)
