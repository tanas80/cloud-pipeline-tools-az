from datetime import datetime, timedelta
from typing import Iterable, List, Optional

from azurebatch_cleanup import cp_api
from azurebatch_cleanup.core import run_cleanup
from azurebatch_cleanup.io import ConsoleIO
from azurebatch_cleanup.criteria import CleanupJobCriteria
from data_builders import _job, _task, test_now


class Recorder:
    def __init__(self) -> None:
        self.lines: List[str] = []

    def __call__(self, message: str) -> None:
        self.lines.append(message)


class FixedInput:
    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self, prompt: str) -> str:
        return self.value


def test_core__dry_run_only_prints() -> None:
    job = _job()
    tasks: List = []

    def list_jobs():
        return [job]

    def list_tasks(job_id: str):
        return tasks

    def get_tasks_run_info(task_id_list: Iterable[str]) -> cp_api.CpApiTaskRunInfoResponse:
        return cp_api.CpApiTaskRunInfoResponse({})

    deleted: List[str] = []

    def delete_job(job_id: str) -> None:
        deleted.append(job_id)

    io = ConsoleIO(printer=Recorder(), reader=FixedInput("no"))
    criteria = CleanupJobCriteria(
        empty=timedelta(minutes=10)
    )

    code = run_cleanup(
        list_jobs,
        list_tasks,
        get_tasks_run_info,
        delete_job,
        criteria,
        dry_run=True,
        assume_yes=False,
        ignore_errors=False,
        io=io,
        now=test_now
    )

    assert code == 0
    assert deleted == []


def test_core__confirm_and_delete() -> None:
    job = _job(
        id='job-1', last_modified=datetime.fromisoformat("2020-01-01T00:00:00+00:00"))

    def list_jobs():
        return [job]

    def list_tasks(job_id: str):
        return []

    def get_tasks_run_info(task_id_list: Iterable[str]) -> cp_api.CpApiTaskRunInfoResponse:
        return cp_api.CpApiTaskRunInfoResponse({})

    deleted: List[str] = []

    def delete_job(job_id: str) -> None:
        deleted.append(job_id)

    io = ConsoleIO(printer=Recorder(), reader=FixedInput("yes"))
    criteria = CleanupJobCriteria(
        empty=timedelta(minutes=10)
    )

    code = run_cleanup(
        list_jobs,
        list_tasks,
        get_tasks_run_info,
        delete_job,
        criteria,
        dry_run=False,
        assume_yes=False,
        ignore_errors=False,
        io=io,
        now=datetime.fromisoformat("2020-01-01T00:11:00+00:00")
    )

    assert code == 0
    assert deleted == [job.id]
