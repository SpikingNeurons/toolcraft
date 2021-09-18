import dataclasses
import numpy as np
import time
import datetime
import typing as t
from dearpygui import core as dpg
import pyarrow as pa

from toolcraft import gui, util
from toolcraft import storage as s


a = np.zeros((2, 3, 4, 5), dtype=np.uint8)
pa_a = util.np_to_pa(a)
_a = util.pa_to_np(pa_a)
print(a.shape, a.dtype)
print(_a.shape, _a.dtype)

tt = pa.table({'a': pa_a})


