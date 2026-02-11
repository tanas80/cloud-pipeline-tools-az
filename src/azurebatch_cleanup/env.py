from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

def load_env(path: Optional[str] = None, *, override: bool = False) -> Path:
    env_path = Path(path or ".env")
    load_dotenv(dotenv_path=env_path, override=override)
    return env_path
