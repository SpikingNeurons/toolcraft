import inspect
import pathlib
import dataclasses
import dearpygui.dearpygui as dpg
from typing import NamedTuple
import typing as t
import re

_WRAP_TEXT_WIDTH = 70
_NEEDED_ENUMS = {}


class WidgetBuildParamDef(NamedTuple):
    name: str
    type: str
    value: str
    dpg_value: str
    doc: str

    @property
    def class_field_def(self) -> str:
        return f"\t{self.name}: {self.type} = {self.value}"

    @property
    def is_callback(self) -> bool:
        return self.type.find("Callback") != -1


@dataclasses.dataclass(frozen=True)
class WidgetDef:
    method: t.Callable

    # used to generate multiple widgets based on parameters supplied that will be
    # hardcoded in build method
    parameters: t.Dict[str, str] = None

    @property
    def name(self) -> str:
        # ------------------------------------------------------- 01
        # generate name based on method and parameters
        if self.method == dpg.plot_axis:
            if self.parameters['axis'] == 'dpg.mvXAxis':
                return "BXAxis"
            if self.parameters['axis'] == 'dpg.mvYAxis':
                return "BYAxis"
            raise Exception(
                f"Unknown parameter value for axis {self.parameters['axis']}"
            )

        # ------------------------------------------------------- 02
        # if you reach here means parameters are not needed
        assert self.parameters is None, "You need not supply parameters"

        # ------------------------------------------------------- 03
        # generate name based on method
        if self.method == dpg.table:
            return "BTable"
        if self.method == dpg.plot:
            return "BPlot"
        if self.method == dpg.add_3d_slider:
            return "Slider3D"

        # ------------------------------------------------------- 04
        # default name generation
        _name = self.method.__name__.replace("add_", "")
        _name = _name.title().replace("_", "")
        _name = _name.replace("Intx", "IntX").replace("Floatx", "FloatX")

        # ------------------------------------------------------- 05
        return _name

    @property
    def has_dpg_contextmanager(self) -> bool:
        return '__wrapped__' in dir(self.method)

    def __post_init__(self):
        # make checks
        self.checks()

    def checks(self):
        # ---------------------------------------------------------- 01
        # if method name starts with add_ check if it has wrapped counterpart
        # in module dpg
        if self.method.__name__.startswith("add_"):
            if self.method.__name__.replace("add_", "") in dir(dpg):
                raise Exception(
                    f"Looks like there is wrapped counterpart for "
                    f"`{self.method.__name__}`. "
                    f"May be you need to make widget for that as this method will be "
                    f"consumed by it."
                )
        # ---------------------------------------------------------- 02
        # calling name property to do more checks
        _ = self.name

    def get_docs(self) -> t.Dict[str, str]:
        _main_doc = []
        _docs_dict = {}
        _track = False
        for _l in self.method.__doc__.split("\n"):
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
                _v = _l_strip.split(':')[0].strip() + ": " + _v
                _docs_dict[_k] = _v
            else:
                _main_doc.append(_l)
        _docs_dict['main_doc'] = "\n".join(_main_doc)
        return _docs_dict

    def code(self) -> t.List[str]:
        # ------------------------------------------------------- 01
        # initial things
        self.checks()

        # ------------------------------------------------------- 02
        # get docs dict
        _docs_dict = self.get_docs()
        _param_defs = self.get_param_defs()

        # ------------------------------------------------------- 03
        # make code lines
        # ------------------------------------------------------- 03.01
        # code header
        _lines = [
            "",
            "",
            "@dataclasses.dataclass(frozen=True)",
            f"class {self.name}(Widget):",
            '\t"""',
            "\tRefer:",
            f"\t>>> dpg.{self.method.__name__}",
            "",
        ] + [_docs_dict['main_doc']] + ['\t"""', ""]
        # ------------------------------------------------------- 03.02
        # make fields
        for _pd in _param_defs:
            _lines += [f"\t# {_pd.doc}"]
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if _pd.value is inspect._empty:
                _lines += [f"\t{_pd.name}: {_pd.type}"]
            else:
                _lines += [f"\t{_pd.name}: {_pd.type} = {_pd.value}"]
            _lines += [""]

        # ------------------------------------------------------- 03.03
        # make property has_dpg_contextmanager
        _lines += [
            "\t@property",
            "\tdef has_dpg_contextmanager(self) -> bool:",
            f"\t\treturn {self.has_dpg_contextmanager}"
        ]

        # ------------------------------------------------------- 03.04
        # make property allow_children
        if self.name in ['BXAxis', 'BYAxis']:
            assert self.has_dpg_contextmanager, \
                "should be true as we intend to limit it"
            _lines += [
                "",
                "\t@property",
                "\tdef allow_children(self) -> bool:",
                f"\t\t# For class `{self.name}` we block adding children as ",
                f"\t\t# this can be addressed with special properties or is not needed",
                f"\t\treturn False",
            ]

        # ------------------------------------------------------- 03.05
        # add build method
        _params = {} if self.parameters is None else self.parameters
        _lines += [
            "",
            "\tdef build(self) -> t.Union[int, str]:",
            f"\t\t_ret = dpg.{'add_' if self.has_dpg_contextmanager else ''}"
            f"{self.method.__name__}(",
            f"\t\t\t**self.internal.dpg_kwargs,",
            *[f"\t\t\t{_k}={_v}," for _k, _v in _params.items()],
            *[
                f"\t\t\t{_pd.name}={_pd.dpg_value},"
                for _pd in _param_defs
            ],
            f"\t\t)",
            f"\t\t",
            f"\t\treturn _ret",
        ]

        # ------------------------------------------------------- 03.06
        # add methods for callback params
        for _pd in _param_defs:
            if not _pd.is_callback:
                continue
            _lines += [
                "",
                f"\tdef {_pd.name}_fn("
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
                f"\t\tif self.{_pd.name} is None:",
                f"\t\t\treturn None",
                f"\t\telse:",
                f"\t\t\treturn self.{_pd.name}.fn("
                f"\n\t\t\t\tsender=self, app_data=app_data, user_data=user_data"
                f"\n\t\t\t)",
            ]

        # ------------------------------------------------------- 04
        # replace \t to 4 spaces
        _lines = [_.replace("\t", "    ") for _ in _lines]
        return _lines

    def get_param_defs(self) -> t.List[WidgetBuildParamDef]:

        # initial things
        _signature = inspect.signature(self.method)
        _docs_dict = self.get_docs()

        # to return container
        _ret = []

        # ignore params
        _ignore_params = ['id', 'parent', 'before', 'tag', 'kwargs']

        # ignore axis param if needed
        if self.method == dpg.plot_axis:
            _ignore_params.append('axis')

        # loop over all params
        for _param in _signature.parameters.values():

            # get name
            _param_name = _param.name

            # some things are ignored
            if _param_name in _ignore_params:
                continue

            # param type
            _param_type = f"{_param.annotation}".replace(
                'typing', 't'
            ).replace(
                "<class '", ""
            ).replace(
                "'>", ""
            ).replace(
                "t.Callable", "Callback"
            )

            # is callback
            _is_callback = _param_type.find("Callback") != -1

            # param value
            _param_value = _param.default

            # param dpg value
            _param_dpg_value = f"self.{_param_name}"

            # param doc
            _param_doc = _docs_dict[_param_name]

            # if param is enum we will get _enum_def
            _enum_def = None
            if _param_name not in ['source']:
                _enum_def = fetch_enum_def_from_param_doc(
                    method=self.method, param_name=_param_name, param_doc=_param_doc
                )

            # some replacements
            if _param_name == "source":
                _param_type = "t.Optional[Widget]"
                _param_value = "None"
                _param_dpg_value = "getattr(self.source, 'dpg_id', 0)"
            if _param_name == "user_data":
                _param_type = "t.Union[Widget, t.List[Widget]]"
                _param_value = "None"
            if _param_name == "on_enter":
                _param_name = "if_entered"
                _param_dpg_value = "self.on_enter"
            if _is_callback:
                _param_dpg_value += "_fn"
            if _enum_def is not None:
                _param_type = _enum_def.enum_name
                _param_value = _enum_def.get_enum_instance_str_from_value(
                    value=_param_value
                )
                _param_dpg_value = f"self.{_param_name}.value"

            # update param value if not empty
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if _param_value != inspect._empty:
                if _param_value in ["", "$$DPG_PAYLOAD"] or \
                        str(_param_value).startswith('%'):
                    _param_value = f"'{_param_value}'"
                elif isinstance(_param_value, (list, tuple)):
                    if isinstance(_param_value, tuple):
                        _param_value = list(_param_value)
                    _param_value = f"\\\n\t\tdataclasses.field(" \
                                   f"default_factory=lambda: {_param_value})"

            # append
            _ret.append(
                WidgetBuildParamDef(
                    name=_param_name,
                    type=_param_type,
                    value=_param_value,
                    dpg_value=_param_dpg_value,
                    doc=_param_doc,
                )
            )

        # final return
        return _ret


class EnumDef(NamedTuple):
    dpg_enum_prefix: str
    dpg_enum_values: t.List[str]

    @property
    def enum_name(self) -> str:
        return "En" + self.dpg_enum_prefix.replace("mv", "").replace("_", "")

    def __eq__(self, other):
        return self.dpg_enum_prefix == other.dpg_enum_prefix and \
               self.dpg_enum_values == other.dpg_enum_values

    def code(self) -> t.List[str]:

        # add header
        _lines = [
            "",
            "",
            f"class {self.enum_name}(m.FrozenEnum, enum.Enum):",
            "",
            # "\tDEFAULT = 0",
        ]

        # add enum fields
        _dpg_prefix = self.dpg_enum_prefix
        for _dpg_val_str in self.dpg_enum_values:

            # dpg value
            _dpg_val = getattr(dpg, _dpg_val_str)

            # replace None
            _enum_val_str = self.get_dpg_val_to_enum_val(_dpg_val_str)

            # append line
            _lines.append(
                f"\t{_enum_val_str} = dpg.{_dpg_val_str}  # {_dpg_val}")

        # add yaml tag
        _lines += [
            "",
            "\t@classmethod",
            "\tdef yaml_tag(cls) -> str:",
            f"\t\treturn \"!gui_{self.enum_name}\"",
        ]

        # replace \t to 4 spaces
        _lines = [_.replace("\t", "    ") for _ in _lines]
        return _lines

    def get_dpg_val_to_enum_val(self, dpg_val: str) -> str:
        _ret = dpg_val.replace(self.dpg_enum_prefix, "")
        if _ret == 'None':
            _ret = 'NONE'
        return _ret

    def get_enum_instance_str_from_value(self, value: int) -> str:

        # add enum fields
        _selected_dpg_v = None
        _dpg_values = []
        for _dpg_v in self.dpg_enum_values:

            # dpg value
            _dpg_val = getattr(dpg, _dpg_v)
            _dpg_values.append(_dpg_val)

            # if matches set
            if _dpg_val == value:
                _selected_dpg_v = _dpg_v

        # if None raise error
        if _selected_dpg_v is None:
            raise Exception(
                f"Cannot fetch enum instance str for enum {self.enum_name}. "
                f"The value {value} is not one of "
                f"{_dpg_values} for enum fields {self.dpg_enum_values}"
            )

        # return
        _selected_dpg_v = self.get_dpg_val_to_enum_val(_selected_dpg_v)
        return f"{self.enum_name}.{_selected_dpg_v}"


def fetch_enum_def_from_param_doc(
    method: t.Callable, param_name: str, param_doc: str
) -> t.Optional[EnumDef]:
    """
    If we detect that widget param doc can be a enum field we return tuple i.e.
    (possible enum name, and the enum fields) else we return None ...
    """
    # ----------------------------------------------------------------- 01
    # enum starts with `mv` then letters and one underscore
    # multiple underscores can follow
    _enum_val_s = re.findall(" mv[a-zA-Z0-9]+_[*_a-zA-Z0-9]+", param_doc)

    # ----------------------------------------------------------------- 02
    # param name has star
    _param_name_has_star = False
    if len(_enum_val_s) == 1:
        _param_name_has_star = _enum_val_s[0].find("*") != -1

    # ----------------------------------------------------------------- 03
    # is param dog_id type
    _is_dpg_id = param_doc.find("Union[int, str]") != -1

    # ----------------------------------------------------------------- 04
    # if dpg field and no enum values raise error if cannot be handled
    if _is_dpg_id:
        if not bool(_enum_val_s):
            raise Exception(
                f"There are no enum fields detected for "
                f"\n\tmethod: {method} "
                f"\n\tparameter: {param_name} "
                f"\n\tdoc: {param_doc}"
            )

    # ----------------------------------------------------------------- 05
    # there is no enum for this then return
    if not bool(_enum_val_s) and not _is_dpg_id:
        return None

    # ----------------------------------------------------------------- 06
    # remove extra space
    _enum_val_s = [_.strip() for _ in _enum_val_s]

    # ----------------------------------------------------------------- 07
    # figure out enum name and values if needed
    # ----------------------------------------------------------------- 07.01
    if _param_name_has_star:
        _enum_prefix = _enum_val_s[0].replace("*", "")
        _enum_val_s = []
        for _item in dir(dpg):
            if _item.startswith(_enum_prefix):
                _enum_val_s.append(_item)
    # ----------------------------------------------------------------- 07.02
    # else figure out name from enum values
    else:
        _l_of_l = [list(_) for _ in _enum_val_s]
        _enum_prefix = ""
        for _ in zip(*_l_of_l):
            _break = all(__ == _[0] for __ in _)
            if not _break:
                break
            _enum_prefix += _[0]

    # ----------------------------------------------------------------- 08
    # update enum name further if needed
    # Note this section is hardcoded and any fixes can be done here

    # ----------------------------------------------------------------- 09
    # build enum num def and see if proper duplicate
    _enum_def = EnumDef(
        dpg_enum_prefix=_enum_prefix, dpg_enum_values=_enum_val_s)
    if _enum_def.enum_name not in _NEEDED_ENUMS.keys():
        _NEEDED_ENUMS[_enum_def.enum_name] = _enum_def
    else:
        _other_enum_def = _NEEDED_ENUMS[_enum_def.enum_name]
        if _enum_def != _other_enum_def:
            raise Exception(
                f"Inspect enum {_enum_def.enum_name} and update it above so "
                f"that every enum is unique"
            )

    # ----------------------------------------------------------------- 10
    # return
    return _enum_def


def fetch_widget_defs() -> t.List[WidgetDef]:
    """
    Right now hardcoded but we will automate this later
    """
    return [
        WidgetDef(method=dpg.table, ),
        WidgetDef(method=dpg.add_table_column, ),
        WidgetDef(method=dpg.table_row, ),
        WidgetDef(method=dpg.table_cell, ),
        WidgetDef(method=dpg.add_tab_button, ),
        WidgetDef(method=dpg.tab_bar, ),
        WidgetDef(method=dpg.tab, ),
        WidgetDef(method=dpg.add_button, ),
        WidgetDef(method=dpg.add_combo, ),
        WidgetDef(method=dpg.add_separator, ),
        WidgetDef(method=dpg.child_window, ),
        WidgetDef(method=dpg.window, ),
        WidgetDef(method=dpg.add_text, ),
        WidgetDef(method=dpg.collapsing_header, ),
        WidgetDef(method=dpg.group, ),
        WidgetDef(method=dpg.add_plot_legend, ),
        WidgetDef(method=dpg.plot_axis, parameters={'axis': 'dpg.mvXAxis'}, ),
        WidgetDef(method=dpg.plot_axis, parameters={'axis': 'dpg.mvYAxis'}, ),
        WidgetDef(method=dpg.subplots, ),
        WidgetDef(method=dpg.add_simple_plot, ),
        WidgetDef(method=dpg.plot, ),
        WidgetDef(method=dpg.add_input_intx, ),
        WidgetDef(method=dpg.add_input_int, ),
        WidgetDef(method=dpg.add_progress_bar, ),
        WidgetDef(method=dpg.add_checkbox, ),
        WidgetDef(method=dpg.add_colormap_scale, ),
        WidgetDef(method=dpg.add_drag_line, ),
        WidgetDef(method=dpg.add_drag_point, ),
        WidgetDef(method=dpg.add_slider_int, ),
        WidgetDef(method=dpg.add_slider_intx, ),
        WidgetDef(method=dpg.add_slider_float, ),
        WidgetDef(method=dpg.add_slider_floatx, ),
        WidgetDef(method=dpg.add_3d_slider, ),
        WidgetDef(method=dpg.tooltip, ),
        # todo: tackle this once below enums are resolved
        #   + mvThemeCat_
        #   + mvThemeCol_
        #   + mvPlotCol_
        #   + mvNodeCol_
        #   + mvStyleVar_
        #   + mvPlotStyleVar_
        #   + mvNodeStyleVar_
        #   + mvFontRangeHint_
        # WidgetDef(
        #     method=dpg.theme,
        # ),
        # WidgetDef(
        #     method=dpg.theme_component,
        # ),
        # WidgetDef(
        #     method=dpg.add_theme_color,
        #     widget_name="ThemeColor",
        #     enum_fields={
        #         'value': 'Color.BLACK',
        #         'target': 'ThemeCol.DEFAULT',
        #         'category': 'ThemeCat.DEFAULT',
        #     },
        # ),
        # WidgetDef(
        #     method=dpg.add_theme_style,
        #     widget_name="ThemeStyle",
        #     enum_fields={
        #         'target': 'ThemeCol.DEFAULT',
        #         'category': 'ThemeCat.DEFAULT',
        #     },
        # ),
    ]


def create_auto_code_for_widgets_and_enums():
    # ---------------------------------------------------- 01
    _script_file = pathlib.Path(__file__)
    _script_file = _script_file.relative_to(
        _script_file.parent.parent.parent.parent).as_posix()
    _header = f'''"""
********************************************************************************
This code is auto-generated using script:
    {_script_file}
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dataclasses
import dearpygui.dearpygui as dpg
import typing as t
import enum

from ... import marshalling as m
from .. import Widget, Callback
'''

    # ---------------------------------------------------- 02
    _widget_code_lines = []
    for _widget in fetch_widget_defs():
        _widget_code_lines += _widget.code()
    _widget_code = "\n".join(_widget_code_lines + [""])

    # ---------------------------------------------------- 03
    # create enum code
    _enum_code_lines = []
    for _enum_def in _NEEDED_ENUMS.values():
        _enum_code_lines += _enum_def.code()
    _enum_code = "\n".join(_enum_code_lines + [""])

    # ---------------------------------------------------- 04
    _output_file = pathlib.Path("../widget/auto.py")
    _output_file.write_text(_header + _enum_code + _widget_code)


if __name__ == '__main__':
    create_auto_code_for_widgets_and_enums()
