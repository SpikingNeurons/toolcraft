import dearpygui.dearpygui as dpg


if __name__ == "__main__":
    tag="mytableid"
    dpg.create_context()
    with dpg.window(label="main_window"):
        with dpg.table(header_row=True, resizable=True, tag=tag, parent="main_window"):
            dpg.add_table_column(label="Name", parent=tag)
            dpg.add_table_column(label="Size (bytes)", default_sort=True, parent=tag)
            for row in range(0, 100):
                with dpg.table_row(parent=tag):
                    dpg.add_text("col1")
                    dpg.add_text("col2")
        dpg.delete_item(tag, children_only=False)
        # dpg.remove_alias(tag)
        with dpg.table(header_row=True, resizable=True, tag=tag):
            dpg.add_table_column(label="Name", parent=tag)
            dpg.add_table_column(label="Size (bytes)", default_sort=True, parent=tag)
            for row in range(0, 4):
                with dpg.table_row(parent=tag):
                    dpg.add_text("col1")
                    dpg.add_text("col2")

    dpg.create_viewport(title='RPM Quick query tool', width=500)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
