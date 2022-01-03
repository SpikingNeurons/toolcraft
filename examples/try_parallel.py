import dataclasses
import time
import typing as t

import numpy as np

from toolcraft import logger, parallel

_LOGGER = logger.get_logger()

_LOGGER.info(msg="try parallel ...")


@dataclasses.dataclass
class SomeTask(parallel.Task):
    def do_it(self, task_runner: "SomeTaskRunner") -> t.Tuple[int, int]:
        return task_runner.task_id, task_runner.fetch()


@dataclasses.dataclass
class SomeTaskRunner(parallel.TaskRunner):
    task_id: int

    def fetch(self) -> int:
        time.sleep(1)
        return 33


def main():

    _task_runners = [
        SomeTaskRunner(0),
        SomeTaskRunner(1),
    ]

    def _task_gen() -> t.Iterator[SomeTask]:
        for _ in range(20):
            yield SomeTask()

    _pool = parallel.TaskRunnerPool(task_runners=_task_runners,
                                    tasks=_task_gen())

    with _pool:
        for _res in _pool.get_results():
            print(_res)


if __name__ == "__main__":
    main()
