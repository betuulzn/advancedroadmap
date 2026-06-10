import logging
import os
import threading
from datetime import datetime
from typing import Optional

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def get_logger(name: str) -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(_formatter())

    # File handler — one file per run, shared across all loggers
    _shared_log_file = _get_shared_log_path()
    file_handler = logging.FileHandler(_shared_log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_formatter(detailed=True))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def _formatter(detailed: bool = False) -> logging.Formatter:
    if detailed:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
    else:
        fmt = "%(levelname)-8s | %(name)-20s | %(message)s"
        datefmt = "%H:%M:%S"
    return logging.Formatter(fmt, datefmt=datefmt)


# Single log file path shared across the entire pytest session
_SESSION_LOG_PATH: Optional[str] = None
_SESSION_LOG_LOCK = threading.Lock()


def _get_shared_log_path() -> str:
    global _SESSION_LOG_PATH
    with _SESSION_LOG_LOCK:
        if _SESSION_LOG_PATH is None:
            os.makedirs(LOG_DIR, exist_ok=True)
            _SESSION_LOG_PATH = os.path.join(
                LOG_DIR, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
    return _SESSION_LOG_PATH
