"""
todo: Separate gui module in new package so that
  + there are few dependencies ... like dearpygui and on rest/grpc api access library
  + can be deployed as exe using pyinstaller, Nuitka
"""
try:
    from .__base__ import \
        COLOR_TYPE, \
        PLOT_DATA_TYPE, \
        USER_DATA, \
        Engine, \
        AwaitableTask, \
        BlockingTask, \
        Hashable, \
        UseMethodInForm, \
        EscapeWithContext
    from ._enum import *
    from . import widget
    from . import window
    from . import table
    from . import plot
    from . import form
    from . import callback
    from . import registry
    from . import dashboard
    from . import asset
    from . import helper
except ImportError:
    import typing as t
    import warnings

    warnings.warn("Dearpygui lib cannot work ... view related things will not work on this machine")

    class UseMethodInForm:
        def __init__(self, *args, **kwargs):
            ...

        def __call__(self, fn: t.Callable):
            return fn
