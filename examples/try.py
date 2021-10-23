
import dearpygui.dearpygui as dpg
import dearpygui._dearpygui as internal_dpg
from dearpygui import demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# demo.show_demo()

w1 = dpg.add_window(label="Dear PyGui Demo", width=800, height=800,
                pos=(100, 100), tag="__demo_id")

w2 = dpg.add_window(label="Dear PyGui Demo", width=800, height=30,
                pos=(0, 0), tag="__demo_id_2", no_title_bar=True, no_move=True)

ch = dpg.add_collapsing_header(label="some label", default_open=True, parent=w1)
some_text = dpg.add_text(default_value="Some text", parent = w1)

p1 = dpg.add_plot(label="Line Series", height=400, width=-1, parent=ch)

# optionally create legend
le = dpg.add_plot_legend(location=dpg.mvPlot_Location_South, parent=p1)

# REQUIRED: create x and y axes
axis_x = dpg.add_plot_axis(dpg.mvXAxis, label="x", parent=p1)

axis_y = dpg.add_plot_axis(dpg.mvYAxis, label="y", parent=p1)
# series belong to a y axis
xx= dpg.add_line_series([1,2], [3,4], label="0.5 + 0.5 * sin(x)", parent=axis_y)

print(internal_dpg.get_item_state(w2))
print(internal_dpg.get_item_configuration(w2))
print(internal_dpg.get_app_configuration())

# with dpg.window(label="Dear PyGui Demo", width=800, height=800,
#                 pos=(100, 100), tag="__demo_id") as w1:
#
#     with dpg.collapsing_header(label="some label", default_open=True,):
#         dpg.add_text(default_value="Some text")
#
#     with dpg.plot(label="Line Series", height=400, width=-1):
#
#         # optionally create legend
#         dpg.add_plot_legend(location=dpg.mvPlot_Location_South)
#
#         # REQUIRED: create x and y axes
#         dpg.add_plot_axis(dpg.mvXAxis, label="x")
#
#         with dpg.plot_axis(dpg.mvYAxis, label="y"):
#             # series belong to a y axis
#             dpg.add_line_series([1,2], [3,4], label="0.5 + 0.5 * sin(x)")
#
# with dpg.window(label="Dear PyGui Demo", width=800, height=800,
#                 pos=(100, 100), tag="xx") as w2:
#
#     with dpg.collapsing_header(label="some label", default_open=True,):
#         dpg.add_text(default_value="Some text")
#
#     with dpg.plot(label="Line Series", height=400, width=-1):
#
#         # optionally create legend
#         dpg.add_plot_legend(location=dpg.mvPlot_Location_South)
#
#         # REQUIRED: create x and y axes
#         dpg.add_plot_axis(dpg.mvXAxis, label="x")
#
#         with dpg.plot_axis(dpg.mvYAxis, label="y"):
#             # series belong to a y axis
#             dpg.add_line_series([1,2], [3,4], label="0.5 + 0.5 * sin(x)")
#
# dpg.set_primary_window(w2, value=True)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
