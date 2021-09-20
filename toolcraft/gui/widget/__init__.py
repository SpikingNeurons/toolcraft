import typing as t

import numpy as np

from .auto import (
    Button,
    CheckBox,
    Child,
    CollapsingHeader,
    ColorMap,
    ColorMapScale,
    Column,
    Combo,
    DragLine,
    DragPoint,
    Group,
    InputInt,
    InputIntX,
    InSameLine,
    Legend,
    Marker,
    Row,
    Separator,
    Slider3D,
    SliderFloat,
    SliderFloatX,
    SliderInt,
    SliderIntX,
    SubPlot,
    Tab,
    TabBar,
    TabButton,
    TableSizingPolicy,
    Text,
    Window,
    XAxis,
    YAxis,
)
from .core import Plot, Table

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]
