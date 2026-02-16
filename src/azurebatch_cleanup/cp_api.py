from __future__ import annotations

import json
import os
from dataclasses import dataclass
import re
from ssl import SSLContext
from typing import Any, Dict, Iterable, List, Optional
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field


def is_run_completed(status: str) -> bool:
    return status in ['STOPPED', 'FAILURE', 'SUCCESS']


@dataclass(frozen=True)
class CpApiConfig:
    base_url: str
    token: str


class CpApiRunInfo(BaseModel):
    status: str
    model_config = ConfigDict(extra="ignore")


class CpApiRunItem(BaseModel):
    run: CpApiRunInfo
    engine_task_keys: List[str] = Field(
        default_factory=list, alias="engineTaskKeys")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class CpApiTaskRunInfoResponse(BaseModel):
    payload: List[CpApiRunItem] = Field(default_factory=list)
    status: str

    model_config = ConfigDict(extra="ignore")


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/"


def _load_config(
    base_url: Optional[str] = None,
    token: Optional[str] = None,
) -> CpApiConfig:
    resolved_base = base_url or os.getenv("CP_API")
    resolved_token = token or os.getenv("CP_API_TOKEN")
    if not resolved_base:
        raise ValueError("CP_API environment variable is required")
    if not resolved_token:
        raise ValueError("CP_API_TOKEN environment variable is required")
    return CpApiConfig(base_url=_normalize_base_url(resolved_base), token=resolved_token)


def _build_run_info_url(base_url: str, engine_type: str) -> str:
    return f"{base_url}run/engine/{engine_type}/tasks/runInfo"


def id2key_azur_to_nextflow(task_id: str) -> str:
    return re.sub(
        r"^nf-([a-f0-9]{2})([a-f0-9]{6}).*$",
        r"\1/\2",
        task_id)


def get_run_info_by_engine_task_keys(
    keys_list: Iterable[str],
    engine_type: str,
    *,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    timeout_seconds: int = 30,
    ssl_context: SSLContext | None = None,
) -> Dict[str, Any]:
    if not keys_list:
        raise ValueError("At least one engine task key must be provided")

    config = _load_config(base_url=base_url, token=token)
    url = _build_run_info_url(config.base_url, engine_type)
    payload = json.dumps({"engineTaskKeys": keys_list}).encode("utf-8")

    request = Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.token}",
            "Content-Type": "application/json",
        },
    )

    with urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
        body = response.read().decode("utf-8")
    return json.loads(body or "{}")


def parse_task_run_info(run_info: Dict[str, Any]) -> CpApiTaskRunInfoResponse:
    return CpApiTaskRunInfoResponse.model_validate(run_info)


def get_tasks_run_info(
    task_keys: Iterable[str],
    *,
    engine_type: str = "NEXTFLOW",
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    timeout_seconds: int = 30,
    ssl_context: SSLContext | None = None,
) -> CpApiTaskRunInfoResponse:
    run_info = get_run_info_by_engine_task_keys(
        task_keys,
        engine_type=engine_type,
        base_url=base_url,
        token=token,
        timeout_seconds=timeout_seconds,
        ssl_context=ssl_context,
    )
    return parse_task_run_info(run_info)


def get_task_key_run_completed_map(
    key2id: Dict[str, str],
    run_info: CpApiTaskRunInfoResponse,
) -> Dict[str, bool]:
    res: Dict[str, bool] = {}
    for item in run_info.payload:
        completed: bool = is_run_completed(item.run.status)
        for key in item.engine_task_keys:
            task_id = key2id[key]
            if task_id in res:
                raise KeyError(
                    f"Duplicate task_id: '{task_id}', key: '{key}'.")
            res[task_id] = completed
    return res
