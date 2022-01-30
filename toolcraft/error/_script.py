"""
This is just for quickly refactoring code and doing some static code tests
"""
import inspect
import pathlib
import re


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
    from toolcraft.error import code, io, validation
    from toolcraft.error import __base__
    _tokens = []
    for _m in [code, io, validation]:
        for _a in dir(_m):
            _v = getattr(_m, _a)
            try:
                if issubclass(_v, __base__._CustomException):
                    _r = inspect.getsource(_v.__init__).find("return")
                    if _v._RAISE_EXPLICITLY:
                        _token = f"{_v.__module__}.{_v.__name__}".replace("toolcraft.error", "e")
                        print(_v, _token)
                        _tokens.append(_token)
            except TypeError:
                ...
    _raise_if_failed_str = ".raise_if_failed"
    for _fo in [
        pathlib.Path("C:\\Users\\prave\\Documents\\Github\\RU"),
        pathlib.Path("C:\\Users\\prave\\Documents\\Github\\toolcraft"),
    ]:
        for _fi in _fo.glob('**/*.py'):
            # do not apply anything for code in this file
            if _fi.absolute() == pathlib.Path(__file__).absolute():
                continue
            # log
            print("Processing", _fi)
            # read source
            _src_txt = _fi.read_text(encoding="utf8")
            # make sure that raise_if_failed is not at end
            for _t in _tokens:
                _r_t = _t.replace(".", "\.") + "[\s\S]*?\][\s\S]*?\)"
                for _match in re.finditer(_r_t, string=_src_txt):
                    print(_match.group())
                    if _src_txt[_match.span()[1]: _match.span()[1]+1] == ".":
                        print(_match.group())
                        raise Exception(
                            f"Check file {_fi} you seem to call some attribute of "
                            f"exception {_t}"
                        )
            # replace tokens and prefix raise to them
            for _t in _tokens:
                _src_txt = _src_txt.replace(_t, "raise " + _t)
            # if already done then there will be two raises
            # so simple do final replace ;) ... this preserves old changes and add
            # raise where we have forgotten
            _src_txt = _src_txt.replace("raise raise", "raise")
            # finally, write back changes
            _fi.write_text(_src_txt, encoding="utf8")





if __name__ == "__main__":
    # should_add_raise_explicitly_class_field()
    add_raise_before_exceptions_to_be_raised_explicitly()
