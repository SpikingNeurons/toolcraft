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
        return widget.Button(
            label=label,
            callback=cls(),
            user_data={'widget_to_delete': widget_to_delete},
        )

    def fn(self, sender: widget.Widget):
        try:
            sender.get_user_data()['widget_to_delete'].delete()
        except KeyError:
            raise KeyError(
                f"Was expecting you to supply dict item `widget_to_delete` in "
                f"`user_data` of sender {sender.__class__}"
            )


@dataclasses.dataclass
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.

    If group_tag is None then we make unique guid for all callable_name
    else we reuse group_tag across different callables this will just
    mimic the TabGroup behaviour where one receiver widget will be updated.

    Note that this will mean that allow_refresh will be True when
    tab_group_name is not None.
    """
    hashable: t.Union[Hashable, "HashableClass"]
    callable_name: str
    receiver: widget.ContainerWidget
    allow_refresh: bool
    group_tag: str = None
    run_async: bool = False

    def init_validate(self):
        # call super
        super().init_validate()

        # if tab_group_name is supplied that means you are sharing receiver
        # object across multiple Callbacks with same tab_group_name
        # So ensure that the allow_refresh is True
        if self.group_tag is not None:
            if not self.allow_refresh:
                raise Exception(
                    f"looks like you are using group_tag. So please "
                    f"ensure that allow_refresh is set to True"
                )

    def fn(self, sender: widget.Widget):
        # get some vars
        # _sender = self.sender
        _hashable = self.hashable
        _receiver = self.receiver
        if self.group_tag is None:
            _tag = f"{_hashable.__class__.__name__}:" \
                   f"{_hashable.hex_hash[-10:]}.{self.callable_name}"
        else:
            # this make sure that same guid is shared across multiple
            # callbacks that use same tab_group_name.
            # Note this applies if _hashable and receiver are same
            _tag = f"{_hashable.__class__.__name__}:" \
                   f"{_hashable.hex_hash[-10:]}.{self.group_tag}"

        # get widget for given tag if present
        # .... doesn't matter if you use sender or _receiver as there is one dashboard for all
        #      This might change if we have multiple dashboard instances
        # todo: we are using Engine we do not need this
        _dash_board = _receiver.dash_board
        # todo: precaution check ... remove later
        assert id(_dash_board) == id(sender.dash_board), "must be same ..."
        # noinspection PyTypeChecker
        _widget = Engine.tags.get(_tag, None)
        _after_widget = None

        # if allow refresh then delete widget and set it to None so that it
        # can be created again
        if self.allow_refresh:
            # if widget is available i.e. it is tagged then delete it
            if _widget is not None:
                # fetch _before_widget
                # we are assuming this will be MovableWidget ... Note that we want to
                # keep this way and if possible modify other code ... this is possible
                # for container widgets, and we do not see that this callback will be
                # used for non-movable Widgets
                try:
                    _widget: widget.MovableWidget
                    _after_widget = _widget.after()
                except AttributeError:
                    ...
                # this will delete itself
                # this will also remove itself from `parent.children`
                # this will also untag itself if tagged
                _widget.delete()
                # set back to None so that it can be recreated
                # noinspection PyTypeChecker
                _widget = None

        # if widget is not present create it
        if _widget is None:
            # get actual result widget we are interested to display ... and make
            # it child to receiver
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

            # tag it as it was newly created
            Engine.tag_widget(tag=_tag, widget=_new_widget)

            # add to receiver children
            _receiver(_new_widget)

            # move widget
            if _after_widget is not None:
                _new_widget.move(before=_after_widget)
