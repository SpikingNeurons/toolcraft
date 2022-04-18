import dearpygui.dearpygui as dpg
import numpy as np

dpg.create_context()


def update():
    global _text, _cell
    dpg.delete_item(_text)

    _text = dpg.add_text(
        parent=_cell,
        default_value=f"hiiiiiiii {np.random.randint(324214234)}")


_win = dpg.add_window(label="Tutorial")
_butt = dpg.add_button(label="Update Series", callback=update, parent=_win)
_table = dpg.add_table(parent=_win)
_col = dpg.add_table_column(parent=_table)
_row = dpg.add_table_row(parent=_table)
_cell = dpg.add_table_cell(parent=_row)
_text = dpg.add_text(parent=_cell, default_value="hiiiiiiii ")

dpg.create_viewport(title="Custom Title", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
