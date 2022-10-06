import dataclasses
import typing as t


from .__base__ import Form, Hashable, UseMethodInForm, EscapeWithContext
from . import widget
from . import table
from . import callback


# noinspection PyUnreachableCode
if False:
    from ..marshalling import HashableClass


@dataclasses.dataclass
class ButtonBarForm(Form):

    def init(self):
        # call super
        super().init()

        # make class for callback handling
        @dataclasses.dataclass
        class Callback(callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: widget.Widget):
                _key = sender.get_user_data()["key"]
                self._receiver.clear()
                with self._receiver:
                    _fn, _fn_kwargs = self._mapper[_key]
                    if _fn_kwargs is None:
                        _fn()
                    else:
                        _fn(**_fn_kwargs)

        # make some vars
        self._mapper = dict()  # type: t.Dict[str, (t.Callable, t.Dict)]
        self._callback = Callback()
        with EscapeWithContext():
            self._button_bar = widget.Group(horizontal=True)
            self._receiver = widget.Group()


    def layout(self) -> widget.MovableContainerWidget:
        # get fromm super
        _layout = super().layout()

        # add more vars
        _layout(self._button_bar)
        _layout(self._receiver)

        # return
        return _layout

    def register(self, key: str, fn: t.Callable, fn_kwargs: t.Dict = None, gui_name: str = None, ):
        """
        todo: handle fn is None with different callback for now it is reassigned in job.ArtifactManager.gui
        """
        # just set default
        if gui_name is None:
            gui_name = key

        # check if already mapped
        if key in self._mapper.keys():
            raise KeyError(
                f"Looks like you have already registered gui function for this key {key!r}"
            )

        # test if in with context
        if self.is_in_gui_with_mode:
            raise Exception(
                "Register new buttons and their gui methods outside gui related with context"
            )

        # add
        self._mapper[key] = fn, fn_kwargs

        # make button and add it to container
        with self._button_bar:
            widget.Button(
                label=gui_name, callback=self._callback, user_data={"key": key},
            )


@dataclasses.dataclass
class HashableMethodsRunnerForm(Form):
    """
    This is the form which appears on right side of split window. And it needs
    accompanying button wo work with

    todo: if methods takes kwargs then make a form inside form fo that the method
      call can be parametrized
    """

    hashable: t.Union[Hashable, "HashableClass"]
    # a single receiver will be used for all methods given by callable_names,
    # so we share it with `group_tag`
    # This allows to use keys in callable_names as tab bar
    group_tag: t.Optional[str]
    # todo: add icons for this
    close_button: bool
    # todo: add icons for this
    info_button: bool
    callable_names: t.List[str]

    def init(self):
        # call super
        super().init()

        # make some vars
        with EscapeWithContext():
            self._button_bar = widget.Group(horizontal=True)
            self._receiver = widget.Group()

    def layout(self) -> widget.MovableContainerWidget:
        # get fromm super
        _layout = super().layout()

        # add more vars
        _layout(self._button_bar)
        _layout(self._receiver)

        # add close button
        if self.close_button:
            self._button_bar(
                widget=callback.CloseWidgetCallback.get_button_widget(
                    widget_to_delete=self),
            )

        # add info button
        _button_bar = self._button_bar
        _receiver = self._receiver
        _hashable = self.hashable
        _callable_names = self.callable_names
        if self.info_button:
            _callable_names.append("info_widget")

        # make buttons for callable names
        for _callable_name in _callable_names:
            # get UseMethodInForm
            _use_method_in_form_obj = UseMethodInForm.get_from_hashable_fn(
                hashable=_hashable, fn_name=_callable_name
            )
            # create button widget
            _button = _use_method_in_form_obj.get_button_widget(
                hashable=_hashable,
                receiver=_receiver,
                allow_refresh=True,
                group_tag=self.group_tag,
            )
            # add button
            _button_bar(widget=_button)

        # return
        return _layout


@dataclasses.dataclass
class DoubleSplitForm(Form):
    """
    Takes
    + Buttons in left panel (can be grouped with group_key)
    + And responses are added to right receiver panel
    """
    callable_name: str
    allow_refresh: bool

    def init(self):
        # call super
        super().init()

        # make container for button_panel_group
        self._button_panel_group = dict()  # type: t.Dict[str, widget.CollapsingHeader]
        with EscapeWithContext():
            self._button_panel = widget.Group(horizontal=False)
            self._receiver_panel = widget.Group(horizontal=False)

    def layout(self) -> table.Table:
        # call super
        _layout = super().layout()

        # create table
        _table = table.Table.table_from_literals(
            rows=1,
            cols=2,
        )
        _table.header_row = False
        _table.resizable = True
        # _table.policy = gui.En
        _table.borders_innerH = True
        _table.borders_outerH = True
        _table.borders_innerV = True
        _table.borders_outerV = True

        # add cells
        _table[0, 0](self._button_panel)
        _table[0, 1](self._receiver_panel)

        # add table
        _layout(widget=_table)

        # return
        # noinspection PyTypeChecker
        return _layout

    def add(
        self,
        hashable: t.Union[Hashable, "HashableClass"],
        group_key: str = None,
        default_open: bool = False,
    ):

        # ----------------------------------------------------- 01
        # check if using with mode for gui
        if self.is_in_gui_with_mode:
            raise Exception(
                f"To add elements to {self.__class__.__name__!r} exist from gui with mode ..."
            )

        # ----------------------------------------------------- 02
        # get UseMethodInForm
        _use_method_in_form_obj = UseMethodInForm.get_from_hashable_fn(
            hashable=hashable, fn_name=self.callable_name
        )

        # ----------------------------------------------------- 03
        # get container
        if group_key is None:
            _container = self._button_panel
        else:
            if group_key in self._button_panel_group.keys():
                _container = self._button_panel_group[group_key]
            else:
                with self._button_panel:
                    self._button_panel_group[group_key] = widget.CollapsingHeader(
                        label=group_key, default_open=default_open,
                    )
                    _container = self._button_panel_group[group_key]

        # ----------------------------------------------------- 04
        # create button widget ... note use of with context so that it can also work when
        # `add` is called inside `with` context
        with _container:
            _use_method_in_form_obj.get_button_widget(
                hashable=hashable,
                receiver=self._receiver_panel,
                allow_refresh=self.allow_refresh,
                # we can maintain this as we will be using single `callable_name` and hence
                # no use for this kwarg
                group_tag=None,
            )
