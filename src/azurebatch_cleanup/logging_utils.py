from __future__ import annotations

import logging
from typing import Optional


def configure_logging(level: Optional[str]) -> None:
    if not level:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        return
    logging.basicConfig(level=level.upper(), format="%(levelname)s: %(message)s")
