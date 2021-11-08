import dearpygui.dearpygui as dpg
import numpy as np
from dearpygui import demo
from toolcraft.gui import _demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

# ----------------------------------------------------------------- DEMO
# demo.show_demo()
# _demo.show_demo()

with dpg.window(label="Dear PyGui Demo", width=800, height=800,
                pos=(100, 100), tag="__demo_id") as w1:

    with dpg.plot(label="plot"):
        dpg.add_plot_axis(dpg.mvXAxis)
        with dpg.plot_axis(dpg.mvYAxis):
            dpg.add_line_series(x=np.arange(10), y=np.random.normal(0.0, scale=2.0, size=10))

    with dpg.plot(label="plot"):
        dpg.add_plot_axis(dpg.mvXAxis)
        with dpg.plot_axis(dpg.mvYAxis):
            _id = dpg.add_line_series(x=np.arange(10), y=np.random.normal(0.0, scale=2.0, size=10))
            dpg.configure_item(_id, x=np.arange(10), y=np.random.normal(0.0, scale=2.0, size=10))
    dpg.configure_item(_id, x=np.arange(10))
#
#     with dpg.collapsing_header(label="some label 111", default_open=True,) as p1:
#         a1 = dpg.add_text(default_value="Some text 111")
#     with dpg.collapsing_header(label="some label 222", default_open=True,) as p2:
#         a2 = dpg.add_text(default_value="Some text 222", before=p1)
#     with dpg.tooltip(parent=p2, label="sasdasd") as tt:
#         dpg.add_text("dddddddddddd")
#     with dpg.tooltip(parent=p2, label="rrrrr") as tt2:
#         dpg.add_text("werwer333333333333")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
