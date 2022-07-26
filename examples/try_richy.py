
import sys
import time
sys.path.append("..")

from toolcraft import richy, logger
from toolcraft import marshalling as m

_LOGGER = logger.get_logger()


def try_progress():
    for _ in richy.Progress.simple_track(title="Try Progress", sequence=[1, 2, 3, 4], tc_log=_LOGGER):
        time.sleep(1)

    with richy.Progress.for_download_and_hashcheck(
        title="Try Progress Download HashCheck", tc_log=_LOGGER,
    ) as _p:
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(0.2)
        _p.log(["aaaa", "bbbb", "ccccc"])
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(0.2)
        for _ in _p.track(sequence=[1, 2, 3, 4], task_name="task 3"):
            time.sleep(0.2)


def try_status_panel():
    # ------------------------------------------------------------------- 01
    with richy.StatusPanel(
        tc_log=_LOGGER,
        title="Test Only Status"
    ) as _s:
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.dots, status="start")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.arrow, status="next")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.balloon, status="done")
        time.sleep(1)
        _s.update(spinner_speed=1.0, spinner=richy.SpinnerType.star, status="close")
        time.sleep(1)

    # ------------------------------------------------------------------- 02
    _stages_meta = {
        'start': richy.SpinnerType.dots,
        'next': richy.SpinnerType.arrow,
        'done': richy.SpinnerType.balloon,
        'close': richy.SpinnerType.star,
    }
    _sp = richy.StatusPanel(
        tc_log=_LOGGER,
        title="Test Status with overall progress",
        stages=['start', 'next', 'done', 'close'],
    )
    for _stage in _sp:
        _sp.update(spinner_speed=1.0, spinner=_stages_meta[_stage], status=_stage)
        _sp.log([f"phase {_stage}"])
        time.sleep(1)
        # on last stage end
        if _stage == 'close':
            # _sp.set_final_message(msg="\n---\n + I am done ... \n + See you soon ...")
            _sp.set_final_message(msg=" + I am done ... \n + See you soon ...")

    # ------------------------------------------------------------------- 03
    _sp = richy.StatusPanel(
        title="Test Status Panel with generic progress bar", tc_log=_LOGGER
    )
    with _sp:
        _time = 0.2

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 1"):
            time.sleep(_time)
        _sp.update(status="executing task 1 ...")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 2"):
            time.sleep(_time)
        _sp.update(status="executing task 2 ...")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 3", msg=":)"):
            time.sleep(_time)
        _sp.update(status="executing task 3 ...")
        time.sleep(_time)

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="task 4", msg=":("):
            time.sleep(_time)
        _sp.update(status="executing task 4 ...")
        time.sleep(_time)

        # _sp.set_final_message(msg="\n---\n + I am done ... \n + See you soon ...")
        _sp.set_final_message(msg=" + I am done ... \n + See you soon ...")

    # ------------------------------------------------------------------- 04
    _sp = richy.StatusPanel(
        title="Test Status Panel with generic and stages progress bar", tc_log=_LOGGER,
        stages=['start', 'next ', 'done ', 'close'],
    )
    _time = 0.1
    for _i, _stage in enumerate(_sp):
        time.sleep(_time)
        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name=f"task_0 {_i}", prefix_current_stage=True):
            time.sleep(_time)
        _task = _sp.add_task(
            task_name=f"task_1 {_i}", prefix_current_stage=True, total=4
        )
        for _ in [0, 1, 2, 3]:
            _task.update(advance=1, msg=f">> {[':(', ':|', ':o', ':)'][_]} <<")
            time.sleep(_time)
        if _stage == 'close':
            # _sp.set_final_message(msg="\n---\n + I am done ... \n + See you soon ...")
            _sp.set_final_message(msg=" + I am done ... \n + See you soon ...")


def try_fit_progress_status_panel():

    _train_samples = 20
    _validate_samples = 10
    _fit_panel = richy.FitStatusPanel(
        tc_log=_LOGGER, epochs=3,
        train_steps=_train_samples, validate_steps=_validate_samples,
    )
    _msg_fmt = "[green]A {acc:.2f} [yellow]L {loss:.2f}"

    for _epoch in _fit_panel:
        _train_task = _fit_panel.train_task
        _validate_task = _fit_panel.validate_task
        for _ in range(_train_samples):
            time.sleep(0.1)
            _train_task.update(
                advance=1,
                msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
            )
        for _ in range(_validate_samples):
            time.sleep(0.1)
            _validate_task.update(
                advance=1,
                msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
            )
        _fit_panel.append_to_summary(
            f"+ {_epoch}: [train] acc {0.23:.03f} loss {0.23:.03f} | [validation] acc {0.23:.03f} loss {0.23:.03f}")
        if _epoch == "epoch 3":
            _fit_panel.set_final_message(
                msg=f"---\n"
                    f"Currently at {_epoch}. \n"
                    f"Found best epoch at {2} for val loss {0.004}. \n"
                    f"+ train   : acc: {1.0} | loss: {4.33} \n"
                    f"+ validate: acc: {1.0} | loss: {4.33} \n"
                    f"---"
            )


def try_hashable_status_panel():
    class Tracker(m.Tracker):
        ...

    _tracker = Tracker()

    with _tracker(richy_panel=richy.StatusPanel(tc_log=_LOGGER, title="ggg")):
        time.sleep(1)


def main():
    # try_progress()
    # try_status_panel()
    # try_fit_progress_status_panel()
    try_hashable_status_panel()


if __name__ == '__main__':
    main()
