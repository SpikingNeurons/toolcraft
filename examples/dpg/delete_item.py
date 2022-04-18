import dearpygui.dearpygui as dpg
from math import sin

_uid_container = {}

dpg.create_context()


# creating data
sindatax = []
sindatay = []
for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))


with dpg.window(label="Tutorial"):
    _b1 = dpg.add_button(label="Button 1")
    _b2 = dpg.add_button(label="Button 2")
    with dpg.group():
        _b3 = dpg.add_button(label="Button 3")
        _b4 = dpg.add_button(label="Button 4")
        with dpg.group() as group1:
            pass

    # create plot
    with dpg.plot(label="Line Series", height=400, width=400) as _p:
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        _x = dpg.add_plot_axis(dpg.mvXAxis, label="x")
        _y = dpg.add_plot_axis(dpg.mvYAxis, label="y")

        # series belong to a y axis
        _l = dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)", parent=_y)

_b5 = dpg.add_button(label="Button 5", parent=group1)
_b6 = dpg.add_button(label="Button 6", parent=group1)



def button_callback(sender, app_data, user_data):
    print(_b1, _b2, _b3, _b4, _b5, _b5, _bb, _p, _x, _y, _l)
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")
    dpg.delete_item(_b1, children_only=False, slot=-1)
    dpg.delete_item(_b2, children_only=False, slot=-1)
    dpg.delete_item(_b5, children_only=False, slot=-1)
    dpg.delete_item(_p, children_only=False, slot=-1)
    dpg.delete_item(_l, children_only=False, slot=-1)

_bb = dpg.add_button(label="Button Button", callback=button_callback, parent=group1)

dpg.create_viewport(title='Custom Title', width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
