import asyncio
import dataclasses
import typing as t
import sys
import time

sys.path.append("..")

import dearpygui.dearpygui as dpg
from toolcraft.gui import _demo, USER_DATA
import numpy as np
from toolcraft import gui, util, logger
from toolcraft import marshalling as m

_LOGGER = logger.get_logger()

_LOGGER.info(msg="try gui ...")


@dataclasses.dataclass
class InfoForm(gui.form.Form):

    title: str = "Info"

    collapsing_header_open: bool = False

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

    title: str = "Plotting"

    collapsing_header_open: bool = False

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

    def plot_some_examples(self):
        # ------------------------------------------------------- 01
        # _simple_plot
        # todo: add the simple plot form dpg
        ...

        # ------------------------------------------------------- 02
        # _line_plot
        _ = self.line_plot.x_axis
        _ = self.line_plot.legend
        with self.line_plot.y1_axis:
            gui.plot.LineSeries(
                label="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
            gui.plot.LineSeries(
                label="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
            gui.plot.VLineSeries(x=[1.0, 2.0], label="vline 1")
            gui.plot.VLineSeries(x=[10.0, 11.0], label="vline 2")
            gui.plot.HLineSeries(x=[1.0, 2.0], label="hline 1")
            gui.plot.HLineSeries(x=[10.0, 11.0], label="hline 2")

        # ------------------------------------------------------- 03
        # scatter plot
        with self.scatter_plot.y1_axis:
            gui.plot.ScatterSeries(
                label="scatter 1",
                x=np.random.normal(1.0, scale=2.0, size=100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
            gui.plot.ScatterSeries(
                label="scatter 2",
                x=np.random.normal(0.0, scale=2.0, size=100),
                y=np.random.normal(1.0, scale=2.0, size=100),
            )

        # ------------------------------------------------------- 04
        # sub plots
        with self.subplot:
            for i in range(4):
                _plot = gui.plot.Plot(height=200)
                with _plot.y1_axis:
                    gui.plot.LineSeries(
                        label="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100),
                    )
                    gui.plot.LineSeries(
                        label="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100),
                    )


@dataclasses.dataclass
class PlottingWithUpdates(gui.form.Form):

    title: str = "Plotting with updates"

    collapsing_header_open: bool = False

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200, width=-1, num_of_y_axis=1,
    )

    lines_count: int = 0

    @property
    @util.CacheResult
    def form_fields_container(self) -> gui.widget.Group:
        _grp = gui.widget.Group()
        _grp(self.create_button_bar())
        return _grp

    @property
    @util.CacheResult
    def add_button(self) -> gui.widget.Button:

        @dataclasses.dataclass(frozen=True)
        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _form.lines_count += 1
                _l = f"line {_form.lines_count}"
                _ls = gui.plot.LineSeries(
                    label=_l,
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100),
                )
                _y1_axis = _form.line_plot.y1_axis
                _y1_axis(_ls)
                _ls_ks = [_.label for _ in _y1_axis.children.values()]
                _form.combo_select.items = _ls_ks
                _form.combo_select.default_value = _ls_ks[-1]

        _button = gui.widget.Button(
            label="Add", callback=__Callback(), user_data={"form": self},
        )
        return _button

    @property
    @util.CacheResult
    def clear_button(self) -> gui.widget.Button:

        @dataclasses.dataclass(frozen=True)
        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
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

        @dataclasses.dataclass(frozen=True)
        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _y1_axis = _form.line_plot.y1_axis
                _combo_select_value = _form.combo_select.get_value()
                if _combo_select_value == '':
                    return
                _plot_series = _y1_axis[_combo_select_value]
                _plot_series.x = np.arange(100)
                _plot_series.y = np.random.normal(0.0, scale=2.0, size=100)

        _button = gui.widget.Button(
            label="Update", callback=__Callback(), user_data={"form": self},
        )

        return _button

    @property
    @util.CacheResult
    def delete_button(self) -> gui.widget.Button:

        @dataclasses.dataclass(frozen=True)
        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _y1_axis = _form.line_plot.y1_axis
                _combo_select_value = _form.combo_select.get_value()
                if _combo_select_value == '':
                    return
                _y1_axis[_combo_select_value].delete()
                _ls_ks = [_.label for _ in _y1_axis.children.values()]
                _form.combo_select.items = _ls_ks
                try:
                    _form.combo_select.default_value = _ls_ks[-1]
                except IndexError:
                    _form.combo_select.default_value = ''

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


@dataclasses.dataclass
class MyText(gui.widget.Text):

    some_value: str = None

    def init(self):
        super().init()

    def update(self):

        self.set_value(f"{int(self.get_value()) + 1:03d}")

        if self.some_value == "first hashable ...":
            if int(self.get_value()) == 3:
                self.sleep()
            else:
                self.sleep(2)
        else:
            if int(self.get_value()) == 10:
                self.sleep()
            else:
                self.sleep(0.5)


@dataclasses.dataclass
class AwaitableTask(gui.AsyncTask):

    txt_widget: gui.widget.Text
    some_value: str

    async def awaitable_fn(self):
        # get reference
        widget = self.txt_widget

        try:

            # loop infinitely
            while widget.does_exist:

                # if not build continue
                if not widget.is_built:
                    continue

                # dont update if not visible
                # todo: can we await on bool flags ???
                if not widget.is_visible:
                    await asyncio.sleep(0.2)
                    continue

                # update widget
                widget.set_value(f"{int(widget.get_value())+1:03d}")

                # change update rate based on some value
                if self.some_value == "first hashable ...":
                    await asyncio.sleep(1)
                    if int(widget.get_value()) == 10:
                        break
                else:
                    await asyncio.sleep(0.1)
                    if int(widget.get_value()) == 50:
                        break

        except Exception as _e:
            if widget.does_exist:
                raise _e
            else:
                ...


@dataclasses.dataclass(frozen=True)
class SimpleHashableClass(m.HashableClass):

    some_value: str

    @property
    def all_plots_gui_label(self) -> str:
        return f"{self.__class__.__name__}.{self.hex_hash}\n" \
               f" >> some_value - {self.some_value}"

    @m.UseMethodInForm(label_fmt="update")
    def update(self) -> gui.widget.Group:
        _grp = gui.widget.Group(horizontal=True)
        with _grp:
            gui.widget.Text(default_value="count")
            _txt = gui.widget.Text(default_value="000")
            AwaitableTask(txt_widget=_txt, some_value=self.some_value).add_to_task_queue()
        return _grp

    # @m.UseMethodInForm(label_fmt="async_update", call_as_async=True)
    # def async_update(self) -> gui.widget.Widget:
    #     time.sleep(5)
    #     return gui.widget.Text(default_value="I am done in 5 seconds ...")

    @m.UseMethodInForm(label_fmt="line")
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

    @m.UseMethodInForm(label_fmt="scatter")
    def some_scatter_plot(self) -> gui.plot.Plot:
        _plot = gui.plot.Plot(
            label=f"This is scatter plot for {self.some_value}",
            height=200, width=-1,
        )
        _plot_y1_axis = _plot.y1_axis
        _plot_y1_axis(
            gui.plot.ScatterSeries(
                label="scatter 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        _plot_y1_axis(
            gui.plot.ScatterSeries(
                label="scatter 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100),
            )
        )
        return _plot

    @m.UseMethodInForm(
        label_fmt="all_plots_gui_label"
    )
    def all_plots(self) -> gui.form.HashableMethodsRunnerForm:
        return gui.form.HashableMethodsRunnerForm(
            title=self.all_plots_gui_label,
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["some_line_plot",  "some_scatter_plot", "update", ],
            collapsing_header_open=True,
        )


@dataclasses.dataclass
class MyDoubleSplitForm(gui.form.DoubleSplitForm):

    title: str = "Double split form ..."
    callable_name: str = "all_plots"
    allow_refresh: bool = False
    collapsing_header_open: bool = False


@dataclasses.dataclass
class MyDashboard(gui.dashboard.BasicDashboard):

    theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.widget.Text = gui.widget.Text(
        "Welcome to my dashboard ..... toolcraft ..... ",
    )

    topic1: InfoForm = InfoForm()

    topic2: Plotting = Plotting()

    topic3: PlottingWithUpdates = PlottingWithUpdates()

    topic4: gui.form.DoubleSplitForm = MyDoubleSplitForm()

    topic5: gui.form.ButtonBarForm = gui.form.ButtonBarForm(title="Button bar form ...", collapsing_header_open=False)


def basic_dashboard():
    _dash = MyDashboard(title="My Dashboard")
    _dash.topic2.plot_some_examples()
    # noinspection PyTypeChecker
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="first hashable ..."),
        group_key="Group 1 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="second hashable ..."),
        group_key="Group 1 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="third hashable ..."),
        group_key="Group 2 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic4.add(
        hashable=SimpleHashableClass(some_value="fourth hashable ..."),
        group_key="Group 2 ..."
    )
    _dash.topic5.register(key="aaa", gui_name="a...", fn=lambda: gui.widget.Text("aaa..."))
    _dash.topic5.register(key="bbb", gui_name="b...", fn=lambda: gui.widget.Text("bbb..."))
    _dash.topic5.register(key="ccc", gui_name="c...", fn=lambda: gui.widget.Text("ccc..."))

    gui.Engine.run(_dash)


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
