from datetime import time
from pathlib import Path

import richuru
from loguru import logger


def setup_logger(sink: Path, log_rotate: int, no_store_log: bool = False):
    if not no_store_log:
        logger.add(
            sink / "{time:YYYY-MM-DD}" / "common.log",
            level="INFO",
            retention=f"{log_rotate} days" if log_rotate else None,
            encoding="utf-8",
            rotation=time(),
        )
        logger.add(
            sink / "{time:YYYY-MM-DD}" / "error.log",
            level="ERROR",
            retention=f"{log_rotate} days" if log_rotate else None,
            encoding="utf-8",
            rotation=time(),
        )
    richuru.install()
