from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from datetime import datetime
from tqdm import tqdm

from . import cp_api
from .criteria import CleanupJobCriteria, Decision, evaluate_job
from .io import ConsoleIO
from .models import JobModel, TaskModel

logger = logging.getLogger(__name__)

ListJobsFn = Callable[[], List[JobModel]]
ListTasksFn = Callable[[str], List[TaskModel]]
DeleteJobFn = Callable[[str], None]
GetTasksRunInfoFn = Callable[[Iterable[str]], cp_api.CpApiTaskRunInfoResponse]


@dataclass(frozen=True)
class JobWithTasks:
    job: JobModel
    tasks: List[TaskModel]
    decision: Decision


def collect_jobs(
    list_jobs: ListJobsFn,
    list_tasks: ListTasksFn,
    criteria: CleanupJobCriteria,
    get_tasks_run_info: GetTasksRunInfoFn,
    now: datetime,
) -> List[JobWithTasks, ]:
    jobs = list_jobs()
    tasks: Dict[str, List[TaskModel]] = {}
    all_task_id_list: List[str] = []

    for job in tqdm(jobs, desc="Collecting job data", unit="job"):
        job_id = job.id
        tasks[job_id] = job_tasks = list_tasks(job_id)
        for task in job_tasks:
            all_task_id_list.append(task.id)

    # fetch all tasks run info for efficiency
    task_run_completed = None
    if criteria.task_run_completed is not None and all_task_id_list:
        task_run_completed = get_run_completed(
            all_task_id_list,
            cp_api.id2key_azur_to_nextflow,
            get_tasks_run_info,
        )

    jobs_res: List[JobWithTasks] = []
    for job in tqdm(jobs, desc="Collecting job data", unit="job"):
        job_id = job.id
        job_tasks = tasks[job_id]
        decision: Decision = evaluate_job(
            job,
            job_tasks,
            criteria,
            now,
            task_run_completed
        )
        job_with_tasks = JobWithTasks(job, job_tasks, decision)
        jobs_res.append(job_with_tasks)
    return jobs_res


def get_run_completed(
    all_task_id_list: Iterable[str],
    id2key: Callable[[str], str],
    get_tasks_run_info: GetTasksRunInfoFn,
) -> Dict[str, bool]:
    all_task_key_list: List[str] = []
    key2id: Dict[str, str] = {}
    for task_id in all_task_id_list:
        task_key = id2key(task_id.strip())
        all_task_key_list.append(task_key)
        key2id[task_key] = task_id.strip()

    tasks_run_info_response = get_tasks_run_info(all_task_key_list)
    task_run_completed = cp_api.get_task_key_run_completed_map(
        key2id,
        tasks_run_info_response)

    return task_run_completed


def format_candidate(candidate: JobWithTasks) -> List[str]:
    job = candidate.job
    header = f"job_id: {job.id}, state: {job.state}, display_name: {job.display_name or '<None>'}"
    lines = [header]
    if candidate.tasks:
        for task in candidate.tasks:
            lines.append(f"  task_id: {task.id}, state: {task.state or ''}")
    else:
        lines.append("  tasks: []")

    if candidate.decision.reasons:
        lines.append(f"  reasons: {', '.join(candidate.decision.reasons)}")
    return lines


def run_cleanup(
    list_jobs: ListJobsFn,
    list_tasks: ListTasksFn,
    get_tasks_run_info: GetTasksRunInfoFn,
    delete_job: DeleteJobFn,
    criteria: CleanupJobCriteria,
    *,
    dry_run: bool,
    assume_yes: bool,
    ignore_errors: bool,
    io: ConsoleIO,
    now: datetime,
) -> int:
    job_list = collect_jobs(
        list_jobs,
        list_tasks,
        criteria,
        get_tasks_run_info,
        now,
    )
    if not job_list:
        io.print("No jobs matched deletion criteria.")
        return 0

    candidate_list = [job for job in job_list if job.decision.can_delete]
    io.print(f"Jobs for deletion: {len(candidate_list)}/{len(job_list)}")
    for candidate in candidate_list:
        io.print_lines(format_candidate(candidate))

    if dry_run:
        io.print("Dry-run mode: no deletions performed.")
        return 0

    if not assume_yes:
        if not io.confirm("Delete these jobs? [y/N]: "):
            io.print("Aborted by user.")
            return 0

    for candidate in candidate_list:
        job_id = candidate.job.id
        try:
            delete_job(job_id)
            io.print(f"Deleted job: {job_id}")
        except Exception as exc:  # pragma: no cover - failure path
            logger.error("Failed to delete job %s: %s", job_id, exc)
            if not ignore_errors:
                return 1

    return 0
