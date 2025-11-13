"""
Handles logging of business events.
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import current_app


def setup_event_logger() -> None:
    """
    Configures the logger for business events.
    """
    log_dir = Path(current_app.instance_path)
    log_file = log_dir / "events.log"

    # Ensure the directory exists
    log_dir.mkdir(exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "event_type": "%(message)s"}'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("event_logger")
    if not logger.handlers:
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def log_event(event_type: str) -> None:
    """
    Logs a business event to the dedicated log file.

    Args:
        event_type (str): The type of event to log (e.g., 'chart_generated').
    """
    logger = logging.getLogger("event_logger")
    logger.info(event_type)
