
import sys
import time
sys.path.append("..")

from toolcraft import richy, logger

_LOGGER = logger.get_logger()


def try_progress():
    for _ in richy.Progress.simple_track(sequence=[1, 2, 3, 4]):
        time.sleep(1)

    with richy.Progress.for_download_and_hashcheck(title="Test Progress") as _p:
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(0.2)
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(0.2)
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 3"):
            time.sleep(0.2)


def try_status():
    with richy.Status(title="Test Status") as _s:
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.dots, status="start")
        time.sleep(3)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.arrow, status="next")
        time.sleep(3)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.balloon, status="done")
        time.sleep(3)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.star, status="close")
        time.sleep(3)


def try_status_panel():
    _sp = richy.ProgressStatusPanel(
        title="Test Status Panel", tc_log=_LOGGER
    )
    with _sp:
        _p = _sp.progress
        _s = _sp.status
        _time = 0.2

        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(_time)
        _s.update(spinner_speed=1.0, spinner=None, status="start")
        time.sleep(_time)

        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(_time)
        _s.update(spinner_speed=1.0, spinner=None, status="next")
        time.sleep(_time)

        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 3"):
            time.sleep(_time)
        _s.update(spinner_speed=1.0, spinner=None, status="done")
        time.sleep(_time)

        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 4"):
            time.sleep(_time)
        _s.update(spinner_speed=1.0, spinner=None, status="close")
        time.sleep(_time)


def main():
    # try_progress()
    try_status()
    # try_status_panel()


if __name__ == '__main__':
    main()
