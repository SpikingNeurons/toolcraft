import inspect
import pathlib
import textwrap
import typing as t
import dearpygui.dearpygui as dpg

_script_file = pathlib.Path(__file__)
_script_file = _script_file.relative_to(
    _script_file.parent.parent.parent.parent).as_posix()


def get_methods_related_to_plot():
    _ret = []
    for _name in dir(dpg):

        _method = getattr(dpg, _name)

        if not callable(_method):
            continue

        if _method in [
            dpg.plot, dpg.subplots, dpg.add_plot,
            dpg.add_plot_axis, dpg.add_plot_legend, dpg.add_simple_plot,
            dpg.add_subplots, dpg.deprecated,
            dpg.fit_axis_data, dpg.plot_axis,

            # todo later not handled methods
            dpg.get_plot_mouse_pos, dpg.get_plot_query_area, dpg.is_plot_queried,
            dpg.show_implot_demo,
        ]:
            continue

        if _method.__doc__ is None:
            if _method in [dpg.mutex, dpg.popup]:
                continue
            raise Exception(f"no doc for `{_name}`")

        if _method.__doc__.find("plot") == -1:
            continue

        if '__wrapped__' in dir(_method):
            raise Exception(f"method `{_name}` has a decorator")

        if 'parent' not in inspect.signature(_method).parameters.keys():
            raise Exception(f"method `{_name}` ")

        _ret.append(_method)

    return _ret


def fetch_kwarg_doc_dict(method) -> t.Dict[str, str]:
    _ret = {}
    _main_doc = []
    _track = False
    for _l in method.__doc__.split("\n"):
        _l_strip = _l.strip()
        if _l_strip in ['Returns:', 'Yields:']:
            break
        if _l_strip == 'Args:':
            _track = True
            continue
        if _track:
            _k = _l_strip.split(':')[0].split(' ')[0]
            _v = _l_strip.split(':')[1].strip()
            if _k in ['id', 'parent', 'tag', ]:
                continue
            if _v == '':
                _v = '...'
            _ret[_k] = _v
            # for _s in textwrap.wrap(_v, 60):
            #     _kwarg_doc.append(f"\t\t\t  {_s}")
        else:
            _main_doc.append(f"\t\t{_l_strip}")
            # for _s in textwrap.wrap(_l_strip, 70):
            #     _main_doc.append(f"\t\t{_s}")
    _ret['main_doc'] = "\n".join(_main_doc)
    return _ret


def main():
    # ------------------------------------------------------- 01
    # check if tags are present in file
    _dst_file = pathlib.Path(__file__).parent.parent / "widget" / "core.py"
    _start_tag = "# pk; start tag >>>"
    _end_tag = "# pk; end tag >>>"
    _dst_file_txt = _dst_file.read_text()
    if _dst_file_txt.find(_start_tag) == -1:
        raise Exception(
            f"Cannot find start tag `{_start_tag}` in file {_dst_file}"
        )
    if _dst_file_txt.find(_end_tag) == -1:
        raise Exception(
            f"Cannot find end tag `{_end_tag}` in file {_dst_file}"
        )
    # remove anything in between those tags
    _start_tag_index = -1
    _end_tag_index = -1
    _dst_file_lines = _dst_file_txt.split("\n")
    for _i, _ in enumerate(_dst_file_lines):
        if _.find(_start_tag) != -1:
            _start_tag_index = _i
        if _.find(_end_tag) != -1:
            _end_tag_index = _i
    _dst_file_lines_start = _dst_file_lines[:_start_tag_index+1]
    _dst_file_lines_end = _dst_file_lines[_end_tag_index:]

    # ------------------------------------------------------- 02
    # get eligible methods and loop over
    _code_lines = []
    for _method in get_methods_related_to_plot():
        # --------------------------------------------------- 02.01
        # get docs
        _docs_dict = fetch_kwarg_doc_dict(_method)
        # --------------------------------------------------- 02.02
        # get signature
        _signature = inspect.signature(_method)
        # --------------------------------------------------- 02.03
        # method start
        _code_lines += [
            f"\tdef {_method.__name__}(",
            f"\t\tself, *,",
        ]
        # --------------------------------------------------- 02.04
        _param_call_lines = []
        _param_doc_lines = []
        _param_dpg_call_lines = []
        _callback_params = []
        # loop over params
        for _param in _signature.parameters.values():
            # ----------------------------------------------- 02.04.01
            # get param name and ignore some params
            _param_name = _param.name
            if _param_name in ['id', 'parent', 'tag', 'kwargs', ]:
                continue
            # get param type
            _param_type = f"{_param.annotation}".replace(
                'typing', 't'
            ).replace(
                "<class '", ""
            ).replace(
                "'>", ""
            ).replace(
                "t.Callable", "t.Optional[Callback]"
            )
            # get param value
            _param_value = _param.default
            # ----------------------------------------------- 02.04.02
            # detect if param is a callback type
            if _param_type.find("Callback") != -1:
                _callback_params.append(_param_name)
            # ----------------------------------------------- 02.04.03
            # update things
            # here you can do any customizations that needs to be hardcoded
            if _param_name in ["source", "before"]:
                _param_type = "t.Optional[Widget]"
                _param_value = "None"
            if _param_value in ["", "$$DPG_PAYLOAD"] or \
                    str(_param_value).startswith('%'):
                _param_value = f"'{_param_value}'"
            elif isinstance(_param_value, (list, tuple)):
                if isinstance(_param_value, tuple):
                    _param_value = list(_param_value)
                _param_value = f"dataclasses.field(" \
                               f"default_factory=lambda: {_param_value})"
            # ----------------------------------------------- 02.04.04
            # append _param_call_lines
            _param_call_str = f"\t\t{_param_name}: {_param_type}"
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if _param_value == inspect._empty:
                _param_call_str += ","
            else:
                _param_call_str += f" = {_param_value},"
            _param_call_lines.append(_param_call_str)
            # ----------------------------------------------- 02.04.05
            # append _param_doc_lines
            _param_doc_lines.append(f"\t\t\t{_param_name}: {_param_type}")
            _param_doc_lines.append(f"\t\t\t\t{_docs_dict[_param_name]}")
            # ----------------------------------------------- 02.04.06
            # append _param_dpg_call_str
            _param_dpg_call_str = f"\t\t\t{_param_name}="
            if _param_name in ["source", "before"]:
                _param_dpg_call_str += f"getattr({_param_name}, 'dpg_id', 0),"
            elif _param_name in _callback_params:
                _param_dpg_call_str += f"getattr({_param_name}, 'fn', None),"
            else:
                _param_dpg_call_str += f"{_param_name},"
            _param_dpg_call_lines.append(_param_dpg_call_str)

        # --------------------------------------------------- 02.05
        _code_lines += _param_call_lines
        _code_lines += [
            "\t) -> t.Union[int, str]:",
            '\t\t"""',
            "\t\tRefer:",
            f"\t\t>>> dpg.{_method.__name__}",
            "",
            f"\t\t(autogenerated by: {_script_file})",
            "",
        ]
        # _code_lines += _docs_dict['main_doc']
        _code_lines += ["\t\tArgs:"]
        _code_lines += _param_doc_lines
        _code_lines += [
            "",
            "\t\tReturns:",
            "\t\t\tt.Union[int, str]",
            "",
            '\t\t"""',
            "",
        ]
        _code_lines += [
            f"\t\t_dpg_id = dpg.{_method.__name__}(",
            f"\t\t\tparent=self.dpg_id,",
        ]
        _code_lines += _param_dpg_call_lines
        _code_lines += [
            f"\t\t)",
            f"\t\t",
            f"\t\treturn _dpg_id",
            f"\t\t",
        ]

    # ------------------------------------------------------- 02
    # replace \t to 4 spaces
    _code_lines = [_.replace("\t", "    ") for _ in _code_lines]
    # write to disk
    _result = "\n".join(
         _dst_file_lines_start + _code_lines + _dst_file_lines_end
    )
    print(_result)

    _dst_file.write_text(_result)


if __name__ == '__main__':
    main()
