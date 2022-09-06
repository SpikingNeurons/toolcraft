import asyncio
import itertools
import typing as t

from . import widget, Hashable

# noinspection PyUnresolvedReferences, PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from ..marshalling import HashableClass


async def make_async_fn_runner(
    receiver_grp: "widget.Group", blocking_fn: t.Callable,
):
    """
    to be used by `_make_async`
    """
    # noinspection PyUnresolvedReferences
    from .. import gui

    # get reference
    _msg = f"Running fn {blocking_fn.__name__!r} in async \n"
    _blinker = itertools.cycle(["..", "....", "......"])

    try:

        # schedule blocking task to run in queue
        _blocking_task = gui.BlockingTask(
            fn=blocking_fn, concurrent=False
        )
        _blocking_task.add_to_task_queue()
        _future = None
        while _future is None:
            await asyncio.sleep(0.4)
            _future = _blocking_task.future

        # loop infinitely
        while receiver_grp.does_exist:

            # if not build continue
            if not receiver_grp.is_built:
                await asyncio.sleep(0.4)
                continue

            # dont update if not visible
            # todo: can we await on bool flags ???
            if not receiver_grp.is_visible:
                await asyncio.sleep(0.4)
                continue

            # clear group
            receiver_grp.clear()

            # if running
            if _future.running():
                with receiver_grp:
                    gui.widget.Text(
                        default_value=_msg + next(_blinker)
                    )
                await asyncio.sleep(0.4)
                continue

            # if done
            if _future.done():
                _exp = _future.exception()
                if _exp is None:
                    receiver_grp(widget=_future.result())
                    break
                else:
                    with receiver_grp:
                        gui.widget.Text(default_value="Failed ...")
                        gui.widget.Text(default_value=str(_exp))
                    raise _exp

    except Exception as _e:
        if receiver_grp.does_exist:
            raise _e
        else:
            ...


def tab_bar_from_widget_dict(widget_dict: t.Dict) -> widget.TabBar:
    _tab_bar = widget.TabBar()
    for _k, _v in widget_dict.items():
        _tab = widget.Tab(label=_k)
        _tab_bar(widget=_tab)
        if isinstance(_v, dict):
            _tab(tab_bar_from_widget_dict(_v))
        elif isinstance(_v, list):
            for _i, __v in enumerate(_v):
                _tab(widget=__v)
        elif isinstance(_v, widget.Widget):
            if _v.registered_as_child:
                _tab(widget=_v)
            else:
                raise Exception(
                    f"Widget of type {type(_v)} cannot be added as child ...."
                )
        else:
            raise Exception(
                f"Unrecognized type {type(_v)}"
            )
    return _tab_bar


def tab_bar_from_hashable_callables(
    title: str,
    hashable: t.Union[Hashable, "HashableClass"],
    callable_names: t.Dict[str, str],
) -> widget.TabBar:
    # tab bar
    _tab_bar = widget.TabBar(label=title)
    # loop over callable names
    for k, v in callable_names.items():
        _ret_widget = getattr(hashable, v)()
        _tab = widget.Tab(label=k)
        _tab(widget=_ret_widget)
        _tab_bar(widget=_tab)
    # return
    return _tab_bar
