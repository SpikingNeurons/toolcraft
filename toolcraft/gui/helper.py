import asyncio
import itertools
import typing as t

from . import widget, Hashable, EscapeWithContext

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
    from . import BlockingTask, widget

    # get reference
    _cnt = 0
    _msg = f"Running fn {blocking_fn.__name__!r} in async {{cnt:03d}}\n"
    _blinker = itertools.cycle(["..", "....", "......"])

    # launch task
    try:

        # schedule blocking task to run in queue
        # todo: we are using `concurrent=True` as widgets dynamically added are available
        #   although `concurrent=False` will launch new process the widgets get rendered but
        #   cannot be deleted by clear ...
        _blocking_task = BlockingTask(fn=blocking_fn, concurrent=True)
        _blocking_task.add_to_task_queue()
        _future = None
        while _future is None:
            await asyncio.sleep(0.4)
            _future = _blocking_task.future

        # add blink widget
        with receiver_grp:
            _blink_widget = widget.Text(default_value=f"...")

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

            # if running
            if _future.running():
                _cnt += 1
                _blink_widget.default_value = _msg.format(cnt=_cnt) + next(_blinker)
                await asyncio.sleep(0.4)

                # continue
                continue

            # if done
            if _future.done():
                _exp = _future.exception()
                if _exp is None:
                    _result = _future.result()
                    if not isinstance(_result, widget.Widget):
                        raise Exception(
                            f"Expecting {blocking_fn.__name__} to return {widget.Widget}, "
                            f"but found type {type(_result)}"
                        )
                    _blink_widget.default_value = f"Successfully adding widget: [{_result}]"
                    receiver_grp(widget=_result)
                    break
                else:
                    _blink_widget.default_value = "Failed ..."
                    with receiver_grp:
                        widget.Text(default_value=str(_exp))
                    raise _exp

    except Exception as _e:
        if receiver_grp.does_exist:
            raise _e
        else:
            ...


def tab_bar_from_widget_dict(widget_dict: t.Dict, label: str = None) -> widget.TabBar:
    _tab_bar = widget.TabBar(label=label)
    for _k, _v in widget_dict.items():
        with _tab_bar:
            _tab = widget.Tab(label=_k)
        if isinstance(_v, dict):
            _tab(tab_bar_from_widget_dict(_v, label=_k))
        elif isinstance(_v, list):
            for __v in _v:
                if __v.registered_as_child:
                    _tab(widget=__v)
                else:
                    raise Exception(
                        f"Widget of type {type(__v)} cannot be added as child ...."
                    )
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
