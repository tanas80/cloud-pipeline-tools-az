from datetime import timedelta

from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from azurebatch_cleanup.models import TaskModel
from data_builders import _job, _task, test_now


def test_criteria__task_id_pattern_match__task_age_missed() -> None:
    try:
        CleanupJobCriteria(task_id_pattern=r"^task-\d+$")
    except ValueError as exc:
        assert "task_age" in str(exc)
    else:
        raise AssertionError("Expected ValueError when task_age is missing")


def test_criteria__task_id_pattern_match__tasks_empty() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_age=timedelta(days=3))
    decision = evaluate_job(
        _job(), [], criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test_criteria__task_id_pattern_match__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+",
        task_age=timedelta(days=3))
    tasks = [
        _task("task-11"),
        _task("task-23")
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is True
    assert decision.reasons == ["task"]


def test_criteria__task_id_pattern_mismatch__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_age=timedelta(days=3))
    tasks = [
        _task("task-1"),
        _task("oops")
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)), 
        tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []
