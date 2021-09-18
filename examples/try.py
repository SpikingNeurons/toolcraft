import dataclasses
import datetime
import time
import typing as t

import numpy as np
import pyarrow as pa
from dearpygui import core as dpg

from toolcraft import gui
from toolcraft import storage as s
from toolcraft import util


a = np.zeros((2, 3, 4, 5), dtype=np.uint8)
pa_a = util.np_to_pa(a)
_a = util.pa_to_np(pa_a)
print(a.shape, a.dtype)
print(_a.shape, _a.dtype)

tt = pa.table({"a": pa_a})
