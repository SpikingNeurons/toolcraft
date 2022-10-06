
import enum
import typing as t
import dataclasses
import pickle
import sys
import pickle
import os
import pathlib
import numpy as np
sys.path.append("..")

from toolcraft import job
from toolcraft import settings
from toolcraft import util
from toolcraft import logger

_LOGGER = logger.get_logger()


@dataclasses.dataclass(frozen=True)
class Experiment(job.Experiment):

    a: int
    runner: "Runner"


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
            other_jobs=[],
        )


if __name__ == '__main__':
    _runner = Runner()
    _runner.run(
        job.JobRunnerClusterType.ibm_lsf
        if False else
        job.JobRunnerClusterType.local
    )
    _runner.view()
