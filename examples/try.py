import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Dear PyGui Demo", width=800, height=800,
                pos=(100, 100), tag="__demo_id") as w1:

    with dpg.collapsing_header(label="some label 111", default_open=True,) as p1:
        a1 = dpg.add_text(default_value="Some text 111")
    with dpg.collapsing_header(label="some label 222", default_open=True,) as p2:
        a2 = dpg.add_text(default_value="Some text 222", before=a1)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
