import logging
import os
import json
from pathlib import Path
from typing import Optional


class JsonFormatter(logging.Formatter):
    # Shared run_id across all logger instances
    _GLOBAL_RUN_ID: Optional[str] = None

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", self._GLOBAL_RUN_ID),
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def get_logger(
    name: str = "pipeline",
    log_dir: Path = Path("logs"),
    run_id: Optional[str] = None,
) -> logging.Logger:

    if run_id:
        JsonFormatter._GLOBAL_RUN_ID = run_id

    logger = logging.getLogger(name)

    # Already initialized — skip setup
    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "pipeline.json")
    file_handler.setFormatter(JsonFormatter())

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger