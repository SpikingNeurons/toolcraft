import inspect
import re
import sys

from .. import logger


# todo: for python 3 there is special method Exception().with_traceback() see
#  if can be used .... also for stack trace instead if using inspect see if
#  Exception().__traceback__ can be used
#  check PEP 3109 https://www.python.org/dev/peps/pep-3109/


# In some case we want to catch exception to handle while testing but
# this is only for debugging
_SHOW_TRACEBACK = True


def camel_case_split(identifier):
    matches = re.finditer(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


class CustomException:

    def __init__(
        self, *,
        msgs: logger.MESSAGES_TYPE,
        unhandled_exception: Exception = None,
        raise_mode: bool = False,
    ):
        global _SHOW_TRACEBACK
        # -----------------------------------------------------------------01
        # VALIDATIONS
        # do not allow to use CustomException
        if self.__class__ is CustomException:
            raise Exception(
                f"Do not use class {CustomException} instead subclass it ..."
            )

        # -----------------------------------------------------------------02
        # Shutdown all the spinners
        for s in logger.Spinner.NESTED_SPINNERS_STORE:
            s.abort()

        # -----------------------------------------------------------------02
        # GET LOGGER
        _caller_frame = inspect.currentframe().f_back.f_back
        _logger = logger.get_logger(
            module=inspect.getmodule(_caller_frame)
        )

        # -----------------------------------------------------------------03
        # get all spinners and abort it
        for s in logger.Spinner.NESTED_SPINNERS_STORE[::-1]:
            s.hide()
            s.abort()

        # -----------------------------------------------------------------04
        # MESSAGES RELATED
        # get exception str
        exception_str = " ".join(camel_case_split(
            self.__class__.__name__)).upper()

        # -----------------------------------------------------------------05
        # LOG
        _logger.error(
            msg=f"{logger.Emoji.EMOJI_SKULL} >>> {exception_str} <<< "
                f"{logger.Emoji.EMOJI_SKULL}",
            msgs=msgs,
            prefix=""
        )

        # -----------------------------------------------------------------06
        # traceback
        if _SHOW_TRACEBACK:
            cf = _caller_frame
            _traceback_msgs = []
            while cf is not None:
                # bypass some traceback frames
                # print(cf.f_code.co_filename, cf.f_code.co_name, cf.f_lineno)
                if cf.f_code.co_name == "_cache_result_wrapper_func_in_util":
                    cf = cf.f_back
                    continue
                if cf.f_code.co_filename == "<string>":
                    cf = cf.f_back
                    continue
                if cf.f_code.co_filename == "<frozen importlib._bootstrap>":
                    cf = cf.f_back
                    continue
                if cf.f_code.co_filename == \
                        "<frozen importlib._bootstrap_external>":
                    cf = cf.f_back
                    continue

                # append traceback frame
                _traceback_msgs.append(
                    f"File \"{cf.f_code.co_filename}\", line {cf.f_lineno}"
                )

                # go back to previous traceback frame
                cf = cf.f_back

            _logger.error(
                msg=f"Traceback (most recent call at last):",
                msgs=_traceback_msgs[::-1],
                prefix=logger.Emoji.TRACEBACK_PREFIX,
                no_wrap=True)

        # -----------------------------------------------------------------07
        # if unhandled exception passed print them here
        if unhandled_exception is not None:
            from .. import util
            _logger.error(
                msg=f"Encountered unhandled exception (please see below)",
                prefix=logger.Emoji.TRACEBACK_PREFIX,
                no_wrap=True)
            # todo: this currently is not logged in the file and is only
            #  printed to console ... only exception name is logged to file
            #  in above code
            print(util.StringFmt.centered_text())
            print(util.StringFmt.centered_text("Unhandled Exception"))
            print(util.StringFmt.centered_text(
                f"[ {unhandled_exception.__class__.__module__}."
                f"{unhandled_exception.__class__.__name__} ]"
            ))
            print(util.StringFmt.centered_text())
            print(str(unhandled_exception))
            print(util.StringFmt.centered_text())
            print(util.StringFmt.centered_text("End Of Unhandled Exception"))
            print(util.StringFmt.centered_text())

        # -----------------------------------------------------------------08
        _logger.error(
            msg=f"{logger.Emoji.EMOJI_SKULL} >>> EXITING THE PROGRAM <<< "
                f"{logger.Emoji.EMOJI_SKULL}",
            prefix="")

        # -----------------------------------------------------------------09
        # In some case we want to catch exception to handle while testing but
        # this is only for debugging
        if raise_mode:
            e = Exception(exception_str)
            e.custom_exception_class = self.__class__
            raise e
        else:
            sys.exit(0)

            # the below code works with interactive mode but when running
            # scripts from python installation it does not work as intended
            # so we just exit .... the side-effect is in interactive mode the
            # session does not last ... the below solution is not generic
            # enough ...
            # todo: figure out generic solution for exiting in
            #  interactive mode
            # noinspection PyUnresolvedReferences
            # import __main__ as m
            # if hasattr(m, "__file__"):
            #     # only exit if not in interactive mode
            #     sys.exit(0)
            # else:
            #     # todo: figure out how to exit in interactive mode ...
            #     #  without traceback
            #     raise Exception(exception_str)

    @classmethod
    def matches(cls, exception: Exception) -> bool:
        try:
            # noinspection PyUnresolvedReferences
            if exception.custom_exception_class is cls:
                return True
            else:
                # it is custom exception but a different one so re raise it
                raise exception
        except AttributeError:
            # if custom_exception_class attribute not present then
            # unrecognized exception so re raise
            raise exception

