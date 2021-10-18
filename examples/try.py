
import dearpygui.dearpygui as dpg
from dearpygui import demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

demo.show_demo()

# with dpg.window(label="Dear PyGui Demo", width=800, height=800,
#                 pos=(100, 100), tag="__demo_id"):
#
#     with dpg.collapsing_header(label="some label", default_open=True,):
#         dpg.add_text(default_value="Some text")
#
#     with dpg.plot(label="Line Series", height=400, width=-1):
#         dpg.add_text(default_value="Some text")
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

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
