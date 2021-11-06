import typing as t

from . import widget
from .. import marshalling as m
from .. import error as e


def tab_bar_from_widget_dict(
    widget_dict: t.Dict, parent: widget.ContainerWidget
):
    _tab_bar = widget.TabBar()
    parent(widget=_tab_bar)
    for _k in widget_dict.keys():
        _tab = widget.Tab(label=_k)
        _tab_bar(widget=_tab)
        _v = widget_dict[_k]
        if isinstance(_v, dict):
            tab_bar_from_widget_dict(_v, _tab)
        elif isinstance(_v, list):
            for _i, __v in enumerate(_v):
                _tab(widget=__v)
        else:
            e.code.CodingError(
                msgs=[
                    f"Unrecognized type {type(_v)}"
                ]
            )


def tab_bar_from_hashable_callables(
    title: str,
    hashable: m.HashableClass,
    callable_names: t.Dict[str, str],
):
    # tab bar
    _tab_bar = widget.TabBar(
        label=title
    )

    # loop over callable names
    for k, v in callable_names.items():
        _ret_widget = getattr(hashable, v)()
        _tab = widget.Tab(label=k)
        _tab(widget=_ret_widget)
        _tab_bar(widget=_tab)
