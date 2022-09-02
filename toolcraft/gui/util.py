import functools


# noinspection PyPep8Naming
def CacheResult(*dec_args, **dec_kwargs):
    """
    *** NOTE ***

    Note making this as class based decorator is challenging.

    Also making use of descriptor pattern is also challenging as it becomes
    difficult to have properties that are cached. Also note that recursive
    cached method or properties are tedious to cache.

    Hence many open-source library like that from authors of cookiecutter
    tend to use function decorators
    """
    # ---------------------------------------------------------------- 01
    # check if decorator is used appropriately
    # ---------------------------------------------------------------- 01.01
    # kwargs must not be supplied
    if len(dec_kwargs) != 0:
        raise Exception(
            f"Do not pass keyword args to CacheResult related decorators. "
            f"Just use it without braces ... KwArgs detected {dec_kwargs}"
        )
    # ---------------------------------------------------------------- 01.02
    # do not use curly braces for decorator
    if len(dec_args) == 0:
        raise Exception(
            "Do not use curly braces for  CacheResult related decorators ")
    # ---------------------------------------------------------------- 01.03
    # do not pass args to decorator
    if len(dec_args) > 1:
        raise Exception(
            f"Do not pass args to decorator CacheResult related "
            f"decorators ",
            f"Just use it without braces ...",
            f"Args detected: {dec_args}",

        )
    # ---------------------------------------------------------------- 01.04
    # this should be always the case when used decorator with curly braces
    # the thing that i decorated should be a function
    if len(dec_args) == 1:
        e.validation.ShouldBeFunction(
            value=dec_args[0],
            msgs=[
                f"We expect you to use CacheResult related decorators on "
                f"function, instead you have decorated it over {dec_args[0]}"
            ]
        ).raise_if_failed()
    else:
        raise Exception("Should never happen")
    # ---------------------------------------------------------------- 01.05
    # the dec function should not be local function
    # but note that it is okay if it is method of local class ...
    #   as in that case it will be "<...>.<locals>.SomeClassName.method"
    if dec_args[0].__qualname__.split(".")[-2] == "<locals>":
        raise Exception(
            f"We do not allow to use CacheResult decorator to be used "
            f"with local functions ... only instance methods and first "
            f"class functions are supported. Please check {dec_args[0]}"
        )

    # ---------------------------------------------------------------- 02
    # if all is well then the decorated function is as follows
    _dec_func = dec_args[0]
    # and the cache key is
    _cache_key = _dec_func.__name__
    # hack to detect if method ... note that if local function this will be
    # True but anyways we block that in 01.05 ;)
    _is_method = _dec_func.__qualname__.endswith(f".{_dec_func.__name__}")

    # ---------------------------------------------------------------- 03
    # define wrapper function
    # todo: if used with property replace property with value at runtime for
    #  faster access
    # todo: check if the method on which CacheResult is used is made property
    #  by property decorator
    @functools.wraps(_dec_func)
    def _wrap_func(*args, **kwargs):
        # ------------------------------------------------------------ 03.01
        # some validations
        # kwargs should not be provided
        if bool(kwargs):
            raise e.code.NotAllowed(
                msgs=[
                    f"Please so not supply kwargs while using caching",
                    f"Found kwargs",
                    kwargs
                ]
            )
        # check args provided
        if _is_method:
            if len(args) != 1:
                raise e.code.ShouldNeverHappen(
                    msgs=[
                        f"We detected above that this is method so we expect "
                        f"one arg which is self to be available ..."
                    ]
                )
        else:
            if len(args) != 0:
                raise e.code.NotAllowed(
                    msgs=[
                        f"Please do not supply args to function decorated "
                        f"with CacheResult",
                        f"Found args", args,
                    ]
                )
        # if one arg is provided it will be self (i.e the dec function is
        # defined within class)
        if _is_method:
            # todo: check if args[0] is python object i.e. the decorated
            #  function will cache things inside this instance ...
            ...

        # ------------------------------------------------------------ 03.02
        # get dict in which we will add cache container
        if _is_method:
            _cache_store_handler_dict = args[0].__dict__
        else:
            _cache_store_handler_dict = __import__(
                _dec_func.__module__
            ).__dict__
        # add cache container if not present
        if CACHE_KEY in _cache_store_handler_dict.keys():
            _cache_store = _cache_store_handler_dict[
                CACHE_KEY
            ]  # type: dict
        else:
            _cache_store = {}
            _cache_store_handler_dict[CACHE_KEY] = _cache_store

        # ------------------------------------------------------------ 03.03
        # if _cache_key not present set it by return value of _dec_fn
        # NOTE: as smart dict for cache cannot be freezed we use
        # `_cache_store._dict` so that we can bypass freeze checks ;)
        # noinspection PyProtectedMember
        if _cache_key not in _cache_store.keys():
            # compute as key not present with results
            _res = _dec_func(*args, **kwargs)

            # add the results to dict
            # Note that we did not use `_cache_store._dict` as the cache dict
            # will never be freezed ... so writing to it will always be allowed
            _cache_store[_cache_key] = _res

        # return
        # noinspection PyProtectedMember
        return _cache_store[_cache_key]

    # ---------------------------------------------------------------- 04
    # add a tag to detect if decorator was used
    _wrap_func._pk_cached = True

    # ---------------------------------------------------------------- 05
    # return wrapped function
    return _wrap_func
