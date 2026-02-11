from datetime import datetime, timedelta
from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from data_builders import _job, _task, test_now


def test_criteria__empty_match__age_match() -> None:
    criteria = CleanupJobCriteria(empty=timedelta(minutes=10))
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(minutes=11)),
        [], criteria,
        test_now)
    assert decision.can_delete is True
    assert decision.reasons == ["empty"]


def test_criteria__empty_mismatch__age_match() -> None:
    criteria = CleanupJobCriteria(empty=timedelta(minutes=10))
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(minutes=11)),
        [_task("task-1")], criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []


def test_criteria__empty_match__age_mismatch() -> None:
    criteria = CleanupJobCriteria(empty=timedelta(minutes=10))
    decision = evaluate_job(
        _job(last_modified=test_now - timedelta(minutes=9)),
        [], criteria,
        test_now)
    assert decision.can_delete is False
    assert decision.reasons == []
