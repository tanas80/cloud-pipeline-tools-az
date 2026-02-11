"""Test data builders for creating JobModel and TaskModel objects."""

from datetime import datetime
from azurebatch_cleanup.models import JobModel, TaskModel

test_now = datetime.fromisoformat("2020-01-01T00:00:00+00:00")


def _job(
    *,
    id: str | None = None,
    last_modified: datetime | None = None
) -> JobModel:
    default_job = {
        "id": "job-default",
        "state": "active",
        "creationTime": "2020-01-01T00:00:00+00:00",
        "lastModified": "2020-01-01T00:00:00+00:00",
        "stateTransitionTime": "2020-01-01T00:00:00+00:00",
        "eTag": "test-etag",
        "url": "https://example.test/batch/jobs/job-default",
        "poolInfo": {"poolId": "test-pool"},
    }

    data = {
        **default_job,
    }
    if id is not None:
        data["id"] = id
    if last_modified is not None:
        data["lastModified"] = last_modified.isoformat()
    return JobModel(**data)  # type: ignore


def _task(task_id: str) -> TaskModel:
    default_task = {
        "id": "test-task-id",
        "state": "active",
        "creationTime": "2020-01-01T00:00:00+00:00",
        "lastModified": "2020-01-01T00:00:00+00:00",
        "stateTransitionTime": "2020-01-01T00:00:00+00:00",
        "eTag": "test-etag",
        "url": "https://example.test/batch/tasks/task-default",
        "commandLine": "echo test-task",
    }
    data = {
        **default_task,
        "id": task_id,
    }
    return TaskModel(**data)  # type: ignore


def _task_with_workdir(task_id: str, http_url: str) -> TaskModel:
    return TaskModel(
        **{
            "id": task_id,
            "state": "active",
            "creationTime": "2020-01-01T00:00:00+00:00",
            "lastModified": "2020-01-01T00:00:00+00:00",
            "stateTransitionTime": "2020-01-01T00:00:00+00:00",
            "eTag": "test-etag",
            "url": "https://example.test/batch/tasks/task-default",
            "commandLine": "echo test-task",
            "resourceFiles": [
                {
                    "filePath": ".command.run",
                    "httpUrl": http_url,
                }
            ],
        }
    )
