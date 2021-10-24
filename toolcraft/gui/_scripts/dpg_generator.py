import inspect
import pathlib
import dataclasses
import dearpygui
import dearpygui.dearpygui as dpg
from typing import NamedTuple
import typing as t
import re
import datetime

_WRAP_TEXT_WIDTH = 70
_NEEDED_ENUMS = {}


class WidgetBuildParamDef(NamedTuple):
    name: str
    dpg_name: str
    type: str
    value: str
    dpg_value: str
    doc: str

    @property
    def is_callback(self) -> bool:
        return self.type.find("Callback") != -1


@dataclasses.dataclass(frozen=True)
class WidgetDef:
    method: t.Callable
    is_container: bool

    # used to generate multiple widgets based on parameters supplied that will be
    # hardcoded in build method
    parameters: t.Dict[str, str] = None

    @property
    def call_prefix(self) -> str:

        _call_prefix = \
            f"internal_dpg.add_{self.method.__name__}" \
            if self.is_container else f"internal_dpg.{self.method.__name__}"

        if self.method == dpg.plot_axis:
            _call_prefix = f"internal_dpg.add_{self.method.__name__}"

        return _call_prefix

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
        if self.method == dpg.add_2d_histogram_series:
            return "HistogramSeries2D"

        # ------------------------------------------------------- 04
        # default name generation
        _name = self.method.__name__.replace("add_", "")
        _name = _name.title().replace("_", "")
        _name = _name.replace("Intx", "IntX").replace("Floatx", "FloatX")

        # ------------------------------------------------------- 05
        return _name

    def __post_init__(self):
        # make checks
        self.checks()

    def checks(self):
        # ---------------------------------------------------------- 01
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
        print(f"getting code for `dpg.{self.method.__name__}`")
        # ------------------------------------------------------- 01
        # initial things
        self.checks()
        # get docs dict
        _docs_dict = self.get_docs()
        _param_defs = self.get_param_defs()

        # ------------------------------------------------------- 02
        # is widget or container
        _class_name = "Widget"
        if self.is_container:
            _class_name = "Container"

        # ------------------------------------------------------- 03
        # make code lines
        # ------------------------------------------------------- 03.01
        # code header
        _lines = [
            "",
            "",
            "@dataclasses.dataclass",
            f"class {self.name}({_class_name}):",
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
        # add build method
        _params = {} if self.parameters is None else self.parameters
        _lines += [
            "\tdef build(self) -> t.Union[int, str]:",
            f"\t\t_ret = {self.call_prefix}(",
            f"\t\t\t**self.internal.dpg_kwargs,",
            *[f"\t\t\t{_k}={_v}," for _k, _v in _params.items()],
            *[
                f"\t\t\t{_pd.dpg_name}={_pd.dpg_value},"
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

    def allowed_methods_in_container(self) -> t.List[t.Callable]:
        if not self.is_container:
            raise Exception("Should be used with widgets that are containers")

        _ret = []

        for _fn in fetch_fns():
            ...

    def get_param_defs(self) -> t.List[WidgetBuildParamDef]:

        # initial things
        _signature = inspect.signature(self.method)
        _docs_dict = self.get_docs()

        # to return container
        _ret = []

        # ignore params
        _ignore_params = ['id', 'parent', 'before', 'tag', 'kwargs']

        # ignore axis param if needed
        if self.method in [dpg.plot_axis, dpg.add_plot_axis]:
            _ignore_params.append('axis')

        # loop over all params
        for _param in _signature.parameters.values():

            # get name
            _param_name = _param.name
            _param_dpg_name = _param.name

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
                _param_dpg_name = "on_enter"
                _param_dpg_value = "self.if_entered"
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
                if _param_value in [
                    "", "$$DPG_PAYLOAD", ".", "general",
                ] or str(_param_value).startswith('%'):
                    _param_value = f"'{_param_value}'"
                elif isinstance(_param_value, list):
                    _param_value = f"dataclasses.field(" \
                                   f"default_factory=lambda: {_param_value})"
                elif isinstance(_param_value, dict):
                    _param_value = f"dataclasses.field(" \
                                   f"default_factory=lambda: {_param_value})"

            # append
            _ret.append(
                WidgetBuildParamDef(
                    name=_param_name,
                    dpg_name=_param_dpg_name,
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
            f"class {self.enum_name}(enum.Enum):",
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


def fetch_fns() -> t.List[t.Callable]:

    _ret = []

    # loop over dpg module
    for _fn_name in dir(dpg):

        # skip if not function
        _fn = getattr(dpg, _fn_name)
        if not inspect.isfunction(_fn):
            continue

        # fn details
        _fn_src = inspect.getsource(_fn)
        _deprecated_dec_present = _fn_src.find("@deprecated") != -1

        # skip if deprecated
        if _deprecated_dec_present:
            continue

        # skip this one as it gets detected as container Widget
        if _fn == dpg.contextmanager:
            continue

        # skip this too
        if _fn == dpg.deprecated:
            continue

        # append
        _ret.append(_fn)

    return _ret


def fetch_container_widget_defs() -> t.Generator[WidgetDef, None, None]:
    """
    Yields only widgets that are container
    """
    # possible widgets
    _possible_widgets = []
    _skip_fn_names = []

    # loop over dpg module
    for _fn in fetch_fns():

        # fn details
        _fn_src = inspect.getsource(_fn)
        _context_manager_dec_present = _fn_src.find("@contextmanager") != -1

        # skip if not _context_manager_dec_present
        if not _context_manager_dec_present:
            continue

        # assert check if add_ present
        assert not _fn.__name__.startswith("add_"), \
            f"was not expecting to start with add_ >> {_fn}"

        # skip some fns that can be container widgets
        if _fn in [
            # todo: the doc is not available for all kwargs so keep this pending
            # Note that this si simple it pops out any widget and adds it to Window
            dpg.popup,

            # todo: dont know what to do, also there is no corresponding add_mutex
            dpg.mutex,
        ]:
            continue

        # make sure that there is corresponding add method
        _add_fn_name = f"add_{_fn.__name__}"
        if _add_fn_name not in dir(dpg):
            raise Exception(
                f"Cannot find corresponding add_* fn: {_add_fn_name}"
            )

        # special parametrization for `dpg.plot_axis`
        if _fn == dpg.plot_axis:
            # Note we disable the container for plot_axis
            yield WidgetDef(
                method=_fn, is_container=False, parameters={'axis': 'dpg.mvXAxis'}, )
            yield WidgetDef(
                method=_fn, is_container=False, parameters={'axis': 'dpg.mvYAxis'}, )
        # other special treatments
        # elif _fn == ...:
        #     ...
        # else general case
        else:
            yield WidgetDef(
                method=_fn, is_container=_context_manager_dec_present, )


def fetch_widget_defs() -> t.Generator[WidgetDef, None, None]:
    """
    Right now hardcoded but we will automate this later
    """
    # ----------------------------------------------------------- 01
    # first yield container widgets and also store it for future reference
    _container_widgets = []
    for _ in fetch_container_widget_defs():
        _container_widgets.append(_)
        yield _

    # ----------------------------------------------------------- 02
    # decide methods to skip
    # ----------------------------------------------------------- 02.01
    # skip method corresponding to _container_widgets
    _skip_methods = []
    for _container_widget in _container_widgets:
        _skip_methods.append(_container_widget.method)
        _skip_methods.append(getattr(dpg, f"add_{_container_widget.method.__name__}"))
    # ----------------------------------------------------------- 02.02
    # some more methods
    _skip_methods.extend(
        [
            # not required
            dpg.add_alias, dpg.remove_alias, dpg.does_alias_exist,
            dpg.get_alias_id, dpg.get_aliases, dpg.set_item_alias,
            dpg.does_item_exist,
            dpg.generate_uuid, dpg.get_all_items,
            dpg.get_dearpygui_version, dpg.get_item_alias, dpg.get_values,

            # handled methods by Widget
            dpg.delete_item,  # Widget.delete
            dpg.enable_item,  # Widget.enable
            dpg.disable_item,  # Widget.disable
            dpg.focus_item,  # Widget.focus
            dpg.get_value,  # Widget.get_value
            dpg.set_value,  # Widget.set_value
            dpg.set_x_scroll,  # Widget.set_x_scroll
            dpg.get_x_scroll,  # Widget.get_x_scroll
            dpg.get_x_scroll_max,  # Widget.get_x_scroll_max
            dpg.set_y_scroll,  # Widget.set_y_scroll
            dpg.get_y_scroll,  # Widget.get_y_scroll
            dpg.get_y_scroll_max,  # Widget.get_y_scroll_max
            dpg.hide_item,  # Widget.hide
            dpg.show_item,  # Widget.show
            dpg.move_item,  # Widget.move
            dpg.move_item_up,  # Widget.move_up
            dpg.move_item_down,  # Widget.move_down
            dpg.reset_pos,  # Widget.reset_pos
            dpg.show_item_debug,  # Widget.show_debug
            dpg.unstage,  # Widget.unstage

            # handled methods by Table
            dpg.highlight_table_cell,  # Table.highlight_cell
            dpg.highlight_table_column,  # Table.highlight_column
            dpg.highlight_table_row,  # Table.highlight_row
            dpg.unhighlight_table_cell,  # Table.unhighlight_cell
            dpg.unhighlight_table_column,  # Table.unhighlight_column
            dpg.unhighlight_table_row,  # Table.unhighlight_row
            dpg.is_table_cell_highlight,  # Table.is_cell_highlight
            dpg.is_table_column_highlight,  # Table.is_column_highlight
            dpg.is_table_row_highlight,  # Table.is_row_highlight
            dpg.set_table_row_color,  # Table.set_row_color
            dpg.unset_table_row_color,  # Table.unset_row_color

            # handled methods by Plot
            dpg.fit_axis_data,  # XAxis.fit_data, YAxis.fit_data,
            dpg.get_axis_limits,  # XAxis.get_limits, YAxis.get_limits,
            dpg.get_plot_query_area,  # Plot.get_query_area
            dpg.is_plot_queried,  # Plot.is_queried
            dpg.reset_axis_ticks,  # XAxis.reset_ticks, YAxis.reset_ticks
            dpg.set_axis_limits,  # XAxis.set_limits, YAxis.set_limits
            dpg.set_axis_limits_auto,  # XAxis.set_limits_auto, YAxis.set_limits_auto
            dpg.set_axis_ticks,  # XAxis.set_ticks, YAxis.set_ticks

            # handled methods by Widget.__setattr__
            dpg.set_item_callback,
            dpg.set_item_drag_callback,
            dpg.set_item_drop_callback,
            dpg.set_item_height,
            dpg.set_item_indent,
            dpg.set_item_label,
            dpg.set_item_payload_type,
            dpg.set_item_pos,
            dpg.set_item_source,
            dpg.set_item_track_offset,
            dpg.set_item_user_data,
            dpg.set_item_width,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,
            dpg.set_item_callback,

            # handled state commands
            dpg.get_item_state,  # Widget.dpg_state property
            dpg.is_item_hovered,
            dpg.is_item_active,
            dpg.is_item_focused,
            dpg.is_item_clicked,
            dpg.is_item_left_clicked,
            dpg.is_item_right_clicked,
            dpg.is_item_middle_clicked,
            dpg.is_item_visible,
            dpg.is_item_edited,
            dpg.is_item_activated,
            dpg.is_item_deactivated,
            dpg.is_item_deactivated_after_edit,
            dpg.is_item_toggled_open,
            dpg.is_item_ok,
            dpg.get_item_pos,
            dpg.get_available_content_region,
            dpg.get_item_rect_size,
            dpg.get_item_rect_min,
            dpg.get_item_rect_max,

            # handled config commands
            dpg.get_item_configuration,  # Widget.dpg_config property
            dpg.is_item_shown,
            dpg.is_item_enabled,
            dpg.is_item_tracked,
            dpg.is_item_search_delayed,
            dpg.get_item_label,
            dpg.get_item_filter_key,
            dpg.get_item_indent,
            dpg.get_item_track_offset,
            dpg.get_item_width,
            dpg.get_item_height,
            dpg.get_item_callback,
            dpg.get_item_drag_callback,
            dpg.get_item_drop_callback,
            dpg.get_item_user_data,
            dpg.get_item_source,

            # handled info commands
            dpg.get_item_info,  # Widget.dpg_info property
            dpg.get_item_slot,
            dpg.is_item_container,
            dpg.get_item_parent,
            dpg.get_item_children,
            dpg.get_item_type,
            dpg.get_item_theme,
            dpg.get_item_font,
            dpg.get_item_disabled_theme,

            # we assume and keep it at Dashboard level i.e. static method
            # assuming there will be only one dashboard instance
            dpg.get_active_window,
            dpg.get_delta_time,
            dpg.get_drawing_mouse_pos,
            dpg.get_frame_count,
            dpg.get_frame_rate,
            dpg.get_global_font_scale,
            dpg.get_item_types,
            dpg.get_mouse_drag_delta,
            dpg.get_mouse_pos,
            dpg.get_plot_mouse_pos,
            dpg.is_dearpygui_running,
            dpg.is_key_down,
            dpg.is_key_pressed,
            dpg.is_key_released,
            dpg.is_mouse_button_clicked,
            dpg.is_mouse_button_double_clicked,
            dpg.is_mouse_button_down,
            dpg.is_mouse_button_dragging,
            dpg.is_mouse_button_released,
            # app configurations
            dpg.get_app_configuration,  # Dashboard.get_app_configuration
            dpg.get_major_version,  # Dashboard.get_app_configuration
            dpg.get_minor_version,  # Dashboard.get_app_configuration
            dpg.get_dearpygui_version,  # Dashboard.get_app_configuration
            dpg.get_total_time,  # Dashboard.get_total_time
            dpg.get_windows,  # Dashboard.get_windows

            # todo: con be supported after having four enums for mvColorEdit_
            dpg.add_color_edit, dpg.add_color_picker,

            # todo: support later when static and dynamic textures are supported
            dpg.add_image, dpg.add_image_button, dpg.add_image_series, dpg.draw_image,

            # todo: support when using node editor
            dpg.node_editor, dpg.add_node_link, dpg.clear_selected_links,
            dpg.clear_selected_nodes, dpg.get_selected_links, dpg.get_selected_nodes,

            # todo: may be these need to be used as Widget methods and not as Widget's
            dpg.bind_colormap, dpg.bind_font, dpg.bind_item_font,
            dpg.bind_item_handler_registry, dpg.bind_item_theme,
            dpg.bind_template_registry, dpg.bind_theme,

            # todo: viewport ... useful to make visual code style docking
            dpg.create_viewport,
            dpg.get_viewport_configuration,
            dpg.get_viewport_clear_color,
            dpg.get_viewport_pos,
            dpg.get_viewport_width,
            dpg.get_viewport_client_width,
            dpg.get_viewport_client_height,
            dpg.get_viewport_height,
            dpg.get_viewport_min_width,
            dpg.get_viewport_max_width,
            dpg.get_viewport_min_height,
            dpg.get_viewport_max_height,
            dpg.get_viewport_title,
            dpg.is_viewport_always_top,
            dpg.is_viewport_resizable,
            dpg.is_viewport_vsync_on,
            dpg.is_viewport_decorated,
            dpg.is_viewport_ok,
            dpg.maximize_viewport,
            dpg.minimize_viewport,
            dpg.set_viewport_always_top,
            dpg.set_viewport_clear_color,
            dpg.set_viewport_decorated,
            dpg.set_viewport_height,
            dpg.set_viewport_large_icon,
            dpg.set_viewport_max_height,
            dpg.set_viewport_max_width,
            dpg.set_viewport_min_height,
            dpg.set_viewport_min_width,
            dpg.set_viewport_pos,
            dpg.set_viewport_resizable,
            dpg.set_viewport_resize_callback,
            dpg.set_viewport_small_icon,
            dpg.set_viewport_title,
            dpg.set_viewport_vsync,
            dpg.set_viewport_width,
            dpg.show_viewport, dpg.toggle_viewport_fullscreen,

            # todo: dpg related
            dpg.create_context, dpg.destroy_context, dpg.empty_container_stack,
            dpg.last_container, dpg.last_item, dpg.setup_dearpygui,
            dpg.last_root,  # is registry or window ... adapt based on that
            dpg.set_item_children, dpg.set_primary_window,
            dpg.show_tool, dpg.show_debug, dpg.show_about, dpg.show_documentation,
            dpg.show_font_manager, dpg.show_item_registry, dpg.show_imgui_demo,
            dpg.show_implot_demo,
            dpg.show_metrics,
            dpg.show_style_editor,
            dpg.start_dearpygui,
            dpg.stop_dearpygui,
            dpg.top_container_stack,

            # todo: dont know what to do
            dpg.configure_app, dpg.configure_item, dpg.configure_viewport,
            dpg.capture_next_item, dpg.get_colormap_color,
            dpg.get_file_dialog_info,  # maybe class method for FileDialog widget
            dpg.load_image, dpg.lock_mutex, dpg.mutex, dpg.unlock_mutex,
            dpg.pop_container_stack, dpg.push_container_stack,
            dpg.popup, dpg.add_char_remap,
            dpg.render_dearpygui_frame, dpg.reorder_items,
            dpg.sample_colormap, dpg.save_init_file,
            dpg.set_global_font_scale, dpg.set_frame_callback, dpg.set_exit_callback,
            dpg.split_frame,
            dpg.track_item, dpg.untrack_item,
        ]
    )

    # ----------------------------------------------------------- 02
    # loop over dpg module for fetching remaining widgets
    for _fn in fetch_fns():

        # ------------------------------------------------------- 02.01
        # skip some functions
        if _fn in _skip_methods:
            continue
        # ------------------------------------------------------- 02.02
        # yield
        yield WidgetDef(method=_fn, is_container=False, )

    # return [
    #     WidgetDef(method=dpg.add_table, ),
    #     WidgetDef(method=dpg.add_table_column, ),
    #     WidgetDef(method=dpg.add_table_row, ),
    #     WidgetDef(method=dpg.add_table_cell, ),
    #     WidgetDef(method=dpg.add_tab_button, ),
    #     WidgetDef(method=dpg.add_tab_bar, ),
    #     WidgetDef(method=dpg.add_tab, ),
    #     WidgetDef(method=dpg.add_button, ),
    #     WidgetDef(method=dpg.add_combo, ),
    #     WidgetDef(method=dpg.add_separator, ),
    #     WidgetDef(method=dpg.add_child_window, ),
    #     WidgetDef(method=dpg.add_window, ),
    #     WidgetDef(method=dpg.add_text, ),
    #     WidgetDef(method=dpg.add_collapsing_header, ),
    #     WidgetDef(method=dpg.add_group, ),
    #     WidgetDef(method=dpg.add_plot_legend, ),
    #     WidgetDef(method=dpg.add_plot_axis, parameters={'axis': 'dpg.mvXAxis'}, ),
    #     WidgetDef(method=dpg.add_plot_axis, parameters={'axis': 'dpg.mvYAxis'}, ),
    #     WidgetDef(method=dpg.add_subplots, ),
    #     WidgetDef(method=dpg.add_simple_plot, ),
    #     WidgetDef(method=dpg.add_plot, ),
    #     WidgetDef(method=dpg.add_input_intx, ),
    #     WidgetDef(method=dpg.add_input_int, ),
    #     WidgetDef(method=dpg.add_progress_bar, ),
    #     WidgetDef(method=dpg.add_checkbox, ),
    #     WidgetDef(method=dpg.add_colormap_scale, ),
    #     WidgetDef(method=dpg.add_drag_line, ),
    #     WidgetDef(method=dpg.add_drag_point, ),
    #     WidgetDef(method=dpg.add_slider_int, ),
    #     WidgetDef(method=dpg.add_slider_intx, ),
    #     WidgetDef(method=dpg.add_slider_float, ),
    #     WidgetDef(method=dpg.add_slider_floatx, ),
    #     WidgetDef(method=dpg.add_3d_slider, ),
    #     WidgetDef(method=dpg.add_tooltip, ),
    #     # todo: tackle this once below enums are resolved
    #     #   + mvThemeCat_
    #     #   + mvThemeCol_
    #     #   + mvPlotCol_
    #     #   + mvNodeCol_
    #     #   + mvStyleVar_
    #     #   + mvPlotStyleVar_
    #     #   + mvNodeStyleVar_
    #     #   + mvFontRangeHint_
    #     # WidgetDef(
    #     #     method=dpg.theme,
    #     # ),
    #     # WidgetDef(
    #     #     method=dpg.theme_component,
    #     # ),
    #     # WidgetDef(
    #     #     method=dpg.add_theme_color,
    #     #     widget_name="ThemeColor",
    #     #     enum_fields={
    #     #         'value': 'Color.BLACK',
    #     #         'target': 'ThemeCol.DEFAULT',
    #     #         'category': 'ThemeCat.DEFAULT',
    #     #     },
    #     # ),
    #     # WidgetDef(
    #     #     method=dpg.add_theme_style,
    #     #     widget_name="ThemeStyle",
    #     #     enum_fields={
    #     #         'target': 'ThemeCol.DEFAULT',
    #     #         'category': 'ThemeCat.DEFAULT',
    #     #     },
    #     # ),
    # ]


def create_auto_code_for_widgets_and_enums():
    # ---------------------------------------------------- 01
    _script_file = pathlib.Path(__file__)
    _script_file = _script_file.relative_to(
        _script_file.parent.parent.parent.parent).as_posix()
    _header = f'''"""
********************************************************************************
This code is auto-generated:
>> Script: {_script_file}
>> DearPyGui: {dearpygui.__version__}
>> Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import dearpygui.dearpygui as dpg
import dataclasses
import typing as t
import enum

from .__base__ import Widget, Container, Callback
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
    _output_file = pathlib.Path("../_auto.py")
    _output_file.write_text(_header + _enum_code + _widget_code)


if __name__ == '__main__':
    create_auto_code_for_widgets_and_enums()
