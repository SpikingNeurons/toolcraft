"""
Call using run_runner.py
Eventually we need to call this from toolcraft cli i.e. when we install it via pip
"""
import dataclasses
import sys
import numpy as np
sys.path.append("..\\..")
from toolcraft import marshalling as m
from toolcraft import dapr, gui, logger


_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class Test(m.HashableClass):

    some_value: str

    @property
    def all_plots_gui_label(self) -> str:
        return f"{self.__class__.__name__}.{self.hex_hash} (all_plots)\n" \
               f" >> some_value - {self.some_value}"

    @m.UseMethodInForm(label_fmt="all_plots_gui_label")
    def all_plots(self) -> gui.form.HashableMethodsRunnerForm:
        return gui.form.HashableMethodsRunnerForm(
            title=f"SimpleHashable method's runner form for {self.some_value}",
            group_tag="simple",
            hashable=self,
            close_button=True,
            info_button=True,
            callable_names=["some_line_plot",  "some_scatter_plot"],
            use_collapsing_header=True,
        )

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

    def run(self):
        _LOGGER.info(f"Running task for {self.some_value}")


_TASKS = [
    Test("f1"), Test("f2"), Test("f3"), Test("f4"),
]


class HashableRunner(dapr.HashableRunner):

    @classmethod
    def launch(cls):
        # call super
        super().launch()

        for _t in _TASKS:
            _t.run()



if __name__ == '__main__':
    HashableRunner.run()
