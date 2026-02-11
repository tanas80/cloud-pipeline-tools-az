from datetime import datetime, timedelta

from azurebatch_cleanup.criteria import CleanupJobCriteria, evaluate_job
from data_builders import _job, _task


def test_criteria__age_match() -> None:
    criteria = CleanupJobCriteria(age=timedelta(days=3))
    job = _job(last_modified=datetime.fromisoformat(
        "2020-01-01T00:00:00+00:00"))
    decision = evaluate_job(
        job, [], criteria,
        now=datetime.fromisoformat("2020-01-10T00:00:00+00:00"))
    assert decision.can_delete is True
    assert decision.reasons == ["age"]


def test_criteria__age_mismatch() -> None:
    criteria = CleanupJobCriteria(age=timedelta(days=3))
    job = _job(last_modified=datetime.fromisoformat(
        "2020-01-10T00:00:00+00:00"))
    decision = evaluate_job(
        job, [], criteria,
        now=datetime.fromisoformat("2020-01-10T00:00:00+00:00"))
    assert decision.can_delete is False
    assert decision.reasons == []

