import typing as t

from . import widget
from . import callback
from .. import marshalling as m
from .. import error as e


def simple_split_window(
    dash_guid: str,
    title: str
) -> t.Tuple["__base__.Dashboard", widget.Group, widget.Group]:
    _dash = __base__.Dashboard(
        dash_guid=dash_guid,
        title=title, width=1200, height=2400,
    )

    # noinspection PyArgumentList
    _table = widget.Table(
        header_row=False,
        resizable=True, policy=widget.TableSizing.StretchSame,
        borders_innerH=False, borders_outerH=True,
        borders_innerV=True, borders_outerV=True,
        rows=1, columns=2,
    )
    _button_cell = _table.get_cell(row=0, column=0)
    _display_cell = _table.get_cell(row=0, column=1)

    _dash.add_child(
        guid="t", widget=_table
    )

    return _dash, _button_cell, _display_cell


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


def button_bar_from_hashable_callables(
    group_tag: str,
    hashable: m.HashableClass,
    title: str,
    # todo: add icons for this
    close_button: bool,
    # todo: add icons for this
    info_button: bool,
    callable_names: t.Dict[str, str],
    no_main_ui: bool = False,
) -> widget.MovableWidget:
    # ----------------------------------------------------- 01
    # everything will be added to main UI which is window with
    # scrollbar
    if no_main_ui:
        _main_ui = widget.Group()
    else:
        # todo: instead of child we can also use Window which can pop out
        _main_ui = widget.CollapsingHeader(
            label=title, default_open=True,
        )
        # make title and add it main ui
        # _main_ui.add_child(
        #     guid="bb_sub_title",
        #     widget=widget.Text(
        #         f"{hashable.group_by}: {hashable.hex_hash}",
        #         bullet=True,
        #     )
        # )

    # ----------------------------------------------------- 03
    # make buttons and add make them plot to _button_receiver
    _button_receiver = widget.Group()
    # make button bar
    _buttons_bar = widget.Group(horizontal=True)
    # add close button
    if close_button:
        _buttons_bar(
            widget=callback.CloseWidgetCallback.get_button_widget(
                widget_to_delete=_main_ui),
        )
    # add info button
    if info_button:
        callable_names["Info"] = "info"

    # make buttons for callable names
    for _button_label, _callable_name in callable_names.items():
        _b = hashable.get_gui_button(
            group_tag=group_tag,
            button_label=_button_label,
            callable_name=_callable_name,
            receiver=_button_receiver,
            allow_refresh=True,
        )
        _buttons_bar(widget=_b)
    # add buttons to _main_ui
    _main_ui(widget=_buttons_bar)
    # add separator
    # _main_ui(widget=widget.Separator())
    # add _button_receiver display to _main_ui
    _main_ui(widget=_button_receiver)
    # add separator
    # _main_ui(widget=widget.Separator())

    # ----------------------------------------------------- 04
    # return
    return _main_ui
