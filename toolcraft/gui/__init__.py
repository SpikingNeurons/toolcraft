"""
todo: Separate gui module in new package so that
  + there are few dependencies ... like dearpygui and on rest/grpc api access library
  + can be deployed as exe using pyinstaller, Nuitka
"""

from .__base__ import COLOR_TYPE, PLOT_DATA_TYPE, USER_DATA, Tag
from ._enum import *
from . import window
from . import widget
from . import table
from . import plot
from . import form
from . import callback
from . import dashboard
from . import asset
from . import helper
