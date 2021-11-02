import dataclasses
import typing as t

import dearpygui.dearpygui as dpg
from toolcraft.gui import _demo
import numpy as np
from toolcraft import gui, util


@dataclasses.dataclass
class InfoForm(gui.form.Form):

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        return gui.widget.CollapsingHeader()

    label: str = "Topic 1 - Text"

    message: gui.widget.Text = gui.widget.Text(
        "This is topic 1. We will just add some bullet points below ...",
    )

    bullet_1: gui.widget.Text = gui.widget.Text(
        "bullet 1 ...", bullet=True,
    )

    bullet_2: gui.widget.Text = gui.widget.Text(
        "bullet 2 ...", bullet=True,
    )


@dataclasses.dataclass
class Plotting(gui.form.Form):

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        return gui.widget.CollapsingHeader()

    label: str = "Topic 2 - Plotting"

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200,
    )

    scatter_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is scatter plot ...",
        height=200,
    )

    subplot: gui.plot.SubPlots = gui.plot.SubPlots(
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
        _line_plot_y1_axis = self.line_plot.y1_axis
        _line_plot_y1_axis(
            gui.plot.LineSeries(
                label="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        _line_plot_y1_axis(
            gui.plot.LineSeries(
                label="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        _line_plot_y1_axis(
            gui.plot.VLineSeries(x=[1.0, 2.0], label="vline 1")
        )
        _line_plot_y1_axis(
            gui.plot.VLineSeries(x=[10.0, 11.0], label="vline 2")
        )
        _line_plot_y1_axis(
            gui.plot.HLineSeries(x=[1.0, 2.0], label="hline 1")
        )
        _line_plot_y1_axis(
            gui.plot.HLineSeries(x=[10.0, 11.0], label="hline 2")
        )

        # ------------------------------------------------------- 03
        _scatter_plot_y1_axis = self.scatter_plot.y1_axis
        _scatter_plot_y1_axis(
            gui.plot.ScatterSeries(
                label="scatter 1",
                x=np.random.normal(1.0, scale=2.0, size=100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        _scatter_plot_y1_axis(
            gui.plot.ScatterSeries(
                label="scatter 2",
                x=np.random.normal(0.0, scale=2.0, size=100),
                y=np.random.normal(1.0, scale=2.0, size=100),
            )
        )

        # ------------------------------------------------------- 04
        _subplot = self.subplot
        for i in range(4):
            _plot = gui.plot.Plot(height=200)
            _subplot(widget=_plot)
            _plot_y1_axis = _plot.y1_axis
            _plot_y1_axis(
                gui.plot.LineSeries(
                    label="line 1",
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100),
                )
            )
            _plot_y1_axis(
                gui.plot.LineSeries(
                    label="line 2",
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100),
                )
            )


@dataclasses.dataclass(frozen=True)
class ButtonPlotCallback(gui.callback.Callback):

    receiver: gui.widget.ContainerWidget

    def fn(
        self,
        sender: gui.widget.Widget,
        app_data: t.Any,
        user_data: t.Union[gui.widget.Widget, t.List[gui.widget.Widget]],
    ):
        # provide type
        sender: gui.widget.Button

        # display to receiver i.e. add_child if not there
        if self.receiver.index_in_children(sender) == -1:

            # make collapsing header
            _collapsing_header = gui.widget.CollapsingHeader(
                label=sender.label,
                closable=False,
                default_open=True,
            )

            # add child to receiver
            self.receiver(widget=_collapsing_header)

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


@dataclasses.dataclass
class ButtonPlot(gui.widget.CollapsingHeader):

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


@dataclasses.dataclass
class MyDashboard(gui.dashboard.BasicDashboard):

    theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.widget.Text = gui.widget.Text(
        "Welcome to my dashboard ..... toolcraft ..... ",
    )

    topic1: InfoForm = InfoForm()

    topic2: Plotting = Plotting()

    # topic3: ButtonPlot = ButtonPlot()


def basic_dashboard():
    _dash = MyDashboard(title="My Dashboard")
    # _dash.topic2.plot_some_examples()
    _dash.run()


def demo():
    """
    Refer
    >>> from dearpygui import demo
    """

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    _demo.show_demo()

    # with dpg.window(label="Dear PyGui Demo", width=800, height=800,
    #                 pos=(100, 100), tag="__demo_id"):
    #     with dpg.collapsing_header(label="some label", default_open=True,):
    #         dpg.add_text(default_value="Some text")

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    basic_dashboard()
    # demo()


if __name__ == "__main__":
    main()
