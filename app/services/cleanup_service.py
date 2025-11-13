"""
Handles cleanup of orphaned session directories and charts.
"""

import os
import time
from pathlib import Path

from flask import current_app


def cleanup_expired_sessions(max_age_hours: int = 24) -> None:
    """
    Removes session directories and charts that are older than the specified
    age.

    Args:
        max_age_hours (int): Maximum age in hours before a session is
                             considered expired. Default is 24 hours.
    """
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()

    # Clean up expired upload directories
    uploads_dir = Path(current_app.instance_path) / "uploads"
    if uploads_dir.exists():
        for session_dir in uploads_dir.iterdir():
            if session_dir.is_dir():
                dir_age = current_time - session_dir.stat().st_mtime
                if dir_age > max_age_seconds:
                    try:
                        import shutil

                        shutil.rmtree(session_dir)
                    except OSError:
                        pass

    # Clean up expired charts
    charts_dir = Path(current_app.instance_path) / "charts"
    if charts_dir.exists():
        for chart_file in charts_dir.iterdir():
            if chart_file.is_file():
                file_age = current_time - chart_file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        os.remove(chart_file)
                    except OSError:
                        pass
