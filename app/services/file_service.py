"""
Contains the business logic for file management.
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from flask import current_app, session
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

MAX_FILES_PER_SESSION = 5
MAX_FILE_SIZE_MB = 1


def get_session_dir() -> Path:
    """
    Retrieves the path to the user's session directory, creating it if it
    doesn't exist.

    Returns:
        Path: The path to the session directory.
    """
    if "session_dir_id" not in session:
        session["session_dir_id"] = uuid.uuid4().hex

    session_dir_id = session["session_dir_id"]
    # The `uploads` directory is created within the instance folder
    session_dir = (
        Path(current_app.instance_path) / "uploads" / str(session_dir_id)
    )
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def clear_session_dir() -> None:
    """
    Deletes the user's session directory and all its contents.
    """
    if "session_dir_id" in session:
        session_dir_id = session["session_dir_id"]
        session_dir = (
            Path(current_app.instance_path) / "uploads" / str(session_dir_id)
        )
        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir)

    session.pop("session_dir_id", None)
    session.pop("files", None)


def is_valid_csv(file_stream: Any) -> bool:
    """
    Checks if the uploaded file is a valid CSV with UTF-8 encoding and
    headers.

    Args:
        file_stream: The file stream to validate.

    Returns:
        bool: True if the file is a valid CSV, False otherwise.
    """
    try:
        # The first line is read to check for headers
        pd.read_csv(file_stream, nrows=1)
        file_stream.seek(0)  # Reset stream for subsequent reads
        return True
    except (pd.errors.ParserError, UnicodeDecodeError, Exception):
        return False


def add_file_to_session(
    file: FileStorage,
) -> Optional[Dict[str, Any]]:
    """
    Saves an uploaded file to the session directory and adds its metadata to
    the session.

    Args:
        file (FileStorage): The file to add.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the file's metadata
                                  if successful, otherwise None.
    """
    if "files" not in session:
        session["files"] = []

    if len(session["files"]) >= MAX_FILES_PER_SESSION:
        return None

    filename = secure_filename(file.filename or f"file_{uuid.uuid4().hex}.csv")
    session_dir = get_session_dir()
    file_path = session_dir / filename
    file.save(file_path)

    file_id = f"file_{uuid.uuid4().hex}"
    file_metadata = {
        "id": file_id,
        "original_filename": filename,
        "server_path": str(file_path),
    }

    session["files"].append(file_metadata)
    session.modified = True
    return file_metadata


def remove_file_from_session(file_id: str) -> bool:
    """
    Removes a file from the session directory and its metadata from the
    session.

    Args:
        file_id (str): The ID of the file to remove.

    Returns:
        bool: True if the file was removed successfully, False otherwise.
    """
    if "files" not in session:
        return False

    file_to_remove = next(
        (f for f in session["files"] if f["id"] == file_id), None
    )

    if not file_to_remove:
        return False

    try:
        os.remove(file_to_remove["server_path"])
    except OSError:
        # The file may not exist, but we should still remove it from the
        # session
        pass

    session["files"] = [f for f in session["files"] if f["id"] != file_id]
    session.modified = True
    return True


def get_csv_headers(file_path: str) -> List[str]:
    """
    Reads the header row from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List[str]: A list of column headers.
    """
    try:
        return pd.read_csv(file_path, nrows=0).columns.tolist()
    except Exception:
        return []
