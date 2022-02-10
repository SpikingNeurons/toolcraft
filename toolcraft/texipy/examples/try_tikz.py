"""
We do this tutorial in texipy
https://www.overleaf.com/learn/latex/TikZ_package
"""

from toolcraft import texipy



if __name__ == '__main__':
    _doc = texipy.Document(
        title="TikZ tutorial",
        author="Praveen Kulkarni",
        date="\\today",
        items=[
            "dsfsdfsdfsd"
        ],
        main_tex_file="../main.tex",
    )

    _doc.write(save_to_file="try.tex", make_pdf=True)