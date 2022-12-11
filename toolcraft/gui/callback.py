import dataclasses
import typing as t

from . import widget, asset, util, AwaitableTask, helper, UseMethodInForm
from .__base__ import Callback, EnColor, Engine, Hashable

# noinspection PyUnreachableCode
if False:
    from ..marshalling import HashableClass


@dataclasses.dataclass
class SetThemeCallback(Callback):
    """
    todo: we will get rid of this callback in favour of assets module ...
      once we understand theme, icon, font, background, color etc styling
      related things
    """

    @staticmethod
    def themes() -> t.List[str]:
        return [
            "Dark", "Light",
            # "Classic",
            # "Dark 2", "Grey", "Purple",
            # "Dark Grey", "Cherry", "Gold", "Red"
        ]

    @staticmethod
    def default_theme() -> str:
        return "Dark"

    @classmethod
    def get_combo_widget(cls) -> widget.Combo:
        return widget.Combo(
            items=cls.themes(),
            default_value=cls.default_theme(),
            callback=cls(),
            label="Select Theme"
        )

    def fn(self, sender: widget.Widget):
        _theme_str = sender.get_value()
        if _theme_str == "Dark":
            _theme = asset.Theme.DARK
        elif _theme_str == "Light":
            _theme = asset.Theme.LIGHT
        else:
            raise Exception(f"unknown theme {_theme_str}")
        # we change theme of parent to which this Combo widget is child
        sender.parent.bind_theme(theme=_theme)


@dataclasses.dataclass
class CallFnCallback(Callback):

    def get_button_widget(
        self, label: str, call_fn: t.Callable, call_fn_kwargs: t.Dict[str, t.Any] = None
    ) -> widget.Button:
        return widget.Button(
            label=label,
            callback=self,
            user_data={'call_fn': call_fn, 'call_fn_kwargs': call_fn_kwargs},
        )

    def fn(self, sender: widget.Widget):
        try:
            _call_fn = sender.get_user_data()['call_fn']
            _call_fn_kwargs = sender.get_user_data()['call_fn_kwargs']
            if _call_fn_kwargs is None:
                _call_fn_kwargs = dict()
            _call_fn(**_call_fn_kwargs)
        except KeyError:
            raise KeyError(
                f"Was expecting you to supply dict item 'call_fn' or `call_fn_kwargs` in "
                f"`user_data` of sender {sender.__class__}"
            )


@dataclasses.dataclass
class CloseWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete the widget supplied
    """

    @classmethod
    def get_button_widget(
        cls, widget_to_delete: widget.Widget, label: str ="Close [X]",
    ) -> widget.Button:
        # return widget.ColorButton(
        #     default_value=EnColor.RED.value,
        #     label=label,
        #     callback=cls(),
        #     user_data={'widget_to_delete': widget_to_delete},
        # )
        _ret = widget.Button(
            label=label,
            callback=cls(),
            user_data={'widget_to_delete': widget_to_delete},
        )
        return _ret

    def fn(self, sender: widget.Widget):
        _user_data = sender.get_user_data()
        if 'widget_to_delete' in _user_data.keys():
            print("Deleting via Close [X]", sender.get_user_data()['widget_to_delete'])
            sender.get_user_data()['widget_to_delete'].delete()
        else:
            raise KeyError(
                f"Was expecting you to supply dict item `widget_to_delete` in "
                f"`user_data` of sender {sender.__class__}"
            )


@dataclasses.dataclass
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.
    """
    hashable: t.Union[Hashable, "HashableClass"]
    callable_name: str
    receiver: widget.ContainerWidget

    def init(self):
        # call super
        super().init()

        # _use_method_in_form_obj
        # noinspection PyAttributeOutsideInit
        self._use_method_in_form_obj = UseMethodInForm.get_from_hashable_fn(
            hashable=self.hashable, fn_name=self.callable_name
        )

    def init_validate(self):
        # call super
        super().init_validate()

        # check i fuser_data is set to dict in receiver
        _user_data = self.receiver.get_user_data()
        if not isinstance(_user_data, dict):
            raise Exception("We expect that you set user_data to dict in receiver ...")

    def fn(self, sender: widget.Widget):
        # ------------------------------------------------------------------ 01
        # initial stuff
        # ------------------------------------------------------------------ 01.01
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        _callable_name = self.callable_name
        _user_data = _receiver.get_user_data()
        _use_method_in_form_obj = self._use_method_in_form_obj
        _tag_in_receiver = _use_method_in_form_obj.tag_in_receiver
        _run_async = _use_method_in_form_obj.run_async
        _hide_previously_opened = _use_method_in_form_obj.hide_previously_opened
        # ------------------------------------------------------------------ 01.02
        # Remove stale widgets from `_user_data` that might have been deleted from other gui interactions
        # We detect stale if those widgets are not available in `_receiver.children`
        # This is because we cannot delete them from `_use_data` when `_widget.delete()` is called
        for _t, _guid in [(_k, _v.guid) for _k, _v in _user_data.items()]:
            if _guid not in _receiver.children.keys():
                del _user_data[_t]

        # ------------------------------------------------------------------ 02
        # check if dashboard same
        # .... doesn't matter if you use sender or _receiver as there is one dashboard for all
        #      This might change if we have multiple dashboard instances
        # todo: we are using Engine we do not need this
        # todo: precaution check ... remove later
        assert id(_receiver.dash_board) == id(sender.dash_board), "must be same ..."

        # ------------------------------------------------------------------ 03
        # create tag
        _actual_tag = _tag_in_receiver
        if _actual_tag == 'auto':
            _actual_tag = f"{_hashable.hex_hash}.{_callable_name}"
        if _actual_tag is None:
            _actual_tag = "_NONE_"

        # ------------------------------------------------------------------ 04
        # get widget and after_widget
        # ------------------------------------------------------------------ 04.01
        # some vars
        # noinspection PyTypeChecker
        _widget: widget.MovableWidget = None
        # noinspection PyTypeChecker
        _after_widget: widget.MovableWidget = None
        # ------------------------------------------------------------------ 04.02
        # get widget if already present in user_data
        if _actual_tag in _user_data.keys():
            # get cached _widget
            # noinspection PyTypeChecker
            _widget = _user_data[_actual_tag]
        # ------------------------------------------------------------------ 04.03
        # + we are assuming this will be MovableWidget ... Note that we want to
        #   keep this way and if possible modify other code ... this is possible
        #   for container widgets, and we do not see that this callback will be
        #   used for non-movable Widgets
        try:
            _after_widget = _widget.after()
        except AttributeError:
            ...

        # ------------------------------------------------------------------ 05
        # hide all things in _user_data
        if _hide_previously_opened:
            for _ in _user_data.values():
                _.hide_widget()

        # ------------------------------------------------------------------ 06
        # if above steps results in widget then that means there is a cached widget which we can reuse or overwrite
        # but in case of `tag_in_receiver` is not `auto` then that means that user wants to overwrite previous tag
        if _widget is not None:
            # -------------------------------------------------------------- 06.01
            # if `self.tag_in_receiver` is `auto` than show widget that was hidden in step 05
            if _tag_in_receiver == 'auto':
                _widget.show_widget()
            # -------------------------------------------------------------- 06.02
            # if `self.tag_in_receiver` is None or some `str` that means we want to overwrite
            elif _tag_in_receiver is None or _tag_in_receiver != 'auto':
                # delete tag from receiver
                del _user_data[_actual_tag]
                # delete widget
                # this will delete itself
                # this will also remove itself from `parent.children`
                _widget.delete()
                # set back to None so that it can be recreated
                # noinspection PyTypeChecker
                _widget = None
            # -------------------------------------------------------------- 06.03
            # else raise exception
            else:
                raise Exception(f"Unknown {_tag_in_receiver}")

        # ------------------------------------------------------------------ 07
        # if _widget is None generate it and then tag it
        if _widget is None:
            # -------------------------------------------------------------- 07.01
            # get actual result widget we are interested to display ...
            if _run_async:
                _new_widget = widget.Group(horizontal=False)
                AwaitableTask(
                    fn=helper.make_async_fn_runner,
                    fn_kwargs=dict(
                        receiver_grp=_new_widget,
                        blocking_fn=util.rgetattr(_hashable, _callable_name),
                    )
                ).add_to_task_queue()
            else:
                _new_widget = util.rgetattr(_hashable, _callable_name)()  # type: widget.MovableWidget
            # -------------------------------------------------------------- 07.02
            # tag it i.e. save it to receiver user_data as it was newly created
            _user_data[_actual_tag] = _new_widget
            # -------------------------------------------------------------- 07.03
            # also add it to receiver children
            _receiver(_new_widget)
            # -------------------------------------------------------------- 07.04
            # move widget based on _after_widget
            if _after_widget is not None:
                _new_widget.move(before=_after_widget)
