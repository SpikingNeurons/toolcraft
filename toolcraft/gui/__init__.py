"""
todo: Separate gui module in new package so that
  + there are few dependencies ... like dearpygui and on rest/grpc api access library
  + can be deployed as exe using pyinstaller, Nuitka
"""
import typing as t

try:
    import dearpygui.dearpygui as dpg
    DPG_WORKS = True
    # todo: instead of import call some code in dearpygui to raise errors ... so that in except block
    #   we can set `DPG_WORKS = False`
except ImportError:
    DPG_WORKS = False

if DPG_WORKS:
    from .__base__ import COLOR_TYPE, PLOT_DATA_TYPE, USER_DATA, Engine, AwaitableTask, BlockingTask, \
        Hashable, UseMethodInForm, EscapeWithContext
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
    try:
        # noinspection PyUnresolvedReferences
        from . import dl
    except ImportError:
        ...
else:

    # fake class that does nothing and alternative to `__base__.UseMethodInForm`
    # when dpg is not available ....
    # This allows to use UseMethodInForm when dpg is not available as a decorator
    # Note that it does nothing and if decorated method called then it will raise error that
    # dpg cannot be used as this is server side code
    class UseMethodInForm:
        def __init__(
            self,
            label_fmt: str = None,
            run_async: bool = False,
            allow_refresh: bool = None,
            display_in_form: bool = True,
        ):
            ...

        def __call__(self, fn: t.Callable):

            def _fn(*args, **kwargs):
                raise Exception(
                    "Looks like you are running on server where dearpygui is not available",
                    "Avoid calling any gui code on server ...",
                    f"Check decorated function {fn}",
                )
            return _fn
