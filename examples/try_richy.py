
import sys
import time
import typing as t
sys.path.append("..")

from toolcraft import richy, logger
from toolcraft import marshalling as m

_LOGGER = logger.get_logger()


def try_progress():
    for _ in richy.Progress.simple_track(
        title="Try Progress", sequence=[1, 2, 3, 4], tc_log=_LOGGER,
        console=None,
    ):
        time.sleep(1)

    _sp = richy.Progress.simple_progress(
        title="Try Progress inside Progress",
        tc_log=_LOGGER,
        console=None,
    )
    with _sp:
        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="main"):
            for __ in _sp.track(sequence=[3, 3, 3, 3], task_name=f"child {_}"):
                time.sleep(0.25)

    with richy.Progress.for_download_and_hashcheck(
        title="Try Progress Download HashCheck", tc_log=_LOGGER,
        console=None,
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
        _s.append_to_summary("Hi I am A")
        _s.append_to_summary("Hi I am B")
        _s.append_to_summary("Hi I am C")

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
            _sp.append_to_summary("Hi I am A")
            _sp.append_to_summary("Hi I am B")
            _sp.append_to_summary("Hi I am C")

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

        for _ in _sp.track(sequence=[1, 2, 3, 4], task_name="main"):
            for __ in _sp.track(sequence=[3, 3, 3, 3], task_name=f"child {_}"):
                time.sleep(_time)

        # _sp.set_final_message(msg="\n---\n + I am done ... \n + See you soon ...")
        _sp.set_final_message(msg=" + I am done ... \n + See you soon ...")
        _sp.append_to_summary("Hi I am A")
        _sp.append_to_summary("Hi I am B")
        _sp.append_to_summary("Hi I am C")

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
            _sp.append_to_summary("Hi I am A")
            _sp.append_to_summary("Hi I am B")
            _sp.append_to_summary("Hi I am C")


def try_fit_progress_status_panel():

    _train_samples = 5
    _validate_samples = 5
    _fit_panel = richy.StatusPanel(
        tc_log=_LOGGER, sub_title=["aaa", "bbb", "ccc"]
    )

    with _fit_panel:

        _train_task_fetcher, _validate_task_fetcher = \
            _fit_panel.convert_to_fit_status_panel(epochs=30)
        _msg_fmt = "[green]A {acc:.2f} [yellow]L {loss:.2f}"

        for _i, _epoch in enumerate(_fit_panel):
            _train_task = _train_task_fetcher()
            _validate_task = _validate_task_fetcher()
            _fit_panel.update("estimating total ;) ...")
            _train_task.update(total=_train_samples)
            _validate_task.update(total=_validate_samples)
            for _ in range(_train_samples):
                _train_task.update(
                    advance=1,
                    msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
                )
            for _ in range(_validate_samples):
                _validate_task.update(
                    advance=1,
                    msg=_msg_fmt.format(acc=_*0.1, loss=_*0.01),
                )
            _fit_panel.append_to_summary(
                f"+ {_epoch}: [train] acc {0.23:.03f} loss {0.23:.03f} | [validation] acc {0.23:.03f} loss {0.23:.03f}",
                highlight_line=_i if _i < 15 else 15,
            )
            if _epoch == "epoch 30":
                _fit_panel.set_final_message(
                    msg=f"---\n"
                        f"Currently at {_epoch}. \n"
                        f"Found best epoch at {2} for val loss {0.004}. \n"
                        f"+ train   : acc: {1.0} | loss: {4.33} \n"
                        f"+ validate: acc: {1.0} | loss: {4.33} \n"
                        f"---"
                )


class HashableCLass(m.HashableClass):
    ...


def try_hashable_status_panel():

    _hashable = HashableCLass()

    _rp = richy.StatusPanel(
        tc_log=_LOGGER, title="Tracker(...).richy_panel", sub_title=_hashable,
        stages=["start", "download", "hashcheck", "finish"],
    )
    with _rp, _hashable(richy_panel=_rp):
        # update status message
        _hashable.richy_panel.update(status="updating status message ...")
        time.sleep(1)

        # adding task via `track()`
        _hashable.richy_panel.update(status="adding task via `track()` ...")
        for _ in _hashable.richy_panel.track([1, 2, 3, 4], task_name="task via track()", msg="fff"):
            time.sleep(0.2)

        # adding task via `add_task()`
        _hashable.richy_panel.update(status="adding task via `add_task()` ...")
        _task = _hashable.richy_panel.add_task(task_name="task via add_task()", total=5, msg="rrr")
        for _ in range(5):
            _task.update(advance=1, msg=f"Doing {_}")
            time.sleep(0.2)

        # testing stages
        _hashable.richy_panel.update(status="testing stages ...")
        for _stage in _hashable.richy_panel:
            for _ in _hashable.richy_panel.track(
                [1, 2, 3, 4], task_name="loop", msg="fff", prefix_current_stage=True
            ):
                time.sleep(0.2)

        # adding widget on the fly
        _hashable.richy_panel.update(status="adding widget on the fly ...")
        time.sleep(1)
        _hashable.richy_panel["on the fly 1"] = richy.r_markdown.Markdown("# on the fly \n+ one")
        _hashable.richy_panel["on the fly 2"] = richy.r_markdown.Markdown("# on the fly \n+ two")

        # ask question
        # todo: support this ...
        # response = richy.r_prompt.Confirm.ask(
        #     f"Do you want to delete files for Folder?",
        #     default=True, console=_hashable.richy_panel.console
        # )

        # setting final message
        _hashable.richy_panel.update(status="setting final message ...")
        time.sleep(1)
        _hashable.richy_panel.set_final_message("+ i am done \n+ see you again")


def main():
    # try_progress()
    # try_status_panel()
    try_fit_progress_status_panel()
    # try_hashable_status_panel()


if __name__ == '__main__':
    main()
