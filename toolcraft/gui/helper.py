import typing as t

from . import widget
from .. import marshalling as m
from .. import error as e


def tab_bar_from_widget_dict(widget_dict: t.Dict) -> widget.TabBar:
    _tab_bar = widget.TabBar()
    for _k, _v in widget_dict.items():
        _tab = widget.Tab(label=_k)
        _tab_bar(widget=_tab)
        if isinstance(_v, dict):
            _tab(tab_bar_from_widget_dict(_v))
        elif isinstance(_v, list):
            for _i, __v in enumerate(_v):
                _tab(widget=__v)
        else:
            raise e.code.CodingError(
                msgs=[
                    f"Unrecognized type {type(_v)}"
                ]
            )
    return _tab_bar


def tab_bar_from_hashable_callables(
    title: str,
    hashable: m.HashableClass,
    callable_names: t.Dict[str, str],
) -> widget.TabBar:
    # tab bar
    _tab_bar = widget.TabBar(label=title)
    # loop over callable names
    for k, v in callable_names.items():
        _ret_widget = getattr(hashable, v)()
        _tab = widget.Tab(label=k)
        _tab(widget=_ret_widget)
        _tab_bar(widget=_tab)
    # return
    return _tab_bar
