import inspect
import pathlib
import textwrap
import numpy as np
import dearpygui.dearpygui as dpg


def gen_widget(_method, _widget_name, _enum_fields):

    _signature = inspect.signature(_method)
    _is_wrapped = '__wrapped__' in dir(_method)

    # if method name starts with add_ check if it has wrapped counterpart in module dpg
    if _method.__name__.startswith("add_"):
        if _method.__name__.replace("add_", "") in dir(dpg):
            raise Exception(
                f"Looks like there is wrapped counterpart for `{_method.__name__}`"
            )

    # make _docs_dict
    _main_doc = []
    _docs_dict = {}
    _track = False
    for _l in _method.__doc__.split("\n"):
        _l_strip = _l.strip()
        if _l_strip in ['Returns:', 'Yields:']:
            break
        if _l_strip == 'Args:':
            _track = True
            continue
        if _track:
            _k = _l_strip.replace("*", '').split(' ')[0]
            _v = _l_strip.split(':')[1].strip()
            if _v == '':
                _v = '...'
            _docs_dict[_k] = _v
        else:
            for _s in textwrap.wrap(_l_strip, 70):
                _main_doc.append(f"\t{_s}")

    # header
    _lines = [
        "",
        "",
        "@dataclasses.dataclass(frozen=True)",
        f"class {_widget_name}(Widget):",
        '\t"""',
        "\tRefer:",
        f"\t>>> dpg.{_method.__name__}",
        "",
    ] + _main_doc + ['\t"""', ""]

    # make sure that _enum_fields keys are valid
    _all_param_names = [_.name for _ in _signature.parameters.values()]
    for _enum_field_key in _enum_fields.keys():
        if _enum_field_key not in _all_param_names:
            raise Exception(
                f"The key {_enum_field_key} is not one of {_all_param_names}"
            )

    # make fields
    _callback_params = []
    _all_params_to_consider = []
    _Axis_axis = []
    for _param in _signature.parameters.values():
        _param_name = _param.name
        if _param_name in ['id', 'parent', 'before', ]:
            continue
        if _widget_name in ['XAxis', 'YAxis']:
            if _param_name == 'axis':
                _Axis_axis.append(
                    f"\t\t\taxis="
                    f"{'dpg.mvXAxis' if _widget_name == 'XAxis' else 'dpg.mvYAxis'},"
                )
                continue
        _param_type = f"{_param.annotation}".replace(
            'typing', 't'
        ).replace(
            "<class '", ""
        ).replace(
            "'>", ""
        ).replace(
            "t.Callable", "Callback"
        )
        _all_params_to_consider.append(_param_name)
        try:
            for _s in textwrap.wrap(_docs_dict[_param_name], 70):
                _lines.append(f"\t# {_s}")
        except KeyError as _ke:
            if _param_name == 'kwargs':
                pass
            else:
                raise _ke
        if _param_type.find("Callback") != -1:
            _callback_params.append(_param_name)
        _param_value = _param.default
        if _param_name == "source":
            _param_type = "t.Optional[Widget]"
            _param_value = "None"
        if _param_name == "policy":
            _param_type = "TableSizing"
            _param_value = "None"
        if _param_name == "user_data":
            _param_type = "t.Union[Widget, t.List[Widget]]"
            _param_value = "None"
        if _param_name == "on_enter":
            _param_name = "if_entered"
        if _param_name == "kwargs":
            _param_name = "# kwargs"
        if _param_name in _enum_fields.keys():
            _param_value = _enum_fields[_param_name]
            _param_type = _param_value.split('.')[0]
        _parm_str = f"\t{_param_name}: {_param_type}"
        # noinspection PyUnresolvedReferences,PyProtectedMember
        if _param_value != inspect._empty:
            if _param_value in ["", "$$DPG_PAYLOAD"] or \
                    str(_param_value).startswith('%'):
                _parm_str += f" = '{_param_value}'"
            elif isinstance(_param_value, list):
                _parm_str += f" = \\\n\t\tdataclasses.field(default_factory=list)"
            else:
                _parm_str += f" = {_param_value}"

        _lines.append(_parm_str)
        _lines.append("")

    # make property is_container
    _lines += [
        "\t@property",
        "\tdef is_container(self) -> bool:",
        f"\t\treturn {_is_wrapped}"
    ]

    # make method build()
    _kwargs = []
    for _param in _all_params_to_consider:
        _assign_str = f"\t\t\t{_param}=self.{_param},"
        if _param in ["source", ]:
            _assign_str = \
                f"\t\t\t" \
                f"{_param}=0 if self.{_param} is None else self." \
                f"{_param}.dpg_id,"
        if _param == "on_enter":
            _assign_str = f"\t\t\t{_param}=self.if_entered,"
        if _param in _enum_fields.keys():
            _assign_str = f"\t\t\t{_param}=self.{_param}.value,"
        if _param in _callback_params:
            _assign_str = f"\t\t\t{_param}=self.{_param}_fn,"
        if _param == "kwargs":
            _assign_str = f"\t\t\t# {_param}=self.{_param},"
        _kwargs.append(_assign_str)

    _lines += [
        "",
        "\tdef build(self) -> t.Union[int, str]:",
        f"\t\t_ret = dpg.{'add_' if _is_wrapped else ''}{_method.__name__}(",
        *_Axis_axis,
        f"\t\t\t**self.internal.dpg_kwargs,",
        *_kwargs,
        f"\t\t)",
        f"\t\t",
        f"\t\treturn _ret",
    ]

    # add methods for callback params
    for _cp in _callback_params:
        _lines += [
            "",
            f"\tdef {_cp}_fn("
            f"\n\t\tself, "
            f"\n\t\tsender_dpg_id: int, "
            f"\n\t\tapp_data: t.Any, "
            f"\n\t\tuser_data: t.Any"
            f"\n\t):",
            # todo: remove this sanity check
            "\t\t# eventually remove this sanity check ("
            "dpg_widgets_generator.py)...",
            "\t\tassert sender_dpg_id == self.dpg_id, \\"
            "\n\t\t\t'was expecting the dpg_id to match ...'",
            "",
            "\t\t# logic ...",
            f"\t\tif self.{_cp} is None:",
            f"\t\t\treturn None",
            f"\t\telse:",
            f"\t\t\treturn self.{_cp}.fn("
            f"\n\t\t\t\tsender=self, app_data=app_data, user_data=user_data"
            f"\n\t\t\t)",
        ]

    # replace \t to 4 spaces
    _lines = [_.replace("\t", "    ") for _ in _lines]

    # return
    return _lines


def gen_enum(_enum_class_name, _dpg_prefix):

    _code = f'''

class {_enum_class_name}(m.FrozenEnum, enum.Enum):

'''

    _code += f"\tDEFAULT = 0\n"
    for _ in dir(dpg):
        if _.startswith(_dpg_prefix):
            _enum_item = _.replace(_dpg_prefix, "")
            if _enum_item == 'None':
                _enum_item = 'NONE'
            _code += f"\t{_enum_item} = dpg.{_}\n"

    _code += f'''
    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_{_enum_class_name}"
'''

    _code = _code.replace("\t", "    ")

    return _code


def gen_auto_widgets_and_enums():
    # ---------------------------------------------------- 01
    _header = '''"""
********************************************************************************
** This code is auto-generated using script `scripts/dpg_widget_generator.py` **
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dataclasses
import dearpygui.dearpygui as dpg
import typing as t
import enum

from ... import marshalling as m
from .. import Widget, Callback, Color
'''
    # ---------------------------------------------------- 02
    # see if mv and can be enum
    _unique_items = []
    for _item in dir(dpg):
        if not _item.startswith("mv"):
            continue
        if _item.find("_") == -1:
            continue
        _item = "_".join(_item.split('_')[:-1]) + "_"
        _unique_items.append(_item)
    # see if group
    _unique_items, _unique_count = np.unique(_unique_items, return_counts=True)
    _unique_items = list(_unique_items[_unique_count > 1])
    # make enum items
    _enum_items = []
    for _ui in _unique_items:
        if _ui in ['mvColorEdit_', 'mvColorEdit_input_', 'mvKey_', 'mvReservedUUID_']:
            continue
        if _ui == 'mvTable_':
            _enum_items.append(('TableSizing', 'mvTable_Sizing'))
        else:
            _enum_items.append((_ui.replace("_", "").replace("mv", ""), _ui))
    # create code
    _enum_code = ""
    for _enum_class_name, _dpg_prefix in _enum_items:
        _enum_code += gen_enum(_enum_class_name, _dpg_prefix)

    # ---------------------------------------------------- 03
    _widget_items = [
        (dpg.add_table_column, "Column", {}),
        (dpg.table_row, "Row", {}),
        (dpg.table, "BTable", {'policy': 'TableSizing.DEFAULT'}),
        (dpg.add_tab_button, "TabButton", {}),
        (dpg.tab_bar, "TabBar", {}),
        (dpg.tab, "Tab", {}),
        (dpg.add_button, "Button", {}),
        (dpg.add_combo, "Combo", {}),
        (dpg.add_separator, "Separator", {}),
        (dpg.child_window, "ChildWindow", {}),
        (dpg.window, "Window", {}),
        (dpg.add_text, "Text", {'color': 'Color.DEFAULT'}),
        (dpg.collapsing_header, "CollapsingHeader", {}),
        (dpg.group, "Group", {}),
        (dpg.add_plot_legend, "Legend", {'location': 'PlotLocation.NorthWest'}),
        (dpg.plot_axis, "XAxis", {}),
        (dpg.plot_axis, "YAxis", {}),
        (dpg.subplots, "SubPlot", {}),
        (dpg.add_simple_plot, "SimplePlot", {}),
        (dpg.plot, "BPlot", {}),
        (dpg.add_input_intx, "InputIntX", {}),
        (dpg.add_input_int, "InputInt", {}),
        (dpg.add_progress_bar, "ProgressBar", {}),
        (dpg.add_checkbox, "CheckBox", {}),
        (dpg.add_colormap_scale, "ColorMapScale", {}),
        (dpg.add_drag_line, "DragLine", {'color': 'Color.DEFAULT'}),
        (dpg.add_drag_point, "DragPoint", {'color': 'Color.DEFAULT'}),
        (dpg.add_slider_int, "SliderInt", {}),
        (dpg.add_slider_intx, "SliderIntX", {}),
        (dpg.add_slider_float, "SliderFloat", {}),
        (dpg.add_slider_floatx, "SliderFloatX", {}),
        (dpg.add_3d_slider, "Slider3D", {}),
        (dpg.tooltip, "ToolTip", {}),
        (dpg.theme, "Theme", {}),
        # (dpg.theme_component, "ThemeComponent", {}),
        (
            dpg.add_theme_color, "ThemeColor",
            {
                'value': 'Color.BLACK',
                'target': 'ThemeCol.DEFAULT',
                'category': 'ThemeCat.DEFAULT',
            }
         ),
        (
            dpg.add_theme_style, "ThemeStyle",
            {
                'target': 'ThemeCol.DEFAULT',
                'category': 'ThemeCat.DEFAULT',
            }
        ),
    ]
    _widget_lines = []
    for _method, _widget_name, _enum_fields in _widget_items:
        _widget_lines += gen_widget(_method, _widget_name, _enum_fields)
    _widget_code = "\n".join(_widget_lines + [""])

    # ---------------------------------------------------- 04
    _output_file = pathlib.Path("../widget/auto.py")
    _output_file.write_text(_header + _enum_code + _widget_code)


if __name__ == '__main__':

    gen_auto_widgets_and_enums()
