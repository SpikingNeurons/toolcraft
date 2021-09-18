import typing as t

from . import __base__
from . import widget
from . import callback
from .. import marshalling as m
from .. import error as e


def simple_split_window(
    dash_guid: str,
    title: str
) -> t.Tuple[__base__.Dashboard, widget.Group, widget.Group]:
    _dash = __base__.Dashboard(
        dash_guid=dash_guid,
        title=title, width=1200, height=2400,
    )

    # noinspection PyArgumentList
    _table = widget.Table(
        header_row=False,
        resizable=True, policy=widget.TableSizingPolicy.StretchSame,
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


def add_widgets_in_line(
    guid: str,
    receiver: __base__.Widget,
    widgets: t.List[__base__.Widget]
):
    receiver.add_child(
        guid=f"{guid}_{0}",
        widget=widgets[0],
    )
    for i, w in enumerate(widgets[1:]):
        receiver.add_child(
            guid=f"{guid}_{i}_il",
            widget=widget.InSameLine()
        )
        receiver.add_child(
            guid=f"{guid}_{i+1}",
            widget=w,
        )


def tab_bar_from_widget_dict(
    widget_dict: t.Dict, parent: __base__.Widget
):
    _tab_bar = widget.TabBar()
    parent.add_child(guid="tb", widget=_tab_bar)
    for _k in widget_dict.keys():
        _tab = widget.Tab(label=_k)
        _tab_bar.add_child(guid=_k, widget=_tab)
        _v = widget_dict[_k]
        if isinstance(_v, dict):
            tab_bar_from_widget_dict(_v, _tab)
        elif isinstance(_v, list):
            for _i, __v in enumerate(_v):
                _tab.add_child(
                    guid=f"{_i}",
                    widget=__v
                )
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
    binder: __base__.Binder
):
    # tab bar
    _tab_bar = widget.TabBar(
        label=title
    )

    # bind
    binder(_tab_bar)

    # loop over callable names
    for k, v in callable_names.items():
        _tab = widget.Tab(
            label=k
        )
        _tab_bar.add_child(
            guid=k, widget=_tab
        )
        getattr(hashable, v)(
            binder=__base__.Binder(
                guid=k, parent=_tab
            )
        )


def button_bar_from_hashable_callables(
    tab_group_name: str,
    hashable: m.HashableClass,
    title: str,
    close_button: bool,
    callable_names: t.Dict[str, str],
    no_main_ui: bool = False,
) -> __base__.Widget:
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
        _main_ui.add_child(
            guid="bb_sub_title",
            widget=widget.Text(
                f"{hashable.group_by}: {hashable.hex_hash}",
                bullet=True,
            )
        )

    # ----------------------------------------------------- 03
    # make buttons and add make them plot to _button_receiver
    _button_receiver = widget.Group()
    # make button bar
    _buttons = []
    # add close button
    if close_button:
        _buttons.append(
            callback.CloseWidgetCallback.get_button_widget()
        )
    # make buttons for callable names
    for _button_label, _callable_name in callable_names.items():
        _b = hashable.get_gui_button(
            tab_group_name=tab_group_name,
            button_label=_button_label,
            callable_name=_callable_name,
            receiver=_button_receiver,
            allow_refresh=True,
        )
        _buttons.append(_b)
    # add buttons to _main_ui
    add_widgets_in_line(guid="bb_line1", receiver=_main_ui, widgets=_buttons)
    # add separator
    # _main_ui.add_child(
    #     guid='bb_sep1', widget=widget.Separator()
    # )
    # add _button_receiver display to _main_ui
    _main_ui.add_child(
        guid="bb_r", widget=_button_receiver,
    )
    # add separator
    # _main_ui.add_child(
    #     guid='bb_sep2', widget=widget.Separator()
    # )

    # ----------------------------------------------------- 04
    # return
    return _main_ui



