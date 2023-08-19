import dataclasses
import typing as t


from .__base__ import Hashable, UseMethodInForm, EscapeWithContext, MovableWidget
from . import widget
from . import table
from . import callback


# noinspection PyUnreachableCode
if False:
    from ..marshalling import HashableClass


@dataclasses.dataclass(repr=False)
class Form(widget.CollapsingHeader):
    """
    Form is a special widget which creates a `form_fields_container` container and
    add all form fields to it as defined by layout() method.

    Note that Form itself is not a container and no children can be added to it.
    It only supports UI elements supplied via fields. Non Widget fields like Callbacks
    and constants will be can also be supplied to form to enhance form but obviously
    they are not UI elements and hence will be ignored by layout method.

    If you want dynamic widgets simple have a class field defined with container
    Widgets like Group and dynamically add elements to it.

    todo: the delete can be called on class field Widgets ... mostly we want to not
      allow fields of form to be dynamically deleted ... but that is not the case now
      So do only if needed
    """

    def init(self):
        """
        WHY DO WE CLONE??

        To be called from init. Will be only called for fields that are
        Widget or Callback

        Purpose:
        + When defaults are provided copy them to mimic immutability
        + Each immutable field can have his own parent

        Why is this needed??
          Here we trick dataclass to treat some Hashable classes that were
          assigned as default to be treated as non mutable ... this helps us
          avoid using default_factory

        Who is using it ??
          + gui.Widget
            Needed only while building UI to reuse UI components and keep code
            readable. This will be in line with declarative syntax.
          + gui.Callback
            Although not needed we still allow this behaviour as it will be
            used by users that build GUI and they might get to used to assigning
            callbacks while defining class ... so just for convenience we allow
            this to happen

        Needed for fields that has default values
          When a instance is assigned during class definition then it is not
          longer usable with multiple instances of that classes. This applies in
          case of UI components. But not needed for fields like prepared_data as
          we actually might be interested to share that field with other
          instances.

          When such fields are bound for certain instance especially using the
          property internal we might want an immutable duplicate made for each
          instance.

        todo: Dont be tempted to use this behaviour in other cases like
          Model, HashableClass. Brainstorm if you think this needs
          to be done. AVOID GENERALIZING THIS FUNCTION.

        """
        # ------------------------------------------------------- 01
        # call super
        super().init()

        # ------------------------------------------------------- 02
        # loop over fields
        for f_name in self.dataclass_field_names:
            # --------------------------------------------------- 02.01
            # get value
            v = getattr(self, f_name)
            # --------------------------------------------------- 02.02
            # if not Widget class continue
            # that means Widgets and Containers will be clones if default supplied
            # While Hashable class and even Callbacks will not be cloned
            # note that for UI we only need Dpg elements to be clones as they have
            # build() method
            if not isinstance(v, widget.Widget):
                continue
            # --------------------------------------------------- 02.03
            # get field and its default value
            # noinspection PyUnresolvedReferences
            _field = self.__dataclass_fields__[f_name]
            _default_value = _field.default
            # --------------------------------------------------- 02.04
            # if id(_default_value) == id(v) then that means the default value is
            # supplied ... so now we need to trick dataclass and assigned a clone of
            # default_value
            # To understand why we clone ... read __doc_string__
            # Note that the below code can also handle but we use id(...)
            #   to be more specific
            # _default_value == dataclasses.MISSING
            if id(_default_value) == id(v):
                # make clone
                v_cloned = v.clone()
                # hack to overwrite field value (as this is frozen)
                self.__dict__[f_name] = v_cloned

    def layout(self) -> widget.Group:
        """
        Method to layout widgets in this form and assign Callbacks if any

        Note that default behaviour is to layout the UI elements in the order as
        defined in class fields.

        You can override this method to do layout in any order you wish.

        Note that if you have Callbacks for this form as class fields you need to take
        care to bind them to widgets. The default implementation is very simple

        For dynamic widgets add Group widget as dataclass field and add dynamic items
        to it
        """
        # make grp
        _grp = widget.Group()

        # if there is a widget which is field of this widget then add it
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if isinstance(v, MovableWidget):
                _grp(widget=v)

        # return
        return _grp

    def build_pre_runner(self):
        # call super
        super().build_pre_runner()

        # add layout to form
        self(widget=self.layout())


@dataclasses.dataclass(repr=False)
class ButtonBarForm(Form):

    def init(self):
        # call super
        super().init()

        # make some vars
        self._mapper = dict()  # type: t.Dict[str, (t.Callable, t.Dict)]
        self._callback = callback.CallFnCallback()
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
            self._callback.get_button_widget(
                label=gui_name, call_fn=self._call_fn, call_fn_kwargs=dict(_key=key),
            )

    def _call_fn(self, _key: str):
        self._receiver.clear()
        with self._receiver:
            _fn, _fn_kwargs = self._mapper[_key]
            if _fn_kwargs is None:
                _fn_kwargs = dict()
            _fn(**_fn_kwargs)


@dataclasses.dataclass(repr=False)
class HashableMethodsRunnerForm(Form):
    """
    This is the form which appears on right side of split window. And it needs
    accompanying button wo work with

    todo: if methods takes kwargs then make a form inside form so that the method
      call can be parametrized
    """

    hashable: t.Union[Hashable, "HashableClass"] = None
    # todo: add icons for this
    close_button: bool = True
    # todo: add icons for this
    info_button: bool = True
    callable_names: t.List[str] = None

    def init_validate(self):

        # call super
        super().init_validate()

        # validate
        if self.hashable is None:
            raise ValueError("Please supply field `hashable`")
        if self.callable_names is None:
            raise ValueError("Please supply field `callable_names`")

    def init(self):
        # call super
        super().init()

        # make some vars
        with EscapeWithContext():
            # noinspection PyAttributeOutsideInit
            self._button_bar = widget.Group(horizontal=True)
            # noinspection PyAttributeOutsideInit
            self._receiver = widget.Group(user_data=dict())

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
        _callable_names = self.callable_names.copy()
        if self.info_button:
            if "info_widget" not in _callable_names:
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
            )
            # add button
            _button_bar(widget=_button)

        # return
        return _layout


@dataclasses.dataclass(repr=False)
class DoubleSplitForm(Form):
    """
    Takes
    + Buttons in left panel (can be grouped with group_key)
    + And responses are added to right receiver panel
    """
    callable_name: str = None

    def init_validate(self):

        # call super
        super().init_validate()

        # validate
        if self.callable_name is None:
            raise ValueError("Please supply field `callable_name`")

    def init(self):
        # call super
        super().init()

        # make container for button_panel_group
        # noinspection PyAttributeOutsideInit
        self._button_panel_group = dict()  # type: t.Dict[str, widget.CollapsingHeader]
        with EscapeWithContext():
            # noinspection PyAttributeOutsideInit
            self._button_panel = widget.Group(horizontal=False)
            # we will dict for user data to save things for _receiver_panel
            # noinspection PyAttributeOutsideInit
            self._receiver_panel = widget.Group(horizontal=False, user_data=dict())

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
            )
