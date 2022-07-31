import inspect
import pathlib
import dearpygui
import dearpygui.dearpygui as dpg
from typing import NamedTuple
import typing as t
import re
import datetime
_now = datetime.datetime.now

_WRAP_TEXT_WIDTH = 70
_NEEDED_ENUMS = {}  # type: t.Dict[str, 'EnumDef']

_SKIP_METHODS = [
    # not required
    dpg.contextmanager, dpg.deprecated,
    dpg.add_alias, dpg.remove_alias, dpg.does_alias_exist,
    dpg.get_alias_id, dpg.get_aliases, dpg.set_item_alias,
    dpg.does_item_exist,
    dpg.generate_uuid, dpg.get_all_items,
    dpg.get_dearpygui_version, dpg.get_item_alias, dpg.get_values,
    dpg.run_callbacks, dpg.get_callback_queue,

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
    dpg.is_table_cell_highlighted,  # Table.is_cell_highlighted
    dpg.is_table_column_highlighted,  # Table.is_column_highlighted
    dpg.is_table_row_highlighted,  # Table.is_row_highlighted
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

    # handled by window.PopUp
    dpg.popup,

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
    dpg.get_platform,
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
    dpg.draw_image_quad,

    # todo: support when using node editor
    dpg.node_editor, dpg.add_node_link, dpg.clear_selected_links,
    dpg.clear_selected_nodes, dpg.get_selected_links, dpg.get_selected_nodes,

    # todo: may be these need to be used as Widget methods and not as Widget's
    dpg.bind_colormap, dpg.bind_font, dpg.bind_item_font,
    dpg.bind_item_handler_registry, dpg.bind_item_theme,
    dpg.bind_template_registry, dpg.bind_theme, dpg.get_text_size,

    # todo: transform related animation things
    dpg.apply_transform, dpg.create_fps_matrix, dpg.create_lookat_matrix,
    dpg.create_orthographic_matrix, dpg.create_perspective_matrix,
    dpg.create_rotation_matrix, dpg.create_scale_matrix, dpg.create_translation_matrix,

    # todo: viewport ... useful to make visual code style docking
    dpg.viewport_drawlist,  # this can be a Container ... but note that it is not a Widget
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
    dpg.set_clip_space,
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

    # todo: when grabbing UI frames for examples
    dpg.output_frame_buffer, dpg.save_image,

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
    dpg.add_char_remap,
    dpg.render_dearpygui_frame, dpg.reorder_items,
    dpg.sample_colormap, dpg.save_init_file,
    dpg.set_global_font_scale, dpg.set_frame_callback, dpg.set_exit_callback,
    dpg.split_frame,
    dpg.track_item, dpg.untrack_item,
    dpg.theme, dpg.stage, dpg.get_clipboard_text, dpg.set_clipboard_text,
]


class DpgBuildParamDef(NamedTuple):
    name: str
    dpg_name: str
    type: str
    value: str
    dpg_value: str
    doc: str

    @property
    def is_callback(self) -> bool:
        return self.type.find("Callback") != -1

    @property
    def is_mandatory(self) -> bool:
        # noinspection PyUnresolvedReferences,PyProtectedMember
        return self.value == inspect._empty


class DpgDef:

    @property
    def is_plot_related(self) -> bool:
        # this means that items that Plot class can hold
        # note that plot, subplots and simple_plot are not the children of plot
        if self.fn in [
            # dpg.plot, dpg.subplots, dpg.add_simple_plot,
            dpg.plot_axis, dpg.add_plot_legend,
            dpg.add_plot_annotation, dpg.add_drag_line, dpg.add_drag_point,
        ]:
            return True
        else:
            return False

    @property
    def is_plot_series_related(self) -> bool:
        if self.fn.__name__.startswith("add") and self.fn.__name__.endswith("series"):
            return True
        else:
            return False

    @property
    def is_table_related(self) -> bool:
        if self.fn in [dpg.table, dpg.table_cell, dpg.table_row, dpg.add_table_column]:
            return True
        else:
            return False

    @property
    def is_container(self) -> bool:
        # if dec by @contextmanager then is container
        _is_container = self.fn_src.find("@contextmanager") != -1

        # x_axis is not container but y_axis is
        # >>> check 'gui.plot.XAxis' and `gui.plot.YAxis`
        if self.fn == dpg.plot_axis:
            if self.parametrize['axis'] == 'dpg.mvXAxis':
                _is_container = False
            elif self.parametrize['axis'] == 'dpg.mvYAxis':
                _is_container = True
            else:
                raise Exception(f"Unknown {self.parametrize['axis']} ...")

        # return
        return _is_container

    @property
    def is_frozen(self) -> bool:
        if self.is_registry:
            return True
        return False

    @property
    def _call_prefix(self) -> str:

        _call_prefix = \
            f"internal_dpg.add_{self.fn.__name__}" \
            if self.is_container else f"internal_dpg.{self.fn.__name__}"

        if self.fn == dpg.plot_axis:
            _call_prefix = f"internal_dpg.add_{self.fn.__name__}"

        return _call_prefix

    @property
    def _super_class_name(self) -> str:
        _class_name = "___"
        if self.is_parent_param_present:
            if self.is_before_param_present:
                if self.is_container:
                    _class_name = "MovableContainerWidget"

                else:
                    _class_name = "MovableWidget"

                    # plot series for y-axis ...
                    # always have before and are not containers
                    if self.is_plot_series_related:
                        _class_name = "PlotSeries"

                    # if plot related
                    # note that apart from XAxis, YAxis and Legend rest all are movable
                    # also note that XAxis, YAxis and Legend are handled separately
                    # as they are not true children to Plot
                    if self.is_plot_related:
                        _class_name = "PlotItem"
            else:
                if self.is_container:
                    _class_name = "ContainerWidget"
                else:
                    _class_name = "Widget"

        elif self.is_registry:
            _class_name = "Registry"
        else:
            if self.fn in [
                dpg.window, dpg.file_dialog,
            ]:
                _class_name = "ContainerWidget"
        return _class_name

    @property
    def _name(self) -> str:
        # ------------------------------------------------------- 01
        # generate name based on method and parameters
        if self.fn == dpg.plot_axis:
            if self.parametrize['axis'] == 'dpg.mvXAxis':
                return "PlotXAxis"
            if self.parametrize['axis'] == 'dpg.mvYAxis':
                return "PlotYAxis"
            raise Exception(
                f"Unknown parameter value for axis {self.parametrize['axis']}"
            )

        # ------------------------------------------------------- 02
        # if you reach here means parameters are not needed
        assert self.parametrize is None, "You need not supply parametrize"

        # ------------------------------------------------------- 03
        # generate name based on method
        if self.fn == dpg.add_checkbox:
            return "CheckBox"
        if self.fn == dpg.drawlist:
            return "DrawList"
        if self.fn == dpg.subplots:
            return "SubPlots"
        if self.fn == dpg.add_vline_series:
            return "VLineSeries"
        if self.fn == dpg.add_hline_series:
            return "HLineSeries"
        if self.fn == dpg.add_3d_slider:
            return "Slider3D"
        if self.fn == dpg.add_2d_histogram_series:
            return "HistogramSeries2D"
        if self.fn == dpg.add_drag_line:
            return "PlotDragLine"
        if self.fn == dpg.add_drag_point:
            return "PlotDragPoint"

        # ------------------------------------------------------- 04
        # default name generation
        _name = self.fn.__name__.replace("add_", "")
        _name = _name.title().replace("_", "")
        _name = _name.replace("Intx", "IntX").replace("Floatx", "FloatX")

        # ------------------------------------------------------- 05
        return _name

    @property
    def _docs(self) -> t.Dict[str, str]:
        _main_doc = []
        _docs_dict = {}
        _track = False
        for _l in self.fn.__doc__.split("\n"):
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

    @property
    def _param_defs(self) -> t.List[DpgBuildParamDef]:

        # to return container
        _ret = []

        # ignore params
        _ignore_params = ['id', 'parent', 'tag', 'before', 'kwargs']

        # ignore axis param if needed
        if self.fn in [dpg.plot_axis, dpg.add_plot_axis]:
            _ignore_params.append('axis')

        if self.is_plot_series_related or self.is_plot_related:
            _ignore_params.append("use_internal_label")
            if "use_internal_label" not in [
                _param.name for _param in self.fn_signature.parameters.values()
            ]:
                raise Exception(
                    f"This looks like plot series related method so we expect "
                    f"param use_internal_label"
                )

        # loop over all params
        for _param in self.fn_signature.parameters.values():

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

            # if below type then it is PLOT_DATA_TYPE
            if _param_type == "t.Union[t.List[float], t.Tuple[float, ...]]":
                _param_type = "PLOT_DATA_TYPE"
            # if below type then it is COLOR_TYPE
            if _param_name.find("color") != -1 and \
                    _param_name not in ["colormap", "multicolor"]:
                if self.fn == dpg.add_colormap:
                    if _param_name == "colors":
                        _param_type = "t.List[COLOR_TYPE]"
                elif _param_type == "t.Union[t.List[int], t.Tuple[int, ...]]":
                    _param_type = "COLOR_TYPE"
                else:
                    raise Exception(
                        f"We assume that fn param `{self.fn.__name__}:{_param_name}` "
                        f"is a color type so dpg param type must be "
                        f"<t.Union[t.List[int], t.Tuple[int, ...]]>, but found type "
                        f"<{_param_type}>"
                    )

            # is callback
            _is_callback = _param_type.find("Callback") != -1

            # param value
            _param_value = _param.default

            # param dpg value
            _param_dpg_value = f"self.{_param_name}"

            # param doc
            _param_doc = self.docs[_param_name]

            # if param is enum we will get _enum_def
            _enum_def = None
            if _param_name not in ['source', 'before']:
                _enum_def = CodeMaker.fetch_enum_def_from_fn_param_doc(
                    method=self.fn, param_name=_param_name, param_doc=_param_doc
                )
                if _enum_def is not None:
                    self.enum_defs_needed.append(_enum_def)

            # some replacements
            if _param_name == "source":
                _param_type = "t.Optional[Widget]"
                _param_value = "None"
                _param_dpg_value = "_source_dpg_id"
            if _param_name == "user_data":
                _param_type = "USER_DATA"
                _param_value = "None"
            if _param_name == "on_enter":
                _param_name = "if_entered"
                _param_dpg_name = "on_enter"
                _param_dpg_value = "self.if_entered"
            if _param_name == "label":
                if self.is_plot_series_related or self.is_plot_related:
                    _param_dpg_value = "None if self.label is None else self.label.split('#')[0]"
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
                DpgBuildParamDef(
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

    @property
    def _code(self) -> t.List[str]:
        # ------------------------------------------------------- 01
        # print(f"getting code for `dpg.{self.fn.__name__}`")

        # ------------------------------------------------------- 03
        # make code lines
        # ------------------------------------------------------- 03.01
        _frozen = ""
        if self.is_frozen:
            _frozen = "(frozen=True)"
        # code header
        _lines = [
            "",
            "",
            f"@dataclasses.dataclass{_frozen}",
            f"class {self.name}({self.super_class_name}):",
            '\t"""',
            "\tRefer:",
            f"\t>>> dpg.{self.fn.__name__}",
            "",
        ] + [self.docs['main_doc']] + ['\t"""', ""]
        # ------------------------------------------------------- 03.02
        # make fields
        for _pd in self.param_defs:
            _lines += [f"\t# {_pd.doc}"]
            # noinspection PyUnresolvedReferences,PyProtectedMember
            if _pd.value is inspect._empty:
                _lines += [f"\t{_pd.name}: {_pd.type}"]
            else:
                _lines += [f"\t{_pd.name}: {_pd.type} = {_pd.value}"]
            _lines += [""]

        # ------------------------------------------------------- 03.03
        # add properties
        # ------------------------------------------------------- 03.03.01
        # property ...

        # ------------------------------------------------------- 03.04
        # add build method
        # ------------------------------------------------------- 03.04.01
        # get same values in local vars
        _local_val_lines = []
        if self.is_parent_param_present:
            _local_val_lines += ["\t\t_parent_dpg_id = self.internal.parent.dpg_id"]
        if self.is_source_param_present:
            _local_val_lines += ["\t\t_source_dpg_id = getattr(self.source, 'dpg_id', 0)"]
        if bool(_local_val_lines):
            _local_val_lines = [""] + _local_val_lines
        # ------------------------------------------------------- 03.04.02
        # add some internal params needed for dpg call
        _internal_params = {}
        if self.is_parent_param_present:
            _internal_params['parent'] = "_parent_dpg_id"
        if self.is_plot_series_related or self.is_plot_related:
            _internal_params['use_internal_label'] = "False"
        # ------------------------------------------------------- 03.04.03
        _parametrized_params = {} if self.parametrize is None else self.parametrize
        # ------------------------------------------------------- 03.04.04
        _lines += [
            "\tdef build(self) -> t.Union[int, str]:",
            *_local_val_lines,
            "",
            f"\t\t_ret = {self.call_prefix}(",
            *[
                f"\t\t\t{_pd.dpg_value},"
                for _pd in self.param_defs if _pd.is_mandatory
            ],
            # *[f"\t\t\t{_k}={_v}," for _k, _v in _parametrized_params.items()],
            *[f"\t\t\t{_v}," for _k, _v in _parametrized_params.items()],
            *[f"\t\t\t{_k}={_v}," for _k, _v in _internal_params.items()],
            *[
                f"\t\t\t{_pd.dpg_name}={_pd.dpg_value},"
                for _pd in self.param_defs if not _pd.is_mandatory
            ],
            f"\t\t)",
            f"\t\t",
            f"\t\treturn _ret",
        ]

        # ------------------------------------------------------- 03.05
        # add methods for callback params
        for _pd in self.param_defs:
            if not _pd.is_callback:
                continue
            _lines += [
                "",
                f"\tdef {_pd.name}_fn(self, sender_dpg_id: int):",
                # todo: eventually remove this sanity check
                "\t\t# eventually remove this sanity check in ("
                "dpg_widgets_generator.py)...",
                "\t\tassert sender_dpg_id == self.dpg_id, \\"
                "\n\t\t\t'was expecting the dpg_id to match ...'",
                # "\t\tassert id(user_data) == id(self.user_data), \\"
                # "\n\t\t\t'was expecting the user_data to match ...'",
                "",
                "\t\t# logic ...",
                f"\t\tif self.{_pd.name} is None:",
                f"\t\t\treturn None",
                f"\t\telse:",
                f"\t\t\treturn self.{_pd.name}.fn(sender=self)",
            ]

        # ------------------------------------------------------- 04
        # replace \t to 4 spaces
        _lines = [_.replace("\t", "    ") for _ in _lines]
        return _lines

    def __init__(
        self,
        fn: t.Callable,
        # used to generate multiple widgets based on parameters supplied that will be
        # hardcoded in build method
        parametrize: t.Dict[str, str] = None
    ):
        # -------------------------------------------------------- 01
        self.fn = fn
        self.parametrize = parametrize
        self.enum_defs_needed = []

        # -------------------------------------------------------- 02
        self.fn_src = inspect.getsource(self.fn)
        self.fn_signature = inspect.signature(self.fn)

        # -------------------------------------------------------- 03
        self.is_registry = self.fn.__name__.find("registry") != -1

        # -------------------------------------------------------- 04
        self.is_before_param_present = False
        self.is_source_param_present = False
        self.is_parent_param_present = False
        for _param in self.fn_signature.parameters.values():
            if _param.name == 'before':
                assert _param.annotation == t.Union[int, str]
                self.is_before_param_present = True
            if _param.name == 'source':
                assert _param.annotation == t.Union[int, str]
                self.is_source_param_present = True
            if _param.name == 'parent':
                assert _param.annotation == t.Union[int, str]
                self.is_parent_param_present = True
        if self.is_before_param_present:
            if not self.is_parent_param_present:
                raise Exception("If before is present then parent should also be present")

        # -------------------------------------------------------- 05
        self.name = self._name
        self.call_prefix = self._call_prefix
        self.super_class_name = self._super_class_name
        self.docs = self._docs
        self.param_defs = self._param_defs
        self.code = self._code

    def fn_fake_call(self, parent):
        _kwargs = {}

        if 'x' in self.fn_signature.parameters.keys():
            _kwargs['x'] = [1., 2.]
            _kwargs['y'] = [1., 2.]

        if bool(self.parametrize):
            # noinspection PyTypeChecker
            _kwargs.update(self.parametrize)

        if self.is_container:
            with self.fn(parent=parent, **_kwargs) as _child_dpg_id:
                ...
        else:
            self.fn(parent=parent, **_kwargs)


class EnumDef:

    @property
    def _code(self) -> t.List[str]:

        # add header
        _lines = [
            "",
            "",
            f"class {self.enum_name}(Enum, enum.Enum):",
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

    def __init__(
        self,
        dpg_enum_prefix: str,
        dpg_enum_values: t.List[str]
    ):
        self.dpg_enum_prefix = dpg_enum_prefix
        self.dpg_enum_values = dpg_enum_values
        self.enum_name = "En" + self.dpg_enum_prefix.replace("mv", "").replace("_", "")
        self.code = self._code

    def __eq__(self, other):
        return self.dpg_enum_prefix == other.dpg_enum_prefix and \
               self.dpg_enum_values == other.dpg_enum_values

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


class CodeMaker:

    @property
    def header(self) -> str:

        _script_file = pathlib.Path(__file__)
        _script_file = _script_file.relative_to(
            _script_file.parent.parent.parent.parent).as_posix()
        _header = f'''"""
********************************************************************************
This code is auto-generated:
>> Script: {_script_file}
>> DearPyGui: {dearpygui.__version__}
>> Time: {_now().strftime("%Y-%m-%d %H:%M")}
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

# noinspection PyProtectedMember
import dearpygui._dearpygui as internal_dpg
import dearpygui.dearpygui as dpg
import dataclasses
import enum
import typing as t

from .__base__ import Enum
from .__base__ import Widget
from .__base__ import MovableWidget
from .__base__ import ContainerWidget
from .__base__ import MovableContainerWidget
from .__base__ import Callback
from .__base__ import Registry
from .__base__ import PlotSeries
from .__base__ import PlotItem
from .__base__ import PLOT_DATA_TYPE
from .__base__ import COLOR_TYPE
from .__base__ import USER_DATA
'''
        return _header

    def __init__(self):
        if bool(_NEEDED_ENUMS):
            raise Exception("Should be empty ... only call once")
        self.all_dpg_defs = self.fetch_all_dpg_defs()

        # some enums are not detected via doc string, so we add it here
        # noinspection PyTypeChecker
        _enum_defs = [
            self.fetch_enum_def_from_fn_param_doc(
                method=None, param_name=None,
                param_doc="  Union[int, str]  mvMouseButton_*  "
            ),
            self.fetch_enum_def_from_fn_param_doc(
                method=None, param_name=None,
                param_doc="  Union[int, str]  mvPlatform_*  "
            ),
        ]

    @staticmethod
    def fetch_enum_def_from_fn_param_doc(
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
        for _ in _enum_val_s:
            _param_name_has_star = (_.find("*") != -1) or _param_name_has_star

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
        return _NEEDED_ENUMS[_enum_def.enum_name]

    @staticmethod
    def fetch_all_dpg_defs() -> t.List[DpgDef]:

        _ret = []
        _dir_dpg = dir(dpg)

        # loop over dpg module
        for _fn_name in _dir_dpg:
            # ---------------------------------------------------------- 01
            # skip if not function
            _fn = getattr(dpg, _fn_name)
            if not inspect.isfunction(_fn):
                continue

            # ---------------------------------------------------------- 02
            # fn details
            _fn_src = inspect.getsource(_fn)

            # ---------------------------------------------------------- 03
            # skip if deprecated
            if _fn_src.find("@deprecated") != -1:
                continue

            # ---------------------------------------------------------- 04
            # if in _SKIP_METHODS then skip
            if _fn in _SKIP_METHODS:
                continue
            print(f"Making DpgDef for {_fn}")

            # ---------------------------------------------------------- 05
            # handle fns with contextmanager
            # ---------------------------------------------------------- 05.01
            # if _context_manager_dec_present then check that add_ prefix is not present
            if _fn_src.find("@contextmanager") != -1:
                # ------------------------------------------------------ 05.01.01
                # should not start with add
                assert not _fn.__name__.startswith("add_"), \
                    f"was not expecting to start with add_ >> {_fn}"
                # ------------------------------------------------------ 05.01.02
                # check if corresponding add_ present
                _fn_name_with_add = "add_" + _fn.__name__
                if _fn_name_with_add not in _dir_dpg:
                    raise Exception(
                        f"Corresponding method `{_fn_name_with_add}` is not present"
                    )
            # ---------------------------------------------------------- 05.02
            # if starts with add_* and has corresponding fn with
            # _context_manager_dec_present then skip add_* fn
            if _fn.__name__.startswith("add_"):
                _fn_name_without_add = _fn.__name__.replace("add_", "")
                if _fn_name_without_add in _dir_dpg:
                    # -------------------------------------------------- 05.02.01
                    # also make sure that it has context manager
                    _fn_without_add = getattr(dpg, _fn_name_without_add)
                    if inspect.getsource(_fn_without_add).find("@contextmanager") == -1:
                        raise Exception(
                            f"Was expecting {_fn_without_add} to have contextmanager"
                        )
                    # -------------------------------------------------- 05.02.02
                    # continue
                    continue

            # ---------------------------------------------------------- 06
            # append
            if _fn == dpg.plot_axis:
                _ret.append(DpgDef(fn=_fn, parametrize={'axis': 'dpg.mvXAxis'}, ))
                _ret.append(DpgDef(fn=_fn, parametrize={'axis': 'dpg.mvYAxis'}, ))
            else:
                _ret.append(DpgDef(fn=_fn))

        # return
        return _ret

    @staticmethod
    def add_auto_imports_to_py_file(
        output_file: pathlib.Path, import_lines: t.List[str]
    ):
        # ---------------------------------------------------------- 01
        # get tags and their index
        _start_tag = "# auto pk; start >>>"
        _end_tag = "# auto pk; end <<<"
        _start_tag_index = None
        _end_tag_index = None
        _output_file_lines = output_file.read_text().split("\n")
        for _i, _l in enumerate(_output_file_lines):
            if _l == _start_tag:
                _start_tag_index = _i
            if _l == _end_tag:
                _end_tag_index = _i
        if _start_tag_index is None:
            raise Exception(f"Did not find start tag `{_start_tag}` in file {output_file}")
        if _end_tag_index is None:
            raise Exception(f"Did not find start tag `{_end_tag}` in file {output_file}")
        if _end_tag_index <= _start_tag_index:
            raise Exception(f"{_end_tag_index} <= {_start_tag_index}")
        # ---------------------------------------------------------- 02
        _start_lines = _output_file_lines[:_start_tag_index+1]
        _end_lines = _output_file_lines[_end_tag_index:]
        # ---------------------------------------------------------- 03
        output_file.write_text(
            "\n".join(_start_lines + import_lines + _end_lines)
        )

    def make_widget_py(self):
        # -------------------------------- 01
        # init
        _output_file = pathlib.Path("../widget.py")
        _dis_inspect = "# noinspection PyUnresolvedReferences"

        # -------------------------------- 02
        # widget and container lines
        _lines = []
        for _widget_def in self.all_dpg_defs:
            if _widget_def.is_plot_related or _widget_def.is_table_related or _widget_def.is_plot_series_related or _widget_def.is_plot_related:
                continue
            _lines.append(_dis_inspect)
            _lines.append(f"from ._auto import {_widget_def.name}")

        # -------------------------------- 03
        self.add_auto_imports_to_py_file(_output_file, _lines)

    def make_plot_py(self):
        # -------------------------------- 01
        # init
        _output_file = pathlib.Path("../plot.py")
        _dis_inspect = "# noinspection PyUnresolvedReferences"

        # -------------------------------- 02
        # widget and container lines
        _lines = []
        for _widget_def in self.all_dpg_defs:
            # note that is_plot_related things will be again redefined in ../plot.py
            # so no need to add import
            if _widget_def.is_plot_series_related:
                _lines.append(_dis_inspect)
                _lines.append(f"from ._auto import {_widget_def.name}")

        # -------------------------------- 03
        self.add_auto_imports_to_py_file(_output_file, _lines)

    def make_auto_py(self):
        # -------------------------------- 01
        # init
        _output_file = pathlib.Path("../_auto.py")

        # -------------------------------- 02
        # make lines
        # -------------------------------- 02.01
        # enum lines
        _enum_lines = []
        for _enum_def in _NEEDED_ENUMS.values():
            _enum_lines += _enum_def.code
        # -------------------------------- 02.02
        # widget and container lines
        _widget_lines = []
        for _widget_def in self.all_dpg_defs:
            _widget_lines += _widget_def.code

        # -------------------------------- 03
        _output_file.write_text(
            self.header +
            "\n".join(
                _enum_lines + _widget_lines + [""]
            )
        )

    def make_enum_py(self):
        # -------------------------------- 01
        # init
        _output_file = pathlib.Path("../_enum.py")

        # -------------------------------- 02
        # check
        if not bool(_NEEDED_ENUMS):
            raise Exception("Expected this to be filled up by now")

        # -------------------------------- 03
        # make lines
        _dis_inspect = "# noinspection PyUnresolvedReferences"
        _lines = [_dis_inspect, "from .__base__ import EnColor"]
        for _enum_def in _NEEDED_ENUMS.values():
            _lines.append(_dis_inspect)
            _lines.append(f"from ._auto import {_enum_def.enum_name}")

        # -------------------------------- 04
        # code
        _code = "\n".join(_lines + [""])

        # -------------------------------- 05
        # write
        self.add_auto_imports_to_py_file(_output_file, _lines)

    def make(self):
        self.make_auto_py()
        self.make_enum_py()
        self.make_widget_py()
        self.make_plot_py()


def try_dpg_children(_dpg_def: DpgDef, _all_dpg_defs: t.List[DpgDef]):

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.window(label="Dear PyGui Demo", width=800, height=800,
                    pos=(100, 100), tag="__demo_id") as w1:

        _ret = []
        if _dpg_def.is_container:
            with _dpg_def.fn() as _dpg_id:
                for _child_dpg_def in _all_dpg_defs:
                    try:
                        _child_dpg_def.fn_fake_call(parent=_dpg_id)
                        _ret.append(_child_dpg_def)
                    except Exception:
                        ...

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    return _ret


def main():
    _cm = CodeMaker()
    _cm.make()

    # figure out child automatically ... DIFFICULT
    # for _dpg_def in _cm.all_dpg_defs:
    #     if not _dpg_def.is_container:
    #         continue
    #     print("> ", _dpg_def.fn)
    #     _ret = try_dpg_children(_dpg_def, _cm.all_dpg_defs)
    #     for _child_dpg_def in _ret:
    #         print("\t\t\t: ", _child_dpg_def.fn)


if __name__ == '__main__':
    main()
