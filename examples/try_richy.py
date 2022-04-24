
import sys
import time
sys.path.append("..")

from toolcraft import richy, logger

_LOGGER = logger.get_logger()


def try_progress():
    for _ in richy.Progress.simple_track(sequence=[1, 2, 3, 4], tc_log=_LOGGER):
        time.sleep(1)

    with richy.Progress.for_download_and_hashcheck(
        title="Test Progress", tc_log=_LOGGER,
    ) as _p:
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(0.2)
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(0.2)
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 3"):
            time.sleep(0.2)


def try_status():
    with richy.Status(
        tc_log=_LOGGER,
        title="Test Status"
    ) as _s:
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.dots, status="start")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.arrow, status="next")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.balloon, status="done")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.star, status="close")
        time.sleep(1)

    with richy.Status(
        tc_log=_LOGGER,
        title="Test Status with overall progress",
        overall_progress_iterable=[
            (richy.SpinnerType.dots, "start"),
            (richy.SpinnerType.arrow, "next"),
            (richy.SpinnerType.balloon, "done"),
            (richy.SpinnerType.star, "close"),
        ]
    ) as _s:
        for _spinner, _status in _s:
            _s.update(spinner_speed=1.0, spinner=_spinner, status=_status)
            _s.console.log(f"phase {_status}")
            time.sleep(1)


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

    _sp = richy.ProgressStatusPanel(
        title="Test Status Panel with overall progress", tc_log=_LOGGER,
        overall_progress_iterable=[
            ([1, 2, 3, 4], "task 1", "start"),
            ([1, 2, 3, 4], "task 2", "next"),
            ([1, 2, 3, 4], "task 3", "done"),
            ([1, 2, 3, 4], "task 4", "close"),
        ]
    )
    with _sp:
        _p = _sp.progress
        _s = _sp.status
        _time = 0.2

        for _sequence, _task_name, _status in _s:
            for _ in _p.track(sequence=_sequence, task_name=_task_name):
                time.sleep(_time)
            _s.update(spinner_speed=1.0, spinner=None, status=_status)
            time.sleep(_time)
            _LOGGER.info("jjjjj")


def try_fit_progress_status_panel():
    with richy.FitProgressStatusPanel(
        title="Fitting ...", tc_log=_LOGGER, epochs=5,
    ) as _panel:
        _status_panel = _panel.status
        _train_progress = _panel.train_progress
        _validate_progress = _panel.validate_progress
        _train_samples = 200000
        _validate_samples = 100000
        for _epoch in _status_panel:
            _train_task = _train_progress.add_task(
                task_name=f"ep {_epoch:03d}", total=_train_samples,
                acc=float("nan"), loss=float("inf")
            )
            for _ in range(_train_samples):
                _train_task.update(advance=1, acc=_*0.1, loss=_*0.01)
            _validate_task = _validate_progress.add_task(
                task_name=f"ep {_epoch:03d}", total=_validate_samples,
                acc=float("nan"), loss=float("inf")
            )
            for _ in range(_validate_samples):
                _validate_task.update(advance=1, acc=_*0.1, loss=_*0.01)


def main():
    try_progress()
    try_status()
    try_status_panel()
    try_fit_progress_status_panel()


if __name__ == '__main__':
    main()
