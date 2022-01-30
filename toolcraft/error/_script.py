"""
This is just for quickly refactoring code and doing some static code tests
"""
import inspect


def should_add_raise_explicitly_class_field():
    from toolcraft.error import code, io, validation
    from toolcraft.error import __base__
    for _m in [code, io, validation]:
        for _a in dir(_m):
            _v = getattr(_m, _a)
            try:
                if issubclass(_v, __base__._CustomException):
                    _r = inspect.getsource(_v.__init__).find("return")
                    # if return keyword not found property raise_explicitly must
                    # return True
                    print(_v, _r, _v._RAISE_EXPLICITLY)
                    if _r == -1:
                        if not _v._RAISE_EXPLICITLY:
                            raise Exception(
                                f"Override property raise_explicitly for class "
                                f"{_v} to return True"
                            )
            except TypeError:
                ...


def add_raise_before_exceptions_to_be_raised_explicitly():
    ...


if __name__ == "__main__":
    should_add_raise_explicitly_class_field()
