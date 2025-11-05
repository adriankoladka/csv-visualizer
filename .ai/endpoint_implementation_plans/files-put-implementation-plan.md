# API Endpoint Implementation Plan: PUT /api/v1/files/{file_id}

## 1. Endpoint Overview

This document outlines the implementation plan for the `PUT /api/v1/files/{file_id}` endpoint. Its purpose is to allow an authenticated user to replace an existing CSV file with a new one. The operation involves validating the new file, replacing the old file on the server's temporary storage, updating the user's session data, and returning details about the newly uploaded file.

## 2. Request Details

-   **HTTP Method**: `PUT`
-   **URL Structure**: `/api/v1/files/{file_id}`
-   **Request Type**: `multipart/form-data`
-   **Parameters**:
    -   **Required**:
        -   `file_id` (string, URL path): The unique identifier of the file to be replaced.
        -   `file` (File, body): The new CSV file being uploaded.
-   **Headers**:
    -   `Content-Type: multipart/form-data`
    -   `X-CSRFToken` (if using Flask-WTF for CSRF protection).

## 3. Used Types

The implementation will use `TypedDict` for clear data structuring.

```python
from typing import TypedDict, List

class FileDetails(TypedDict):
    """Represents the structure of a file's details in the response."""
    id: str
    original_filename: str
    columns: List[str]

class UpdateFileResponse(TypedDict):
    """Represents the full JSON response for a successful update."""
    message: str
    file: FileDetails
```

## 4. Response Details

-   **Success (200 OK)**: Returned when the file is successfully replaced.
    ```json
    {
      "message": "File updated successfully.",
      "file": {
        "id": "file_2",
        "original_filename": "new_sales_data.csv",
        "columns": ["Date", "Region", "SalesAmount", "UnitsSold"]
      }
    }
    ```
-   **Error**: See the Error Handling section for details on `400`, `401`, `404`, and `413` status codes.

## 5. Data Flow

1.  A `PUT` request is sent to `/api/v1/files/{file_id}` with the new file.
2.  The `@login_required` decorator verifies user authentication.
3.  The view function retrieves the `file` object from `request.files`.
4.  The `FileService.update_file` method is called with the `file_id` and the new file object.
5.  **Inside `FileService.update_file`**:
    a.  It searches `session['files']` for the dictionary matching `file_id`. If not found, a `FileNotFoundError` is raised.
    b.  The physical path of the old file is retrieved from the session metadata.
    c.  The new file is validated using the `is_valid_csv` helper (checks for non-empty, valid CSV format with a header). If invalid, a `ValueError` is raised.
    d.  The old file is deleted from the filesystem (`os.remove`).
    e.  The new filename is sanitized using `werkzeug.utils.secure_filename`.
    f.  The new file is saved to the user's session directory (`instance/uploads/<session_dir_id>/`).
    g.  The file's metadata in `session['files']` is updated with the new `original_filename` and `server_path`.
    h.  The new CSV file is read using `pandas.read_csv(..., nrows=0)` to get the list of column headers.
    i.  A dictionary containing the updated file's `id`, `original_filename`, and `columns` is returned.
6.  The view function catches potential exceptions from the service and maps them to appropriate HTTP error responses.
7.  On success, the view function constructs the final JSON response and returns it with a `200 OK` status.

## 6. Security Considerations

-   **Authentication**: The endpoint must be protected with Flask-Login's `@login_required` decorator to prevent access by unauthenticated users.
-   **Authorization**: The logic must ensure that the `file_id` belongs to the current user by checking it against the data stored in `flask.session`. This prevents a user from modifying another user's files.
-   **Filename Sanitization**: All user-provided filenames must be sanitized with `werkzeug.utils.secure_filename()` before being used in a file path to prevent directory traversal attacks.
-   **Payload Size**: Flask's `MAX_CONTENT_LENGTH` configuration must be set (e.g., to 1MB) to prevent resource exhaustion attacks and automatically handle `413 Payload Too Large` errors.

## 7. Error Handling

The endpoint will handle the following error scenarios gracefully:

| Status Code | Reason | Condition |
| :--- | :--- | :--- |
| `400 Bad Request` | Invalid Input | - The `file` part is missing in the `multipart/form-data` request. <br> - The uploaded file is not a valid CSV, is empty, or lacks a header row. |
| `401 Unauthorized` | Authentication Required | The request is made without a valid session cookie (user is not logged in). |
| `404 Not Found` | File Not Found | The provided `file_id` does not exist in the user's session data. |
| `413 Payload Too Large` | File Too Large | The uploaded file's size exceeds the `MAX_CONTENT_LENGTH` limit set in the Flask application configuration. |
| `500 Internal Server Error` | Server-Side Failure | An unexpected error occurs, such as a filesystem permission error when trying to delete the old file or save the new one. |

## 8. Performance Considerations

-   **File Validation**: The `is_valid_csv` helper should read only the necessary parts of the file stream to validate it, not the entire file into memory, to conserve resources. Using `pandas.read_csv` within a `try-except` block is efficient for this.
-   **Column Extraction**: To get the column headers, the file should be read with `pandas.read_csv(..., nrows=0)`. This is highly efficient as it only reads the first line (the header) and avoids loading the entire dataset into memory.
-   **Filesystem I/O**: Filesystem operations are relatively fast for small files. The impact is expected to be minimal given the 1MB file size constraint.

## 9. Implementation Steps

1.  **Configure Flask**: Ensure `MAX_CONTENT_LENGTH` is set in the application's configuration file (`config.py`).
2.  **Define Types**: Create the `FileDetails` and `UpdateFileResponse` `TypedDict` types in a relevant module (e.g., `app/services/file_service.py` or a dedicated `app/types.py`).
3.  **Create Service Method**: In `app/services/file_service.py`, implement the `update_file` method. This method will contain the core logic described in the "Data Flow" section. It should raise specific, custom exceptions (e.g., `FileNotFoundError`, `InvalidFileError`) to be caught by the view.
4.  **Create API Blueprint**: If it doesn't exist, create a blueprint for the API (e.g., `api_bp`).
5.  **Implement View Function**:
    -   Create a new route `PUT /api/v1/files/{file_id}` within the API blueprint.
    -   Protect the route with `@login_required`.
    -   Add CSRF protection.
    -   Implement the request validation logic (check for `file` in `request.files`).
    -   Add a `try...except` block to call `FileService.update_file` and handle its specific exceptions, mapping them to the correct HTTP status codes (`404`, `400`).
    -   On success, format the data into the `UpdateFileResponse` structure and return it as JSON with a `200 OK` status.
