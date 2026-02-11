from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from .models import JobModel, TaskModel, ensure_utc


@dataclass(frozen=True)
class CleanupTaskCriteria:
    id_pattern: Optional[str]
    nf_workdir: Optional[str]
    age: timedelta


@dataclass(frozen=True)
class CleanupJobCriteria:
    age: Optional[timedelta]
    empty: Optional[timedelta]
    task: Optional[CleanupTaskCriteria]

    def __init__(
        self,
        *,
        age: Optional[timedelta] = None,
        empty: Optional[timedelta] = None,
        task_id_pattern: Optional[str] = None,
        task_nf_workdir: Optional[str] = None,
        task_age: Optional[timedelta] = None,
    ) -> None:
        object.__setattr__(self, "age", age)
        object.__setattr__(self, "empty", empty)
        if task_id_pattern is not None or task_nf_workdir is not None:
            if task_age is None:
                raise ValueError(
                    "'task_age' is required when 'task_id_pattern' or 'task_nf_workdir' is provided"
                )
            object.__setattr__(self, "task", CleanupTaskCriteria(
                id_pattern=task_id_pattern,
                nf_workdir=task_nf_workdir,
                age=task_age,
            ))
        else:
            object.__setattr__(self, "task", None)


@dataclass(frozen=True)
class Decision:
    can_delete: bool
    reasons: List[str]


def _format_duration(delta: timedelta) -> str:
    parts: List[str] = []
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return "".join(parts) if parts else "0s"


def _matches_age(job: JobModel, age: timedelta, now: datetime) -> bool:
    last_modified = job.last_modified
    if last_modified is None:
        return False
    now_utc = ensure_utc(now or datetime.now(timezone.utc))
    cutoff = now_utc - age
    return ensure_utc(last_modified) <= cutoff


def _matches_empty(
    job: JobModel,
    tasks: Iterable[TaskModel],
    empty_age: timedelta,
    now: datetime,
) -> bool:
    return len(list(tasks)) == 0 and _matches_age(job, empty_age, now)


def _matches_every_task(
    job: JobModel,
    tasks: Iterable[TaskModel],
    taskCriteria: CleanupTaskCriteria,
    now: datetime,
) -> bool:
    """Check if all tasks satisfy the requested pattern/workdir/age constraints."""
    task_list = list(tasks)  # Ensure we can iterate multiple times
    task_id_pattern_match = True
    if taskCriteria.id_pattern is not None:
        task_id_re = re.compile(taskCriteria.id_pattern)

        def check_task_id(task: TaskModel) -> bool:
            return task_id_re.search(task.id or "") is not None

        task_id_pattern_match = len(task_list) > 0 and \
            all(check_task_id(task) for task in task_list)

    nf_workdir_match = True
    if taskCriteria.nf_workdir is not None:
        workdir_re = re.compile(taskCriteria.nf_workdir)

        def check_workdir(task: TaskModel, ) -> bool:
            resource_file = next(
                (rf for rf
                    in task.resource_files or []
                    if rf.file_path == ".command.run"),
                None
            )
            return resource_file is not None and workdir_re.search(resource_file.http_url or "") is not None

        nf_workdir_match = len(task_list) > 0 and \
            all(check_workdir(task) for task in task_list)

    age_match = _matches_age(job, taskCriteria.age, now)

    return task_id_pattern_match and nf_workdir_match and age_match


def evaluate_job(
    job: JobModel,
    tasks: List[TaskModel],
    criteria: CleanupJobCriteria,
    now: datetime,
) -> Decision:
    reasons: List[str] = []

    # Match --empty
    match_empty = False
    if criteria.empty is not None:
        match_empty = _matches_empty(job, tasks, criteria.empty, now)

    # Match --age (independent, global age filter)
    match_age = _matches_age(job, criteria.age, now) \
        if criteria.age is not None else False

    # Match --task-id-pattern and/or --task-nf-workdir with --task-age)
    match_task = False
    if (criteria.task is not None):
        match_task = _matches_every_task(job, tasks, criteria.task, now)

    match_res = match_age or match_empty or match_task

    if match_res:
        if criteria.age is not None and match_age:
            reasons.append(f"age")

        if criteria.empty is not None and match_empty:
            reasons.append(f"empty")

        if criteria.task is not None and match_task:
            reasons.append("task")

        if not reasons:
            raise ValueError("Unexpected criteria")

    return Decision(can_delete=match_res, reasons=reasons)
