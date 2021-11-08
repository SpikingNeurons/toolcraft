import dataclasses
import typing as t

import dearpygui.dearpygui as dpg
from toolcraft.gui import _demo, USER_DATA
import numpy as np
from toolcraft import gui, util, marshalling, logger

_LOGGER = logger.get_logger()

_LOGGER.info(msg="try gui ...")


@dataclasses.dataclass
class InfoForm(gui.form.Form):

    label: str = "Text"

    message: gui.widget.Text = gui.widget.Text(
        "This is topic 1. We will just add some bullet points below ...",
    )

    bullet_1: gui.widget.Text = gui.widget.Text(
        "bullet 1 ...", bullet=True,
    )

    bullet_2: gui.widget.Text = gui.widget.Text(
        "bullet 2 ...", bullet=True,
    )

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        return gui.widget.CollapsingHeader(label=self.label)


@dataclasses.dataclass
class Plotting(gui.form.Form):

    label: str = "Plotting"

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200, width=-1,
    )

    scatter_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is scatter plot ...",
        height=200, width=-1,
    )

    subplot: gui.plot.SubPlots = gui.plot.SubPlots(
        rows=2,
        columns=2,
        label="This is sub plot ...",
        height=200, width=-1,
    )

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        return gui.widget.CollapsingHeader(label=self.label)

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
        # scatter plot
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
        # sub plots
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


@dataclasses.dataclass
class PlottingWithUpdates(gui.form.Form):

    label: str = "Plotting with updates"

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200, width=-1, num_of_y_axis=1,
    )

    lines_count: int = 0

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        _ch = gui.widget.CollapsingHeader(label=self.label)
        _ch(self.create_button_bar())
        return _ch

    @property
    @util.CacheResult
    def add_button(self) -> gui.widget.Button:

        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(
                _self,
                sender: gui.widget.Widget,
                app_data: t.Any,
                user_data: USER_DATA,
            ):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = user_data['form']
                _form.lines_count += 1
                _l = f"line {_form.lines_count}"
                _ls = gui.plot.LineSeries(
                    label=_l,
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100),
                )
                _y1_axis = _form.line_plot.y1_axis
                _y1_axis(_ls)
                _ls_ks = _y1_axis.available_plot_series
                _form.combo_select.items = _ls_ks
                _form.combo_select.default_value = _ls_ks[-1]

        _button = gui.widget.Button(
            label="Add", callback=__Callback(), user_data={"form": self},
        )
        return _button

    @property
    @util.CacheResult
    def clear_button(self) -> gui.widget.Button:

        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(
                _self,
                sender: gui.widget.Widget,
                app_data: t.Any,
                user_data: USER_DATA,
            ):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = user_data['form']
                _form.line_plot.clear()
                _form.combo_select.items = []
                _form.combo_select.default_value = ''

        _button = gui.widget.Button(
            label="Clear", callback=__Callback(), user_data={"form": self},
        )
        return _button

    @property
    @util.CacheResult
    def combo_select(self) -> gui.widget.Combo:
        _combo_select = gui.widget.Combo(
            label="Select line series"
        )
        return _combo_select

    @property
    @util.CacheResult
    def update_button(self) -> gui.widget.Button:
        _button = gui.widget.Button(
            label="Update"
        )
        return _button

    @property
    @util.CacheResult
    def delete_button(self) -> gui.widget.Button:

        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(
                _self,
                sender: gui.widget.Widget,
                app_data: t.Any,
                user_data: USER_DATA,
            ):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = user_data['form']
                # self.line_plot.clear()
                # self.combo_select.items = []
                # self.combo_select.default_value = ''
                print("delete ....")
                print(sender)
                print(sender.get_value())
                print(app_data)
                print(user_data)

        _button = gui.widget.Button(
            label="Delete", callback=__Callback(), user_data={"form": self},
        )
        return _button

    # noinspection PyMethodMayBeStatic
    def create_button_bar(self) -> gui.widget.Group:
        _button_bar = gui.widget.Group(horizontal=True)

        _button_bar(self.add_button)
        _button_bar(self.clear_button)
        _button_bar(gui.widget.Text(default_value=" | "))
        _button_bar(self.combo_select)
        _button_bar(self.update_button)
        _button_bar(self.delete_button)

        return _button_bar

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


@dataclasses.dataclass(frozen=True)
class SimpleHashableClass(marshalling.HashableClass):

    some_value: str

    def all_plots(self) -> gui.form.HashableMethodsRunnerForm:
        return gui.form.HashableMethodsRunnerForm(
            title=f"SimpleHashable method's runner form for {self.some_value}",
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["some_line_plot", "some_scatter_plot"],
            callable_labels=["line", "scatter"],
        )

    def some_line_plot(self) -> gui.plot.Plot:
        _plot = gui.plot.Plot(
            label=f"This is line plot for {self.some_value}",
            height=200, width=-1,
        )
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
        return _plot

    def some_scatter_plot(self) -> gui.plot.Plot:
        _plot = gui.plot.Plot(
            label=f"This is scatter plot for {self.some_value}",
            height=200, width=-1,
        )
        _plot_y1_axis = _plot.y1_axis
        _plot_y1_axis(
            gui.plot.ScatterSeries(
                label="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        _plot_y1_axis(
            gui.plot.ScatterSeries(
                label="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        return _plot


@dataclasses.dataclass
class SimpleHashablesMethodRunnerForm(gui.form.HashablesMethodRunnerForm):

    title: str = "SimpleHashable's method runner form"
    callable_name: str = "some_line_plot"
    allow_refresh: bool = False

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        _collapse_header = gui.widget.CollapsingHeader(label=self.title)
        _ret = super().form_fields_container
        _collapse_header(_ret)
        return _collapse_header


@dataclasses.dataclass
class SimpleHashablesMethodsRunnerForm(gui.form.HashablesMethodRunnerForm):

    title: str = "SimpleHashable's method's runner form"
    callable_name: str = "all_plots"
    allow_refresh: bool = False

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.CollapsingHeader:
        _collapse_header = gui.widget.CollapsingHeader(label=self.title)
        _ret = super().form_fields_container
        _collapse_header(_ret)
        return _collapse_header


@dataclasses.dataclass
class MyDashboard(gui.dashboard.BasicDashboard):

    theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.widget.Text = gui.widget.Text(
        "Welcome to my dashboard ..... toolcraft ..... ",
    )

    topic1: InfoForm = InfoForm()

    topic2: Plotting = Plotting()

    topic3: PlottingWithUpdates = PlottingWithUpdates()

    topic4: SimpleHashablesMethodRunnerForm = SimpleHashablesMethodRunnerForm(
        allow_refresh=True
    )

    topic5: SimpleHashablesMethodsRunnerForm = SimpleHashablesMethodsRunnerForm(
        allow_refresh=True
    )


def basic_dashboard():
    _dash = MyDashboard(title="My Dashboard")
    _dash.topic2.plot_some_examples()
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="first hashable ...")
    )
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="second hashable ...")
    )
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="third hashable ...")
    )
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="fourth hashable ...")
    )
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="first hashable ...")
    )
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="second hashable ...")
    )
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
