
import enum
import typing as t
import dataclasses
import time
import sys
import asyncio
import os
import pathlib
import numpy as np
sys.path.append("..")

from toolcraft import job
from toolcraft import settings
from toolcraft import util
from toolcraft import logger
from toolcraft import gui

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class Experiment(job.Experiment):

    a: int
    runner: "Runner"

    async def some_awaitable_fn(self, txt_widget: "gui.widget.Text"):

        try:

            # loop infinitely
            while txt_widget.does_exist:

                # if not build continue
                if not txt_widget.is_built:
                    await asyncio.sleep(0.2)
                    continue

                # dont update if not visible
                # todo: can we await on bool flags ???
                if not txt_widget.is_visible:
                    await asyncio.sleep(0.2)
                    continue

                # update widget
                txt_widget.set_value(f"{int(txt_widget.get_value())+1:03d}")

                # change update rate based on some value
                await asyncio.sleep(0.1)
                if int(txt_widget.get_value()) == 50:
                    break

        except Exception as _e:
            if txt_widget.does_exist:
                raise _e
            else:
                ...

    @gui.UseMethodInForm(label_fmt="awaitable_task")
    def awaitable_task(self) -> "gui.widget.Group":
        _grp = gui.widget.Group(horizontal=True)
        with _grp:
            gui.widget.Text(default_value="count")
            _txt = gui.widget.Text(default_value="000")
            gui.AwaitableTask(
                fn=self.some_awaitable_fn, fn_kwargs=dict(txt_widget=_txt)
            ).add_to_task_queue()
        return _grp

    @gui.UseMethodInForm(label_fmt="blocking_task", run_async=True)
    def blocking_task(self) -> "gui.widget.Text":
        time.sleep(10)
        return gui.widget.Text(default_value="done sleeping for 10 seconds")




@dataclasses.dataclass(frozen=True)
class Runner(job.Runner):

    def some_job(self):
        _LOGGER.info(f"{(self.job.job_id, self.job.path)}")

    def some_job_experiment(self, experiment: Experiment):
        _LOGGER.info(f"{(self.job.job_id, self.job.path)}")
        if experiment.a == 44444:
            _msg = f"I just wanted to fail one job ... " \
                   f"Note that if cluster type is " \
                   f"{job.JobRunnerClusterType.local.name} " \
                   f"there will be no future jobs running ..."
            raise Exception(_msg)

    def end(self):
        _LOGGER.info(f"{(self.job.job_id, self.job.path, 'ended')}")

    @property
    @util.CacheResult
    def flow(self) -> job.Flow:
        _stage_1 = job.ParallelJobGroup(
            runner=self,
            jobs=[
                job.Job(
                    runner=self, method=self.setup,
                )
            ]
        )
        _stage_2 = job.ParallelJobGroup(
            runner=self,
            jobs=[
                job.Job(
                    runner=self, method=self.some_job,
                    wait_on=[_stage_1],
                ),
            ]
        )
        _stage_3 = job.ParallelJobGroup(
            runner=self,
            jobs=[
                job.Job(
                    runner=self, method=self.some_job_experiment,
                    experiment=Experiment(a=33333, runner=self),
                    wait_on=[_stage_2],
                ),
                job.Job(
                    runner=self, method=self.some_job_experiment,
                    experiment=Experiment(a=44444, runner=self),
                    wait_on=[_stage_2],
                ),
            ]
        )
        _stage_4 = job.ParallelJobGroup(
            runner=self,
            jobs=[
                job.Job(
                    runner=self, method=self.end,
                    wait_on=[_stage_3],
                )
            ]
        )
        return job.Flow(
            runner=self,
            stages=[
                _stage_1, _stage_2, _stage_3, _stage_4,
            ],
        )


if __name__ == '__main__':
    _runner = Runner()
    _runner.run(
        job.JobRunnerClusterType.ibm_lsf
        if False else
        job.JobRunnerClusterType.local
    )
    _runner.view()
