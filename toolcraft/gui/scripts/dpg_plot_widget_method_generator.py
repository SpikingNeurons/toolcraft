import inspect
import pathlib
import textwrap
import dearpygui.dearpygui as dpg

_output = pathlib.Path("out.py")


def get_methods_related_to_plot():
    _ret = []
    for _name in dir(dpg):

        _method = getattr(dpg, _name)

        if not callable(_method):
            continue

        if _name in [
            'plot', 'subplots', 'add_plot',
            'add_plot_axis', 'add_plot_legend', 'add_simple_plot',
            'add_subplots',
        ]:
            continue

        if _method.__doc__ is None:
            if _name in ['mutex', 'popup']:
                continue
            raise Exception(f"no doc for {_name}")

        if _method.__doc__.find("plot") == -1:
            continue

        if '__wrapped__' in dir(_method):
            raise Exception(f"method {_name} has as decorator")

        if 'parent' not in inspect.signature(_method).parameters.keys():
            continue

        _ret.append(_method)

    return _ret


_lines = [
    "import dearpygui.dearpygui as dpg",
    "import dataclasses",
    "import typing as t",
    "import Widget",
    "import Callback",
    "import numpy as np",
    "",
    "PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]",
    "",
    "",
    "@dataclasses.dataclass(frozen=True)",
    "class ___:",
    "",
]

for _method in get_methods_related_to_plot():
    # get signature
    _signature = inspect.signature(_method)

    # make _docs_dict
    _main_doc = []
    _kwarg_doc = ["", "\t\tArgs:"]
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
            if _k in ['id', 'parent']:
                continue
            if _v == '':
                _v = '...'
            _kwarg_doc += [
                f"\t\t\t{_k}:"
            ]
            for _s in textwrap.wrap(_v, 60):
                _kwarg_doc.append(f"\t\t\t  {_s}")
        else:
            for _s in textwrap.wrap(_l_strip, 70):
                _main_doc.append(f"\t\t{_s}")
    _kwarg_doc += [
        "\t\t\ty_axis_dim:",
        "\t\t\t  ...",
        "",
        "\t\tReturns:",
        "\t\t\tint",
        ""
    ]

    # method start
    _lines += [
        f"\tdef {_method.__name__}(",
        f"\t\tself, *,",
    ]

    # method kwargs
    _callback_params = []
    _all_params_to_consider = []
    for _param in _signature.parameters.values():
        _param_name = _param.name
        if _param_name in ['id', "parent"]:
            continue
        _param_type = f"{_param.annotation}".replace(
            'typing', 't'
        ).replace(
            "<class '", ""
        ).replace(
            "'>", ""
        ).replace(
            "t.Callable", "t.Optional[Callback]"
        )
        _all_params_to_consider.append(_param_name)
        if _param_type.find("Callback") != -1:
            _callback_params.append(_param_name)
        _param_value = _param.default
        if _param_name in ["source", "before"]:
            _param_type = "t.Optional[Widget]"
            _param_value = "None"
        _parm_str = f"\t\t{_param_name}: {_param_type}"
        # noinspection PyUnresolvedReferences,PyProtectedMember
        if _param_value == inspect._empty:
            _parm_str = _parm_str.replace("t.List[float]", "PLOT_DATA_TYPE")
            _parm_str += ","
        else:
            if _param_value in ["", "$$DPG_PAYLOAD"] or \
                    str(_param_value).startswith('%'):
                _parm_str += f" = '{_param_value}',"
            else:
                _parm_str += f" = {_param_value},"

        # for _s in textwrap.wrap(_docs_dict[_param_name], 70):
        #     _lines.append(f"\t# {_s}")
        _lines.append(_parm_str)

    # method end
    _lines += [
        "\t\ty_axis_dim: int = 1,",
        "\t) -> int:",
        '\t\t"""',
        "\t\tRefer:",
        f"\t\t>>> dpg.{_method.__name__}",
        "",
    ] + _main_doc + _kwarg_doc + ['\t\t"""', ""]

    # call method code
    _kwargs = []
    for _param in _all_params_to_consider:
        _assign_str = f"\t\t\t{_param}={_param},"
        if _param in ["source", "before"]:
            _assign_str = \
                f"\t\t\t{_param}=0 if {_param} is None else " \
                f"{_param}.dpg_id,"
        if _param in _callback_params:
            _assign_str = f"\t\t\t{_param}=None " \
                          f"if {_param} is None else {_param}.fn,"
        _kwargs.append(_assign_str)
    _lines += [
        f"\t\t_y_axis = self.get_y_axis(axis_dim=y_axis_dim)",
        f"\t\t",
        f"\t\t_dpg_id = dpg.{_method.__name__}(",
        f"\t\t\tparent=_y_axis.dpg_id,",
        *_kwargs,
        f"\t\t)",
        f"\t\t",
        f"\t\treturn _dpg_id",
        f"\t\t",
    ]


# replace \t to 4 spaces
_lines = [_.replace("\t", "    ") for _ in _lines]

# write to disk
_result = "\n".join(_lines + [""])
print(_result)
_output.write_text(_result)
