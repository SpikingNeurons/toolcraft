
import sys
import time
sys.path.append("..")

from toolcraft import richy, logger
from toolcraft import marshalling as m

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


def try_hashable_status_panel():
    class Tracker(m.Tracker):
        ...

    Tracker()


def try_status_panel():
    _sp = richy.ProgressStatusPanel(
        title="Test Status Panel", tc_log=_LOGGER
    )
    with _sp:
        _time = 0.2

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(_time)
        _sp.update(spinner_speed=1.0, spinner=None, status="start")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(_time)
        _sp.update(spinner_speed=1.0, spinner=None, status="next")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 3"):
            time.sleep(_time)
        _sp.update(spinner_speed=1.0, spinner=None, status="done")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 4"):
            time.sleep(_time)
        _sp.update(spinner_speed=1.0, spinner=None, status="close")
        time.sleep(_time)

    _sp = richy.ProgressStatusPanel(
        title="Test Status Panel with overall progress", tc_log=_LOGGER,
        stages=[
            ([1, 2, 3, 4], "task 1", "start"),
            ([1, 2, 3, 4], "task 2", "next"),
            ([1, 2, 3, 4], "task 3", "done"),
            ([1, 2, 3, 4], "task 4", "close"),
        ],
        stages_meta={

        }
    )

    _time = 0.2

    for _sequence, _task_name, _status in _sp:
        for _ in _sp.track(sequence=_sequence, task_name=_task_name):
            time.sleep(_time)
        _sp.update(spinner_speed=1.0, spinner=None, status=_status)
        time.sleep(_time)
        _LOGGER.info("jjjjj")


def try_fit_progress_status_panel():

    _fit_panel = richy.FitProgressStatusPanel(
        title="Fitting ...", tc_log=_LOGGER, epochs=5,
    )
    _train_samples = 200000
    _validate_samples = 100000
    _msg_fmt = "[green]A {acc:.2f} [yellow]L {loss:.2f}"

    for _epoch in _fit_panel:
        _train_task = _fit_panel.add_train_task(
            total=_train_samples, msg=_msg_fmt.format(acc=float("nan"), loss=float("inf")), )
        for _ in range(_train_samples):
            _train_task.update(
                advance=1,
                msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
            )
        _validate_task = _fit_panel.add_validate_task(
            total=_validate_samples, msg=_msg_fmt.format(acc=float("nan"), loss=float("inf")), )
        for _ in range(_validate_samples):
            _validate_task.update(
                advance=1,
                msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
            )

        if _epoch == 4:
            _fit_panel.set_final_message(
                msg=f"Found best epoch at {2} for val loss {0.004}"
                    f"\n+ train   : acc: {1.0} | loss: {4.33}"
                    f"\n+ validate: acc: {1.0} | loss: {4.33}"
            )


def main():
    # try_progress()
    # try_status()
    try_status_panel()
    # try_fit_progress_status_panel()
    # try_hashable_status_panel()


if __name__ == '__main__':
    main()
