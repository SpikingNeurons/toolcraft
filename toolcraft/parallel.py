"""
Multi-Threading and Multi-Processing.

There are multiple patterns we would like to implement

# [1] For Multi-Processing
## [1.1] Divide job among multiple workers to run in parallel
   https://pymotw.com/2/multiprocessing/communication.html


# [2] For Multi-Threading

"""

import multiprocessing as mp
import typing as t
import dataclasses
import queue
import time
import numpy as np
import abc

from . import util

_KILL_PILL = "__KILL_PILL__"


@dataclasses.dataclass
class Task(abc.ABC):

    @abc.abstractmethod
    def do_it(self, task_runner: "TaskRunner") -> t.Any:
        ...


@dataclasses.dataclass
class _Task(Task):
    name: str
    sleep_time: int

    def do_it(self, task_runner: "TaskRunner") -> t.Any:
        time.sleep(self.sleep_time)
        return f"Task result {self.name} {id(task_runner)}"


class TaskRunner:

    def setup(self):
        ...


class ProcessWithQueues(mp.Process):

    def __init__(
        self,
        task_queue: mp.JoinableQueue,
        result_queue: mp.Queue,
        task_runner: TaskRunner
    ):
        # call super
        super().__init__()

        # setup queues
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.task_runner = task_runner

    def run(self):
        self.task_runner.setup()
        while True:
            next_task = self.task_queue.get()  # type: Task
            if next_task == _KILL_PILL:
                # Poison pill means shutdown
                self.task_queue.task_done()
                break
            _result = next_task.do_it(
                self.task_runner
            )
            self.task_queue.task_done()
            self.result_queue.put(_result)


class TaskRunnerPool:

    @property
    @util.CacheResult
    def processes(self) -> t.List[mp.Process]:
        return [
            ProcessWithQueues(
                task_queue=self.task_queue, result_queue=self.result_queue,
                task_runner=_tr
            ) for _tr in self.task_runners
        ]

    def __init__(
        self,
        tasks: t.Iterator[Task],
        task_runners: t.List[TaskRunner],
    ):
        self.task_runners = task_runners
        self.task_queue = mp.JoinableQueue()
        self.result_queue = mp.Queue()

        def _task_yielder() -> t.Iterator[Task]:
            # add tasks
            for _ in tasks:
                yield _

            # add kill pill task for each task runner
            for _ in range(len(task_runners)):
                yield _KILL_PILL

        self.task_iterator = _task_yielder()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        # start task runners
        for _p in self.processes:
            _p.start()

        # at start we will put some tasks
        for _ in range(3*len(self.task_runners)):
            self.task_queue.put(next(self.task_iterator))

    def stop(self):
        # start task runners
        for _p in self.processes:
            _p.terminate()

    def get_results(self) -> t.Iterable[t.Any]:
        _time_for_retrieval = 2.
        _num_task_runners = len(self.task_runners)
        _tasks_available = True

        # yield until queue is empty
        while True:
            # go to sleep
            # todo: see if it has any impact and then change
            # time.sleep(_time_for_retrieval)

            # grow task queue if small
            if _tasks_available:
                if self.task_queue.qsize() < 2*_num_task_runners:
                    for _ in range(_num_task_runners):
                        try:
                            self.task_queue.put(next(self.task_iterator))
                        except StopIteration:
                            _tasks_available = False
                            break

            try:
                # estimate time to retrieve next result based on queue length
                _num_results = self.result_queue.qsize()
                if _num_results > 1:
                    _time_for_retrieval /= _num_results
                elif _num_results == 0:
                    _time_for_retrieval *= 1.1

                # get result
                _ret = self.result_queue.get(block=False)

                # yield
                yield _ret
            except queue.Empty:
                if self.task_queue.qsize() == 0:
                    break

        # let all task runners finish their job
        self.task_queue.join()

    @classmethod
    def test(cls):

        _trp = TaskRunnerPool(
            tasks=[
                _Task(f"{_i}_{_}", _)
                for _i, _ in enumerate(np.random.randint(5, 6, 20))
            ],
            task_runners=[
                TaskRunner() for _ in range(2)
            ]
        )
        _trp.start()
        for _res in _trp.get_results():
            print(_res)


# if __name__ == '__main__':
#     TaskRunnerPool.test()
