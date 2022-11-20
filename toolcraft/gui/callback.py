import dataclasses
import typing as t

from . import widget, asset, util, AwaitableTask, helper
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

    tag:
    + If `tag` is specified then that means you want to add a widget to receiver and replace it with any other
      widget for future callback requests. this allows replacing existing widgets in receiver.
    + Note that when tag is used then allow_refresh must be true as will anyway refresh widget i.e. delete
      it and then render again.
    + If tag is not specified then we will make tag that is based on hashable and callable name. While allow_refresh
      will decide if the widget should be rendered everytime the callback gets called ... Note that as the tags
      will be very unique we can have allow_refresh to be false as the receiver container will stack all the widgets.
    """
    hashable: t.Union[Hashable, "HashableClass"]
    callable_name: str
    receiver: widget.ContainerWidget
    allow_refresh: bool
    receiver_tag: str = None
    run_async: bool = False

    def init_validate(self):
        # call super
        super().init_validate()

        # if tag is not provided then allow_refresh must be True
        # this is because to overwrite old is nothing but refreshing everytime
        if self.receiver_tag is not None:
            if not self.allow_refresh:
                raise Exception(
                    f"looks like you are using tag. So please "
                    f"ensure that allow_refresh is set to True as multiple widgets get mapped to same tag"
                )

        # check i fuser_data is set to dict in receiver
        _user_data = self.receiver.get_user_data()
        if not isinstance(_user_data, dict):
            raise Exception("We expect that you set user_data to dict in receiver ...")

    def fn(self, sender: widget.Widget):
        # ------------------------------------------------------------------ 01
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        _user_data = _receiver.get_user_data()

        # ------------------------------------------------------------------ 02
        # check if dashboard same
        # .... doesn't matter if you use sender or _receiver as there is one dashboard for all
        #      This might change if we have multiple dashboard instances
        # todo: we are using Engine we do not need this
        # todo: precaution check ... remove later
        assert id(_receiver.dash_board) == id(sender.dash_board), "must be same ..."

        # ------------------------------------------------------------------ 03
        # create tag
        _tag = self.receiver_tag
        if _tag is None:
            _tag = f"{_hashable.hex_hash}.{self.callable_name}"

        # ------------------------------------------------------------------ 04
        # get/delete widget and after_widget
        # ------------------------------------------------------------------ 04.01
        # some vars
        # noinspection PyTypeChecker
        _widget: widget.MovableWidget = None
        # noinspection PyTypeChecker
        _after_widget: widget.MovableWidget = None
        # ------------------------------------------------------------------ 04.02
        # get widget if already present in user_data
        if _tag in _user_data.keys():
            # noinspection PyTypeChecker
            _widget = _user_data[_tag]
        # ------------------------------------------------------------------ 04.03
        # if allow_refresh then we delete tag and referenced widget from user data
        # we keep reference to _after_widget so that we can insert newly created widget appropriately
        if self.allow_refresh:
            if _widget is not None:
                # delete tag from receiver
                del _user_data[_tag]
                # + we are assuming this will be MovableWidget ... Note that we want to
                #   keep this way and if possible modify other code ... this is possible
                #   for container widgets, and we do not see that this callback will be
                #   used for non-movable Widgets
                try:
                    _after_widget = _widget.after()
                except AttributeError:
                    ...
                # delete widget
                # this will delete itself
                # this will also remove itself from `parent.children`
                _widget.delete()
                # set back to None so that it can be recreated
                # noinspection PyTypeChecker
                _widget = None

        # ------------------------------------------------------------------ 05
        # if widget is not present create it and add to receiver
        if _widget is None:
            # -------------------------------------------------------------- 05.01
            # get actual result widget we are interested to display ...
            if self.run_async:
                _new_widget = widget.Group(horizontal=False)
                AwaitableTask(
                    fn=helper.make_async_fn_runner,
                    fn_kwargs=dict(
                        receiver_grp=_new_widget,
                        blocking_fn=util.rgetattr(_hashable, self.callable_name),
                    )
                ).add_to_task_queue()
            else:
                _new_widget = util.rgetattr(
                    _hashable, self.callable_name)()  # type: widget.MovableWidget
            # -------------------------------------------------------------- 05.03
            # tag it i.e. save it to receiver user_data as it was newly created
            _user_data[_tag] = _new_widget
            # -------------------------------------------------------------- 05.04
            # also add it to receiver children
            _receiver(_new_widget)
            # -------------------------------------------------------------- 05.05
            # move widget based on _after_widget
            if _after_widget is not None:
                _new_widget.move(before=_after_widget)
