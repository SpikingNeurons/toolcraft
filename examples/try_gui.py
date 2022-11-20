import asyncio
import dataclasses
import itertools
import typing as t
import sys
import time

from toolcraft.gui.__base__ import Widget

sys.path.append("..")

import dearpygui.dearpygui as dpg
from toolcraft.gui import _demo, USER_DATA
import numpy as np
from toolcraft import gui


@dataclasses.dataclass
class InfoForm(gui.form.Form):

    label: str = "Info"

    default_open: bool = False

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

    label: str = "Plotting"

    default_open: bool = False

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
        self.scatter_plot.x_axis.set_ticks(
            (("A", -1), ("B", 0), ("C", 1))
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

    label: str = "Plotting with updates"

    default_open: bool = False

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200, width=-1, num_of_y_axis=1,
    )

    lines_count: int = 0

    def layout(self) -> gui.widget.Group:
        # ---------------------------------------------------------- 01
        # make a button bar
        _button_bar = gui.widget.Group(horizontal=True)

        # ---------------------------------------------------------- 02
        @dataclasses.dataclass
        class AddCallback(gui.callback.Callback):
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
                _form._combo_select.items = _ls_ks
                _form._combo_select.default_value = _ls_ks[-1]
        self._add_button = gui.widget.Button(
            label="Add", callback=AddCallback(), user_data={"form": self},
        )
        _button_bar(self._add_button)

        # ---------------------------------------------------------- 03
        @dataclasses.dataclass
        class ClearCallback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _form.line_plot.clear()
                _form._combo_select.items = []
                _form._combo_select.default_value = ''

        self._clear_button = gui.widget.Button(
            label="Clear", callback=ClearCallback(), user_data={"form": self},
        )
        _button_bar(self._clear_button)

        # ---------------------------------------------------------- 04
        _button_bar(gui.widget.Text(default_value=" | "))

        # ---------------------------------------------------------- 05
        self._combo_select = gui.widget.Combo(
            label="Select line series"
        )
        _button_bar(self._combo_select)

        # ---------------------------------------------------------- 06
        @dataclasses.dataclass
        class UpdateCallback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _y1_axis = _form.line_plot.y1_axis
                _combo_select_value = _form._combo_select.get_value()
                if _combo_select_value == '':
                    return
                _plot_series = None
                for _ in _y1_axis.children.values():
                    if _.label == _combo_select_value:
                        _plot_series = _
                        break
                if _plot_series is None:
                    raise Exception("should never happen ...")
                _plot_series.x = np.arange(100)
                _plot_series.y = np.random.normal(0.0, scale=2.0, size=100)
        self._update_button = gui.widget.Button(
            label="Update", callback=UpdateCallback(), user_data={"form": self},
        )
        _button_bar(self._update_button)

        # ---------------------------------------------------------- 07

        @dataclasses.dataclass
        class DeleteCallback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                # noinspection PyTypeChecker
                _form: PlottingWithUpdates = sender.get_user_data()['form']
                _y1_axis = _form.line_plot.y1_axis
                _combo_select_value = _form._combo_select.get_value()
                if _combo_select_value == '':
                    return
                _plot_series = None
                for _ in _y1_axis.children.values():
                    if _.label == _combo_select_value:
                        _plot_series = _
                        break
                if _plot_series is None:
                    raise Exception("should never happen ...")
                _plot_series.delete()
                _ls_ks = [_.label for _ in _y1_axis.children.values()]
                _form._combo_select.items = _ls_ks
                try:
                    _form._combo_select.default_value = _ls_ks[-1]
                except IndexError:
                    _form._combo_select.default_value = ''
        self._delete_button = gui.widget.Button(
            label="Delete", callback=DeleteCallback(), user_data={"form": self},
        )
        _button_bar(self._delete_button)

        # ---------------------------------------------------------- 08
        # get layout
        _layout = super().layout()
        # add to layout and return
        _layout(_button_bar)
        # move up
        _button_bar.move_up()
        # noinspection PyTypeChecker
        return _layout


@dataclasses.dataclass
class WidgetVisibleCallback(gui.callback.Callback):

    def fn(self, sender: Widget):
        print(sender, "I am Visible")


_widget_handlers = gui.registry.WidgetHandlerRegistry()
with _widget_handlers:
    gui.registry.WidgetVisibleHandler(callback=WidgetVisibleCallback())


@dataclasses.dataclass
class PlottingWithContiniousUpdates(gui.form.Form):

    label: str = "Plotting with continious updates ..."

    default_open: bool = False

    line_plot: gui.plot.Plot = gui.plot.Plot(
        label="This is line plot ...",
        height=200, width=-1,
    )

    def fixed_update(self):
        ...
        print("yyyyyyyyyyyyyyyyyyyyyyy", self.dpg_state['visible'], self.line_plot.dpg_state['visible'])
        print(self.dpg_state)
        print(self.line_plot.dpg_state)
        # _1 = self.line_plot.x_axis.get_limits()
        # _2 = self.line_plot.y1_axis.get_limits()
        # print(">>>>>>>>>>>>>>>>>>>", _1, _2)


@dataclasses.dataclass
class SimpleHashableClass(gui.Hashable):

    some_value: str
    click_count_for_blocking_fn: int = 0

    @property
    def all_plots_gui_label(self) -> str:
        return f"{self.__class__.__name__}.{self.hex_hash}\n" \
               f" >> some_value - {self.some_value}"

    @gui.UseMethodInForm(label_fmt="all_plots_gui_label")
    def all_plots(self) -> gui.form.HashableMethodsRunnerForm:
        return gui.form.HashableMethodsRunnerForm(
            label=self.all_plots_gui_label.split("\n")[0],
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["some_line_plot",  "some_scatter_plot", "awaitable_task", "blocking_task", ],
            default_open=True,
            allow_refresh=True,
        )

    async def some_awaitable_fn(self, txt_widget: gui.widget.Text):

        try:

            # loop infinitely
            while txt_widget.does_exist:

                # if not build continue
                if not txt_widget.is_built:
                    await asyncio.sleep(0.2)
                    continue

                # dont update if not visible
                # todo: can we await on bool flags ???
                if not txt_widget.is_visible:
                    await asyncio.sleep(0.2)
                    continue

                # update widget
                txt_widget.set_value(f"{int(txt_widget.get_value())+1:03d}")

                # change update rate based on some value
                if self.some_value == "first hashable ...":
                    await asyncio.sleep(1)
                    if int(txt_widget.get_value()) == 10:
                        break
                else:
                    await asyncio.sleep(0.1)
                    if int(txt_widget.get_value()) == 50:
                        break

        except Exception as _e:
            if txt_widget.does_exist:
                raise _e
            else:
                ...

    @gui.UseMethodInForm(label_fmt="awaitable_task")
    def awaitable_task(self) -> gui.widget.Group:
        _grp = gui.widget.Group(horizontal=True)
        with _grp:
            gui.widget.Text(default_value="count")
            _txt = gui.widget.Text(default_value="000")
            gui.AwaitableTask(
                fn=self.some_awaitable_fn, fn_kwargs=dict(txt_widget=_txt)
            ).add_to_task_queue()
        return _grp

    @gui.UseMethodInForm(label_fmt="blocking_task", run_async=True)
    def blocking_task(self) -> gui.widget.Text:
        time.sleep(10)
        return gui.widget.Text(default_value="done sleeping for 10 seconds")

    # @m.UseMethodInForm(label_fmt="async_update", call_as_async=True)
    # def async_update(self) -> gui.widget.Widget:
    #     time.sleep(5)
    #     return gui.widget.Text(default_value="I am done in 5 seconds ...")

    @gui.UseMethodInForm(label_fmt="line")
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

    @gui.UseMethodInForm(label_fmt="scatter")
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


@dataclasses.dataclass
class MyDoubleSplitForm(gui.form.DoubleSplitForm):

    label: str = "Double split form ..."
    callable_name: str = "all_plots"
    allow_refresh: bool = False
    default_open: bool = False


@dataclasses.dataclass
class MyDashboard(gui.dashboard.BasicDashboard):

    theme_selector: gui.widget.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.widget.Text = gui.widget.Text(
        default_value="Welcome to my dashboard ..... toolcraft ..... ",
    )

    topic1: InfoForm = InfoForm()

    topic2: Plotting = Plotting()

    topic3: PlottingWithUpdates = PlottingWithUpdates()

    topic4: PlottingWithContiniousUpdates = PlottingWithContiniousUpdates()

    topic5: gui.form.DoubleSplitForm = MyDoubleSplitForm()

    topic6: gui.form.ButtonBarForm = gui.form.ButtonBarForm(label="Button bar form ...", default_open=False)

    container: gui.widget.Group = gui.widget.Group()


def basic_dashboard():
    _dash = MyDashboard(title="My Dashboard")
    _dash.topic2.plot_some_examples()
    # noinspection PyTypeChecker
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="first hashable ..."),
        group_key="Group 1 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="second hashable ..."),
        group_key="Group 1 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="third hashable ..."),
        group_key="Group 2 ..."
    )
    # noinspection PyTypeChecker
    _dash.topic5.add(
        hashable=SimpleHashableClass(some_value="fourth hashable ..."),
        group_key="Group 2 ..."
    )
    _dash.topic6.register(key="aaa", gui_name="a...", fn=lambda: gui.widget.Text("aaa..."))
    _dash.topic6.register(key="bbb", gui_name="b...", fn=lambda: gui.widget.Text("bbb..."))
    _dash.topic6.register(key="ccc", gui_name="c...", fn=lambda: gui.widget.Text("ccc..."))
    with _dash.container:
        with gui.widget.CollapsingHeader(label="Test container") as _cc:
            _t = gui.widget.Text(default_value="first element in container ...")
            _ = gui.form.DoubleSplitForm(
                label=f"*** [[ ]] ***",
                callable_name="job_gui", allow_refresh=False, default_open=False,
            )
            _ = gui.form.ButtonBarForm(label="*** [[ ]] ***", default_open=False)

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
