import dataclasses
import typing as t

import dearpygui.dearpygui as dpg
import numpy as np
from toolcraft import gui


@dataclasses.dataclass(frozen=True)
class Info(gui.CollapsingHeader):

    label: str = "Topic 1 - Text"

    message: gui.Text = gui.Text(
        "This is topic 1. We will just add some bullet points below ...",
    )

    bullet_1: gui.Text = gui.Text(
        "bullet 1 ...",
        bullet=True,
    )

    bullet_2: gui.Text = gui.Text(
        "bullet 2 ...",
        bullet=True,
    )


@dataclasses.dataclass(frozen=True)
class Plotting(gui.CollapsingHeader):

    label: str = "Topic 2 - Plotting"

    line_plot: gui.Plot = gui.Plot(
        label="This is line plot ...",
        height=200,
    )

    scatter_plot: gui.Plot = gui.Plot(
        label="This is scatter plot ...",
        height=200,
    )

    subplot: gui.Subplots = gui.Subplots(
        rows=2,
        columns=2,
        label="This is sub plot ...",
    )

    def plot_some_examples(self):
        # ------------------------------------------------------- 01
        # _simple_plot
        ...

        # ------------------------------------------------------- 02
        # _line_plot
        _line_plot = self.line_plot
        _line_plot.add_line_series(
            label="line 1",
            x=np.arange(100),
            y=np.random.normal(0.0, scale=2.0, size=100),
        )
        _line_plot.add_line_series(
            label="line 2",
            x=np.arange(100),
            y=np.random.normal(0.0, scale=2.0, size=100),
        )
        _line_plot.add_vline_series(x=[1.0, 2.0], label="vline 1")
        _line_plot.add_vline_series(x=[10.0, 11.0], label="vline 2")
        _line_plot.add_hline_series(x=[1.0, 2.0], label="hline 1")
        _line_plot.add_hline_series(x=[10.0, 11.0], label="hline 2")

        # ------------------------------------------------------- 03
        _scatter_plot = self.scatter_plot
        _scatter_plot.add_scatter_series(
            label="scatter 1",
            x=np.random.normal(1.0, scale=2.0, size=100),
            y=np.random.normal(0.0, scale=2.0, size=100),
        )
        _scatter_plot.add_scatter_series(
            label="scatter 2",
            x=np.random.normal(0.0, scale=2.0, size=100),
            y=np.random.normal(1.0, scale=2.0, size=100),
        )

        # ------------------------------------------------------- 04
        _subplot = self.subplot
        for i in range(4):
            _plot = gui.Plot(height=200)
            _subplot.add_child(guid=f"plot_{i}", widget=_plot)
            _plot.add_line_series(
                label="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
            _plot.add_line_series(
                label="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )


@dataclasses.dataclass(frozen=True)
class ButtonPlotCallback(gui.Callback):

    receiver: gui.Widget

    def fn(
        self,
        sender: gui.Widget,
        app_data: t.Any,
        user_data: t.Union[gui.Widget, t.List[gui.Widget]],
    ):
        # provide type
        sender: gui.Button

        # display to receiver i.e. add_child if not there
        if sender.guid not in self.receiver.children.keys():

            # make collapsing header
            _collapsing_header = gui.CollapsingHeader(
                label=sender.label,
                closable=False,
                default_open=True,
            )

            # add child to receiver
            self.receiver.add_child(guid=sender.guid, widget=_collapsing_header)

            # make close button and add it collapsing header
            _close_button = gui.callback.CloseWidgetCallback.get_button_widget(
                _collapsing_header
            )
            _collapsing_header.add_child(
                guid="close_button",
                widget=_close_button,
            )

            # make plot and add to collapsing header
            _plot = gui.Plot(
                label=f"This is plot for {sender.label} ...",
                height=200,
                width=-1,
            )
            _collapsing_header.add_child(guid="plot", widget=_plot)

            # add some data
            _plot.add_line_series(
                label="line 1",
                x=np.random.normal(0.0, scale=2.0, size=100),
                y=np.random.normal(1.0, scale=2.0, size=100),
            )
            _plot.add_scatter_series(
                label="scatter 1",
                x=np.random.normal(0.0, scale=2.0, size=100),
                y=np.random.normal(1.0, scale=2.0, size=100),
            )

        # else we do nothing as things are already plotted
        else:
            # in case user has close collapsable header we can attempt to
            # show it again
            # _collapsable_header = self.receiver.children[_sender.label]
            # _collapsable_header.show()
            ...


@dataclasses.dataclass(frozen=True)
class ButtonPlot(gui.CollapsingHeader):

    label: str = "Topic 3 - Button with action"

    def layout(self):
        _table = gui.Table(
            header_row=False,
            resizable=True,
            policy=gui.TableSizing.StretchSame,
            borders_innerH=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_outerV=True,
            rows=1,
            columns=2,
        )
        _button_cell = _table.get_cell(row=0, column=0)
        _display_cell = _table.get_cell(row=0, column=1)
        for i in range(5):
            _button_cell.add_child(
                guid=f"button{i}",
                widget=gui.Button(
                    width=300,
                    label=f"Button {i}",
                    callback=ButtonPlotCallback(receiver=_display_cell),
                ),
            )
        self.add_child(guid="columns", widget=_table)


@dataclasses.dataclass(frozen=True)
class MyDashboard(gui.Dashboard):

    theme_selector: gui.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.Text = gui.Text(
        "Welcome to my dashboard ..... toolcraft ..... ",
    )

    topic1: Info = Info()

    topic2: Plotting = Plotting()

    topic3: ButtonPlot = ButtonPlot()

    def layout(self):
        self.add_child(guid="theme_selector", widget=self.theme_selector)
        self.add_child(guid="welcome_msg", widget=self.welcome_msg)
        self.add_child(guid="topic2", widget=self.topic2)
        self.add_child(guid="topic1", widget=self.topic1, before=self.topic2)
        self.add_child(guid="topic3", widget=self.topic3)


def basic_dashboard():
    _dash = MyDashboard(dash_guid="my_dashboard", title="My Dashboard")
    _dash.build()
    _dash.topic2.plot_some_examples()
    _dash.run()


def demo():
    """
    Refer
    >>> from dearpygui import demo
    """

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    gui.demo.show_demo()

    # with dpg.window(label="Dear PyGui Demo", width=800, height=800,
    #                 pos=(100, 100), tag="__demo_id"):
    #     with dpg.collapsing_header(label="some label", default_open=True,):
    #         dpg.add_text(default_value="Some text")

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    basic_dashboard()
    demo()


if __name__ == "__main__":
    main()
