import json
from pathlib import Path
from typing import Iterable, List

from azurebatch_cleanup import cp_api, core


def _load_task_run_info(task_keys: List[str]) -> cp_api.CpApiTaskRunInfoResponse:
    fixtures_path = Path(__file__).resolve()\
        .parents[1] / "examples" / "cp_api_tasks_run_info.json"
    payload = json.loads(fixtures_path.read_text(encoding="utf-8"))
    if not payload.get("payload"):
        raise ValueError("Expected payload items in CP API fixture")
    payload["payload"][0]["engineTaskKeys"] = task_keys
    return cp_api.parse_task_run_info(payload)


def test__get_run_completed() -> None:
    task_id_list = [
        "nf-ab123abc0123456789abcdef",
        "nf-cd456cde0123456789abcdef",
    ]
    task_keys = [cp_api.id2key_azur_to_nextflow(
        task_id) for task_id in task_id_list]
    captured_keys: List[str] = []

    def get_tasks_run_info_stub(keys: Iterable[str]) -> cp_api.CpApiTaskRunInfoResponse:
        captured_keys.extend(list(keys))
        run_info = _load_task_run_info(["ab/123abc"])
        return run_info

    result = core.get_run_completed(
        task_id_list,
        cp_api.id2key_azur_to_nextflow,
        get_tasks_run_info_stub,
    )

    assert captured_keys == task_keys
    assert result == {
        task_id_list[0]: True,
    }
