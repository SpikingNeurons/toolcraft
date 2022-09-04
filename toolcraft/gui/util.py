import functools
import typing as t
import inspect


def rsetattr(obj, attr, val):
    """
    Inspired from
    https://stackoverflow.com/questions/31174295/
    """
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    """
    Inspired from
    https://stackoverflow.com/questions/31174295/
    """
    def _getattr(_obj, _attr):
        return getattr(_obj, _attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def rhasattr(obj, attr):
    _nested_attrs = attr.split(".")
    _curr_obj = obj
    for _a in _nested_attrs[:-1]:
        if hasattr(_curr_obj, _a):
            _curr_obj = getattr(_curr_obj, _a)
        else:
            return False
    return hasattr(_curr_obj, _nested_attrs[-1])


class HookUp:
    def __init__(
        self,
        *,
        cls: t.Type,
        method: t.Callable,
        pre_method: t.Optional[t.Callable] = None,
        post_method: t.Optional[t.Callable] = None,
    ):
        # if method is HookUp instance that means the parent class of cls has
        # already hooked itself up and there is no overridden method in this
        # subclass for the same method ... so we need to define new hookup
        # and grab post and pre runners specific to this class
        # So if HookUp we grab method from it and create a new hook up here
        # Note: the HookUp class from parent becomes useless and is replaced
        #   by new HookUp for child class
        # Note: the args pre_method and post_method are the latest one i.e. from
        #   child class ... so no need for `method.pre_method` and `method.post_method`
        if isinstance(method, HookUp):
            # noinspection PyUnresolvedReferences
            method = method.method

        # save variables in self
        self.cls = cls
        self.method = method
        self.pre_method = pre_method
        self.post_method = post_method

        # assign self i.e. HookUp instance in cls
        # Note we do not do `cls.method = self` as that overrides parents HookUp
        # cls.__dict__[method.__name__] = self
        setattr(cls, method.__name__, self)

    def __repr__(self):
        return f"HookUp for {self.cls.__module__}.{self.cls.__name__}: (" \
               f"{self.pre_method.__qualname__}, " \
               f"{self.method.__qualname__}, " \
               f"{self.post_method.__qualname__}" \
               f")"

    def __get__(self, method_self, method_self_type):
        """
        This makes use of description pattern ... now we have access to method's
        self so that we can use it in __call__
        """
        self.method_self = method_self
        return self

    def __eq__(self, other):
        """
        Two hookups are same if method they represent is same ...

        Why this behaviour:
          HookUp instance replaces method but a child class can have
          different pre and post runners but not the different method in that
          we create new HookUp instance and borrow method from parent HookUp.
          So although the hookup instances are different both child and parent
          share same method. So this is justified in this context.

        Useful in rules.py
          We can check if method is overridden or not even if we use ne hookup
          for child class that does not override method
        """
        return self.method == other.method

    def __call__(self, *args, **kwargs):

        # -----------------------------------------------------------01
        # although might not be necessary ... we enforce
        if bool(args):
            raise Exception(
                f"Please avoid methods that use args ... while using "
                f"hook up ..."
            )
        # get default kwargs if not supplied ...
        # so that pre- and post-method gets the default kwargs
        for _k, _p in inspect.signature(self.method).parameters.items():
            if _k not in kwargs.keys():
                # noinspection PyUnresolvedReferences,PyProtectedMember
                if _p.default != inspect._empty:
                    kwargs[_k] = _p.default

        # -----------------------------------------------------------02
        # bake title
        # _kwargs_str = []
        # for k, v in kwargs.items():
        #     if isinstance(v, list):
        #         if len(v) == 1 or len(v) == 2:
        #             v = f"{v}"
        #         else:
        #             v = f"[{v[0]}, ..., {v[-1]}]"
        #     _kwargs_str.append(
        #         f"{k}={v}"
        #     )
        # _kwargs_str = ", ".join(_kwargs_str)
        if bool(kwargs):
            _kwargs_str = "..."
        else:
            _kwargs_str = ""
        # todo: with gui build {self.method_self.name} poses problem find a
        #  way to avoid logs while building GUI
        # _title = f"<{self.method_self.name}> {self.cls.__name__}." \
        _title = f"{self.cls.__name__}." \
                 f"{self.method.__name__}" \
                 f"({_kwargs_str})"
        # _title = logger.replace_with_emoji(_title)

        # -----------------------------------------------------------03
        # call business logic
        # -----------------------------------------------------------03.01
        # call pre_method is provided
        if self.pre_method is not None:
            _pre_ret = self.pre_method(self.method_self, **kwargs)
            # pre_method should not return anything
            if _pre_ret is not None:
                raise Exception(
                    f"{HookUp} protocol enforces the "
                    f"pre_method {self.pre_method} of method "
                    f"{self.method} to "
                    f"not return anything ...",
                    f"Found return value {_pre_ret}"
                )
        # -----------------------------------------------------------03.03
        # call actual method
        _ret = self.method(self.method_self, **kwargs)
        # -----------------------------------------------------------03.04
        # if post_method not provided return what we have
        if self.post_method is not None:
            # call post_method as it is provided
            # spinner.info(msg=f"pre: {pre_method}")
            # spinner.info(msg=f"{method}")
            # spinner.info(msg=f"post: {post_method}")
            _post_ret = self.post_method(
                self.method_self, hooked_method_return_value=_ret, **kwargs)
            # post_method should not return anything
            if _post_ret is not None:
                raise Exception(
                    f"{HookUp} protocol enforces the "
                    f"post_method {self.post_method} of method"
                    f" {self.method} to "
                    f"not return anything ...",
                    f"Found return value {_post_ret}"
                )

        # -----------------------------------------------------------04
        # return the return value of method
        return _ret
