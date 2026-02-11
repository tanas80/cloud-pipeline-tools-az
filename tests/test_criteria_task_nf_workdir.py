from datetime import timedelta

from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from data_builders import _job, _task_with_workdir, test_now


def test__task_nf_workdir_match__task_age_missed() -> None:
    try:
        CleanupJobCriteria(task_nf_workdir="workdir")
    except ValueError as exc:
        assert "task_age" in str(exc)
    else:
        raise AssertionError("Expected ValueError when task_age is missing")


def test__task_nf_workdir_match__tasks_empty() -> None:
    criteria = CleanupJobCriteria(
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3))
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        [], criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test__task_nf_workdir_match__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3))
    tasks = [
        _task_with_workdir(
            "task-11",
            "https://example.test/batch/work/abc"),
        _task_with_workdir(
            "task-12",
            "https://example.test/batch/work/abc"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is True
    assert decision.reasons == ["task"]


def test__task_nf_workdir_mismatch__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3))
    tasks = [
        _task_with_workdir(
            "task-11",
            "https://example.test/batch/work/abc"),
        _task_with_workdir(
            "task-12",
            "https://example.test/batch/work/xyz"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test__task_nf_workdir_match__task_age_mismatch() -> None:
    criteria = CleanupJobCriteria(
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3))
    tasks = [
        _task_with_workdir(
            "task-11",
            "https://example.test/batch/work/abc"),
        _task_with_workdir(
            "task-12",
            "https://example.test/batch/work/abc"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=2)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []
