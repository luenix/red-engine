
from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task, clear_tasks, get_task
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue
from atlas.core.parameters import GLOBAL_PARAMETERS
from atlas import session

import pytest
import logging
import sys
import time
import os
import multiprocessing


def run_failing():
    raise RuntimeError("Task failed")

def test_task_fail_traceback(tmpdir):
    # There is a speciality in tracebacks in multiprocessing
    # See: https://bugs.python.org/issue34334
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(run_failing, name="task", start_cond=AlwaysTrue(), execution="process")

        scheduler = Scheduler(
            [
                task,
            ], shut_condition=TaskStarted(task="task") >= 3
        )
        scheduler()
        history = task.get_history()
        failures = history[history["action"] == "fail"]
        assert 3 == len(failures)

        for tb in failures["message"]:
            assert "Traceback (most recent call last):" in tb
            assert "RuntimeError: Task failed" in tb
