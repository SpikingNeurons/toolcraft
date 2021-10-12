import numpy as np
import typing as t

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]

from .core import Table, Plot
from .auto import Window, SubPlot, DragLine, DragPoint, Child
from .auto import TableSizing, PlotColormap, PlotMarker
from .auto import Row, Column, Legend, XAxis, YAxis, ColorMapScale
from .auto import Group, Tab, TabBar, TabButton, Combo, Button, Text, Separator
from .auto import CheckBox, InputIntX, InputInt, CollapsingHeader, InSameLine
from .auto import SliderInt, SliderIntX, SliderFloat, SliderFloatX, Slider3D
