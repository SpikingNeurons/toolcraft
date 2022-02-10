from toolcraft import texipy

_doc = texipy.Document(
    items=["sadsafsd"],
    main_tex_file="../main.tex",
)

_doc.write(save_to_file="try.tex", make_pdf=True)
print(_doc)