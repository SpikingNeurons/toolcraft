"""
Simple Latex components from __base__
"""
from toolcraft.texipy import List, SubSection


def make_lists(sec: SubSection):
    sec.add_item("List: Itemize")
    sec.add_item(
        item=List(type='itemize', items=["Apple", "Mango", "Orange"])
    )

    sec.add_item("List: Enumerate")
    sec.add_item(
        item=List(type='enumerate', items=["Apple", "Mango", "Orange"])
    )

    sec.add_item("List: Enumerate and Nested and Unordered")
    sec.add_item(
        item=List(
            type='enumerate',
            items=[
                "Apple", "Mango", ("$\\blacksquare$", "Papaya"),
                List(type='enumerate', items=["Apple", "Mango", ("$\\blacksquare$", "Papaya"), "Orange"]),
                "Orange"
            ]
        )
    )

    sec.add_item("List: With bullet https://latex-tutorial.com/bullet-styles/")
    sec.add_item(
        item=List(
            type='enumerate',
            items=[
                ("\\textbf{?}", "Apple"),
                ("\\$\\$]", "Mango"),
                ("$\\blacksquare$", "Orange"),
                ("\\textit{Re}", "Orange"),
                ("--", "Orange"),
                ("$-$", "Orange"),
                ("$\\ast$", "Orange"),
            ]
        )
    )
