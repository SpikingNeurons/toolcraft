"""
This is just for quickly refactoring code and doing some static code tests

Refer: https://regex101.com

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
            # make sure that raise_if_failed is not at end i.e. by detecting "."
            for _t in _tokens:
                _r_t = _t.replace(".", "\.") + "\([\s\S]*?\)\n"
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
            # so simply do final replace ;) ... this preserves old changes and add
            # raise where we have forgotten
            _src_txt = _src_txt.replace("raise raise", "raise")
            # finally, write back changes
            _fi.write_text(_src_txt, encoding="utf8")


def add_raise_if_expected_after_some_exceptions():
    from toolcraft.error import code, io, validation
    from toolcraft.error import __base__
    _tokens = []
    for _m in [code, io, validation]:
        for _a in dir(_m):
            _v = getattr(_m, _a)
            try:
                if issubclass(_v, __base__._CustomException):
                    _r = inspect.getsource(_v.__init__).find("return")
                    # raise_if_expected needed for exceptions that could not be _RAISE_EXPLICITLY
                    if not _v._RAISE_EXPLICITLY:
                        _token = f"{_v.__module__}.{_v.__name__}".replace("toolcraft.error", "e")
                        print(_v, _token)
                        _tokens.append(_token)
            except TypeError:
                ...
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
            # make sure that raise is not at start
            for _t in _tokens:
                if _src_txt.find(f"raise {_t}") != -1:
                    raise Exception(
                        f"You have explicitly raised exception {_t} in file {_fi}. "
                        f"Please instead call `raise_if_failed()` method on "
                        f"exception instance ... "
                    )
            # find the end location for matched tokens
            _locations_to_inject = []
            for _t in _tokens:
                _r_t = _t.replace(".", "\.") + "\([\s\S]*?\)\n"
                for _match in re.finditer(_r_t, string=_src_txt):
                    print(_match.group())
                    _locations_to_inject.append(_match.span()[1]-1)
            _locations_to_inject.sort()
            # inject
            if bool(_locations_to_inject):
                _start = 0
                _new_src_txt = ""
                for _ii in _locations_to_inject:
                    _new_src_txt += _src_txt[_start: _ii] + ".raise_if_failed()"
                    _start = _ii
                _new_src_txt += _src_txt[_start:]
            else:
                _new_src_txt = _src_txt
            # if already done then there will be two raise_if_failed
            # so simply do final replace ;) ... this preserves old changes and add
            # raise where we have forgotten
            _new_src_txt = _new_src_txt.replace(".raise_if_failed().raise_if_failed()", ".raise_if_failed()")
            # finally, write back changes
            _fi.write_text(_new_src_txt, encoding="utf8")


if __name__ == "__main__":
    should_add_raise_explicitly_class_field()
    add_raise_before_exceptions_to_be_raised_explicitly()
    add_raise_if_expected_after_some_exceptions()
