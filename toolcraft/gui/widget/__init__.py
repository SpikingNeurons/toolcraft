import typing as t

import numpy as np

from .auto import Button
from .auto import CheckBox
from .auto import Child
from .auto import CollapsingHeader
from .auto import ColorMap
from .auto import ColorMapScale
from .auto import Column
from .auto import Combo
from .auto import DragLine
from .auto import DragPoint
from .auto import Group
from .auto import InputInt
from .auto import InputIntX
from .auto import InSameLine
from .auto import Legend
from .auto import Marker
from .auto import Row
from .auto import Separator
from .auto import Slider3D
from .auto import SliderFloat
from .auto import SliderFloatX
from .auto import SliderInt
from .auto import SliderIntX
from .auto import SubPlot
from .auto import Tab
from .auto import TabBar
from .auto import TabButton
from .auto import TableSizingPolicy
from .auto import Text
from .auto import Window
from .auto import XAxis
from .auto import YAxis
from .core import Plot
from .core import Table


PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]
