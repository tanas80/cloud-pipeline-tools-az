from datetime import timedelta

from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from data_builders import _job, _task, test_now


def test__task_run_completed_match__age_match__all_tasks_completed() -> None:
    criteria = CleanupJobCriteria(
        task_run_completed=timedelta(seconds=30),
    )
    tasks = [
        _task("task-1"),
        _task("task-2"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(seconds=35)),
        tasks,
        criteria,
        test_now,
        task_run_completed={
            "task-1": True,
            "task-2": True,
        },
    )
    assert decision.can_delete is True
    assert decision.reasons == ["task-run-completed"]


def test__task_run_completed_match__age_match__task_incomplete() -> None:
    criteria = CleanupJobCriteria(
        task_run_completed=timedelta(seconds=30),
    )
    tasks = [
        _task("task-1"),
        _task("task-2"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks,
        criteria,
        test_now,
        task_run_completed={
            "task-1": True,
            "task-2": False,
        },
    )
    assert decision.can_delete is False
    assert decision.reasons == []


def test__task_run_completed_match__age_match__missing_task_mapping() -> None:
    criteria = CleanupJobCriteria(
        task_run_completed=timedelta(seconds=30),
    )
    tasks = [
        _task("task-1"),
        _task("task-2"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks,
        criteria,
        test_now,
        task_run_completed={
            "task-1": True,
        },
    )
    assert decision.can_delete is False
    assert decision.reasons == []
