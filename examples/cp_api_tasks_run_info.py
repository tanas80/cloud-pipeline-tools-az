from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import ssl
import sys
from typing import Optional

from azurebatch_cleanup.cp_api import (
    get_run_info_by_engine_task_keys
)

from azurebatch_cleanup.env import load_env


@dataclass(frozen=True)
class CliOptions:
    task_id: str
    out: str
    insecure: bool


def save_tasks_run_info_to_file(
    run_info: Dict[str, Any],
    output_path: str,
) -> Dict[str, Any]:
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(run_info, handle, indent=2, ensure_ascii=False)
    return run_info


def _load_task_ids(path: Path) -> list[str]:
    # if not path.exists():
    #     raise FileNotFoundError(f"Task id file not found: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    if path.suffix.lower() == ".json":
        data = json.loads(content)
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise ValueError(
                "JSON task id file must contain a list of strings")
        return [item.strip() for item in data if item.strip()]

    return [line.strip() for line in content.splitlines() if line.strip()]


def _build_parser() -> CliOptions:
    parser = argparse.ArgumentParser(
        description="Fetch CP API task run info and save it to a JSON file."
    )
    parser.add_argument(
        "--task-id", type=str, required=True,
        help="path to file with task ids (one per line or JSON array)")
    parser.add_argument(
        "--out", type=str, required=True,
        help="path to output JSON file")
    parser.add_argument(
        "--insecure", action="store_true",
        help="disable SSL certificate verification")
    args = parser.parse_args()
    return CliOptions(**vars(args))


def main() -> None:
    load_env()
    opts = _build_parser()

    task_key_list = _load_task_ids(Path(opts.task_id))

    ssl_context = None
    if opts.insecure:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    run_info = get_run_info_by_engine_task_keys(
        task_key_list,
        "NEXTFLOW",
        ssl_context=ssl_context
    )
    save_tasks_run_info_to_file(run_info, str(opts.out))
    print(f"Saved response to {opts.out}")


if __name__ == "__main__":
    raise SystemExit(main())
