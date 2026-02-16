from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import ssl
from typing import Iterable, Optional

from pytimeparse.timeparse import timeparse

from . import az_cli
from .env import load_env
from .io import ConsoleIO
from .logging_utils import configure_logging
from .criteria import CleanupJobCriteria
from .core import run_cleanup
from . import cp_api


def parseDuration(interval_str: str) -> timedelta:
    """
    Parse time interval string and convert to timedelta.
    Supported formats: 1d, 2h, 30m, 45s, 1 day, 2 hours, 5 minutes, 30 seconds.
    Examples: "1d" -> timedelta(days=1), "48h" -> timedelta(hours=48)

    Args:
        interval_str: String with time interval (e.g., "1d", "2h", "30m", "45s")

    Returns:
        timedelta object

    Raises:
        ValueError: If format is invalid or unit is not recognized
    """
    seconds = timeparse(interval_str.strip())
    if seconds is None:
        raise ValueError(
            f"Invalid time interval format '{interval_str}'."
            " Supported: 1d, 2h, 30m, 45s, 1 day, 2 hours, 5 minutes, 30 seconds."
        )
    return timedelta(seconds=seconds)


@dataclass(frozen=True)
class CliOptions:
    age: Optional[timedelta]

    empty: Optional[timedelta]

    task_id_pattern: Optional[str]
    task_nf_workdir: Optional[str]
    task_age: Optional[timedelta]
    task_run_completed: Optional[timedelta]

    dry_run: bool
    yes: bool
    ignore_errors: bool

    log_level: Optional[str]
    insecure: bool


def _build_parser() -> CliOptions:
    parser = argparse.ArgumentParser(
        description="Delete Azure Batch jobs that are not completed and match criteria."
    )
    parser.add_argument(
        "--age", type=parseDuration, default=None,
        help="delete jobs older than specified time (based on lastModified)")

    parser.add_argument(
        "--empty", type=parseDuration, default=None,
        help="delete empty jobs older than specified time (based on lastModified)")

    parser.add_argument(
        "--task-id-pattern", type=str, default=None,
        help="regex: delete jobs where all task ids match pattern"
             "(use with --task-age)")
    parser.add_argument(
        "--task-nf-workdir", type=str, default=None,
        help="check if resourceFile with filePath='.command.run' "
             "has httpUrl containing this substring "
             "(use with --task-age)")
    parser.add_argument(
        "--task-age", type=parseDuration, default=None,
        help="delete jobs with matching --task-id-pattern and/or --task-nf-workdir "
             "older than specified time (based on lastModified of job)")

    parser.add_argument(
        "--task-run-completed", type=parseDuration, default=None,
        help="delete jobs where all tasks belong to runs with completed status via CP API"
             "older than specified time (based on lastModified of job)")

    parser.add_argument(
        "--dry-run", action="store_true",
        help="only show jobs to delete")
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="auto-confirm deletions")
    parser.add_argument(
        "--ignore-errors", action="store_true",
        help="continue deleting even if one deletion fails",
    )
    parser.add_argument(
        "--log-level", type=str, default="WARNING",
        help="logging level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument(
        "--insecure", action="store_true",
        help="disable SSL certificate verification")
    args = parser.parse_args()

    if args.empty is None and args.age is None and not args.task_id_pattern and args.task_run_completed is None:
        parser.error(
            "at least one filter must be set: --empty, --age, --task-id-pattern, or --task-run-completed")

    if (args.task_id_pattern is not None or args.task_nf_workdir is not None) and args.task_age is None:
        parser.error(
            "--task-age is required when using --task-id-pattern or --task-nf-workdir")

    return CliOptions(**vars(args))


def main() -> int:
    load_env()
    opts = _build_parser()

    configure_logging(opts.log_level)

    criteria = CleanupJobCriteria(
        age=opts.age,
        empty=opts.empty,
        task_id_pattern=opts.task_id_pattern,
        task_age=opts.task_age,
        task_nf_workdir=opts.task_nf_workdir,
        task_run_completed=opts.task_run_completed,
    )

    ssl_context = None
    if opts.insecure:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    def _get_tasks_run_info(task_id_list: Iterable[str]) -> cp_api.CpApiTaskRunInfoResponse:
        return cp_api.get_tasks_run_info(
            task_id_list,
            ssl_context=ssl_context,
        )

    io = ConsoleIO()
    return run_cleanup(
        az_cli.list_non_complete_jobs,
        az_cli.list_tasks,
        _get_tasks_run_info,
        az_cli.delete_job,
        criteria,
        dry_run=opts.dry_run,
        assume_yes=opts.yes,
        ignore_errors=opts.ignore_errors,
        io=io,
        now=datetime.now(tz=timezone.utc)
    )


if __name__ == "__main__":
    raise SystemExit(main())
