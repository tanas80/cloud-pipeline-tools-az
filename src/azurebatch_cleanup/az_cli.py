from __future__ import annotations

import json
import logging
import subprocess
from typing import List

from .models import JobModel, TaskModel

logger = logging.getLogger(__name__)


def _run_az(args: List[str]) -> str:
    logger.debug("Running az: %s", " ".join(args))
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "az command failed")
    return result.stdout


def list_non_complete_jobs() -> List[JobModel]:
    stdout = _run_az([
        "az",
        "batch",
        "job",
        "list",
        "--query",
        "[?state!='completed']",
    ])
    res = [JobModel.from_az(item) for item in json.loads(stdout or "[]")]
    return res


def list_tasks(job_id: str) -> List[TaskModel]:
    stdout = _run_az([
        "az",
        "batch",
        "task",
        "list",
        "--job-id",
        job_id,
    ])
    res = [TaskModel.from_az(item) for item in json.loads(stdout or "[]")]
    return res


def delete_job(job_id: str) -> None:
    _run_az([
        "az",
        "batch",
        "job",
        "delete",
        "--job-id",
        job_id,
        "--yes",
    ])
