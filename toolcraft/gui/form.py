import dataclasses
import typing as t
import asyncio

from .. import util
from .. import error as e
from .. import marshalling as m
from .__base__ import Form
from .. import gui
from . import widget
from . import table
from . import callback


@dataclasses.dataclass
class ButtonBarForm(Form):

    @property
    @util.CacheResult
    def button_bar(self) -> widget.Group:
        with self.form_fields_container:
            return widget.Group(horizontal=True)

    @property
    @util.CacheResult
    def receiver(self) -> widget.Group:
        # just call so that button bar is always on top ;)
        _ = self.button_bar
        # create receiver
        with self.form_fields_container:
            return widget.Group()

    @property
    @util.CacheResult
    def callback(self) -> gui.callback.Callback:

        # make class for callback handling
        @dataclasses.dataclass(frozen=True)
        class __Callback(gui.callback.Callback):
            # noinspection PyMethodParameters
            def fn(_self, sender: gui.widget.Widget):
                _key = sender.get_user_data()["key"]
                self.receiver.clear()
                with self.receiver:
                    self.mapper[_key]()

        return __Callback()

    @property
    @util.CacheResult
    def mapper(self) -> t.Dict[str, t.Callable]:
        return {}

    def register(self, key: str, fn: t.Optional[t.Callable], gui_name: str = None, ):
        # just set default
        if gui_name is None:
            gui_name = key

        # check if already mapped
        e.validation.ShouldNotBeOneOf(
            value=key, values=list(self.mapper.keys()),
            msgs=["Looks like you have already registered gui function for this key"]
        ).raise_if_failed()

        # test if in with context
        if self.is_in_gui_with_mode:
            raise e.code.CodingError(
                msgs=["Register new buttons and their gui methods outside gui related with context"]
            )

        # add
        self.mapper[key] = fn

        # make button and add it to container
        with self.button_bar:
            gui.widget.Button(
                label=gui_name, callback=self.callback, user_data={"key": key},
            )


@dataclasses.dataclass
class HashableMethodsRunnerForm(Form):
    """
    This is the form which appears on right side of split window. And it needs
    accompanying button wo work with

    todo: if methods takes kwargs then make a form inside form fo that the method
      call can be parametrized
    """

    hashable: m.HashableClass
    # a single receiver will be used for all methods given by callable_names,
    # so we share it with `group_tag`
    # This allows to use keys in callable_names as tab bar
    group_tag: t.Optional[str]
    # todo: add icons for this
    close_button: bool
    # todo: add icons for this
    info_button: bool
    callable_names: t.List[str]

    @property
    @util.CacheResult
    def button_bar(self) -> widget.Group:
        with self.form_fields_container:
            return widget.Group(horizontal=True)

    @property
    @util.CacheResult
    def receiver(self) -> widget.Group:
        with self.form_fields_container:
            return widget.Group()

    def init(self):
        # call super
        super().init()

        # get some vars
        _buttons_bar = self.button_bar
        _callable_names = self.callable_names
        _receiver = self.receiver
        _hashable = self.hashable

        # add close button
        if self.close_button:
            _buttons_bar(
                widget=callback.CloseWidgetCallback.get_button_widget(
                    widget_to_delete=self),
            )

        # add info button
        if self.info_button:
            _callable_names.append("info_widget")

        # make buttons for callable names
        for _callable_name in _callable_names:
            # get UseMethodInForm
            _use_method_in_form_obj = m.UseMethodInForm.get_from_hashable_fn(
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
            _buttons_bar(widget=_button)


@dataclasses.dataclass
class DoubleSplitForm(Form):
    """
    Takes
    + Buttons in left panel (can be grouped with group_key)
    + And responses are added to right receiver panel
    """
    callable_name: str
    allow_refresh: bool

    @property
    @util.CacheResult
    def form_fields_container(self) -> table.Table:
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
        return _table

    @property
    @util.CacheResult
    def button_panel(self) -> widget.Group:
        with self.form_fields_container[0, 0]:
            return widget.Group(horizontal=False)

    @property
    @util.CacheResult
    def receiver_panel(self) -> widget.Group:
        with self.form_fields_container[0, 1]:
            return widget.Group(horizontal=False)

    @property
    @util.CacheResult
    def button_panel_group(self) -> t.Dict[str, gui.widget.CollapsingHeader]:
        return {}

    def add(
        self,
        hashable: m.HashableClass,
        group_key: str = None,
    ):

        # ----------------------------------------------------- 01
        # check if using with mode for gui
        if self.is_in_gui_with_mode:
            raise e.code.CodingError(
                msgs=[
                    f"To add elements to {self.__class__.__name__!r} exist from gui with mode ..."
                ]
            )

        # ----------------------------------------------------- 02
        # get UseMethodInForm
        _use_method_in_form_obj = m.UseMethodInForm.get_from_hashable_fn(
            hashable=hashable, fn_name=self.callable_name
        )

        # ----------------------------------------------------- 03
        # get container
        if group_key is None:
            _container = self.button_panel
        else:
            if group_key in self.button_panel_group.keys():
                _container = self.button_panel_group[group_key]
            else:
                with self.button_panel:
                    self.button_panel_group[group_key] = gui.widget.CollapsingHeader(
                        label=group_key, default_open=False,
                    )
                    _container = self.button_panel_group[group_key]

        # ----------------------------------------------------- 04
        # create button widget ... note use of with context so that it can also work when
        # `add` is called inside `with` context
        with _container:
            _use_method_in_form_obj.get_button_widget(
                hashable=hashable,
                receiver=self.receiver_panel,
                allow_refresh=self.allow_refresh,
                # we can maintain this as we will be using single `callable_name` and hence
                # no use for this kwarg
                group_tag=None,
            )
