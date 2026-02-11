from datetime import timedelta

from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from data_builders import _job, _task, _task_with_workdir, test_now


def test_task_id_pattern_match__task_nf_workdir_match__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3),
    )
    tasks = [
        _task_with_workdir(
            "task-1",
            "https://example.test/batch/work/abc"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is True
    assert decision.reasons == ["task"]


def test_task_id_pattern_mismatch__task_nf_workdir_match__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3),
    )
    tasks = [
        _task_with_workdir(
            "task-other-id",
            "https://example.test/batch/work/abc"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test_task_id_pattern_match__task_nf_workdir_mismatch__task_age_match() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3),
    )
    tasks = [
        _task_with_workdir(
            "task-1",
            "https://example.test/batch/work/other"),
    ]
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(days=4)),
        tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test_task_id_pattern_match__task_nf_workdir_match__task_age_mismatch() -> None:
    criteria = CleanupJobCriteria(
        task_id_pattern=r"^task-\d+$",
        task_nf_workdir="/work/abc",
        task_age=timedelta(days=3),
    )
    job = _job(last_modified=test_now - timedelta(days=2))
    tasks = [
        _task_with_workdir(
            "task-1",
            "https://example.test/batch/work/abc"),
    ]
    decision = evaluate_job(
        job, tasks, criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []
