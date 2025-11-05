# API Endpoint Implementation Plan: POST /api/v1/files

## 1. Endpoint Overview
This endpoint allows authenticated users to upload a CSV file. It validates the file against several criteria, saves it to a temporary session-specific directory on the server, and records its metadata in the user's session. Upon success, it returns details about the file, including a unique ID and its column headers.

## 2. Request Details
- **HTTP Method**: `POST`
- **URL Structure**: `/api/v1/files`
- **Headers**:
  - `Content-Type`: `multipart/form-data`
- **Request Body**: The body must be a `multipart/form-data` payload containing a single part.
  - **Required**: `file` - The CSV file being uploaded.

## 3. Used Types
- `werkzeug.datastructures.FileStorage`: Represents the in-memory file object received from the request.
- `pathlib.Path`: For handling file system paths to the session and upload directories.
- `List[str]`: For the list of column names extracted from the CSV file.
- `Dict[str, Any]`: For building the JSON response payload.
- `uuid.UUID`: To generate a unique identifier for the file.

## 4. Data Flow
1.  The user sends a `POST` request with the CSV file to `/api/v1/files`.
2.  The Flask route handler receives the request. The `@login_required` decorator ensures the user is authenticated.
3.  The route handler extracts the `FileStorage` object from `request.files`.
4.  The file object is passed to a `FileService`.
5.  The `FileService` performs the following validation checks in order:
    a. Verifies that the session file count is less than 5.
    b. Checks if the file size is within the 1MB limit.
    c. Validates that the file is a properly formatted CSV with a header row using `pandas`.
6.  If validation succeeds, the `FileService` gets/creates the unique session directory (`instance/uploads/<session_dir_id>/`).
7.  The service sanitizes the original filename using `werkzeug.utils.secure_filename()`.
8.  The file is saved to the session directory.
9.  A unique `file_id` is generated using `uuid.uuid4().hex`.
10. The `FileService` updates the `flask.session` object, adding a new dictionary to the `files` list containing the `file_id`, `original_filename`, and the `server_path`.
11. The route handler receives the processed data (file ID, original name, columns) from the service.
12. A `201 Created` JSON response is constructed and sent back to the client.

## 5. Security Considerations
- **Authentication**: The endpoint must be protected by the `@login_required` decorator to prevent access by unauthenticated users.
- **Authorization**: Any user who is authenticated is authorized to use this endpoint.
- **Input Validation**:
    - **Filename Sanitization**: All user-provided filenames must be processed with `werkzeug.utils.secure_filename()` to prevent directory traversal attacks.
    - **File Content**: The file's content must be validated as a legitimate CSV to prevent the processing of malicious or malformed files.
- **Resource Management**: Strict limits on file size (1MB) and the number of files per session (5) must be enforced to prevent resource exhaustion attacks.

## 6. Error Handling
The API will return specific error codes and messages for different failure scenarios:
- **400 Bad Request**:
  - If the `file` part is missing from the request.
  - If the uploaded file is not a valid CSV or is missing the header row.
- **401 Unauthorized**:
  - If the request is made without a valid session cookie (handled by `@login_required`).
- **413 Payload Too Large**:
  - If the file size exceeds the 1MB limit.
- **429 Too Many Requests**:
  - If the user attempts to upload a file when the session limit of 5 files has already been reached.

## 7. Performance
- **File Size Limit**: The 1MB file size limit ensures that file I/O and processing with pandas remain fast and do not consume excessive memory or CPU time.

## 8. Implementation Steps
1.  **Create Blueprint**: If not already present, create a new Flask Blueprint for the API (e.g., `api_bp` at `csvviz/api/__init__.py`).
2.  **Create Service Layer**:
    -   Create a new file `csvviz/services/file_service.py`.
    -   Implement a `FileService` class to contain the core business logic.
    -   Add a method `upload_file(file: FileStorage)` to the service. This method will orchestrate validation, saving, and session updates.
    -   Implement helper methods within the service for validation (`_is_valid_csv`, `_is_size_valid`).
3.  **Implement Route Handler**:
    -   Create a new file `csvviz/api/routes.py`.
    -   Add the `POST /api/v1/files` route to this file under the `api_bp` blueprint.
    -   Decorate the route with `@login_required`.
    -   Implement the route function, which will call the `FileService.upload_file()` method.
4.  **Handle Request and Response**:
    -   In the route, extract the file from `request.files`.
    -   Wrap the call to the service in a `try...except` block to catch custom exceptions (e.g., `ValidationError`, `FileLimitExceededError`) raised by the service.
    -   Based on the service's return value or the exception caught, construct the appropriate JSON response (201 on success, 4xx on error).
5.  **Update Session Management**:
    -   Ensure the `FileService` correctly interacts with `flask.session` to retrieve the file list and add new file metadata upon successful upload.
    -   Ensure the `session_dir_id` is created and stored as per the data management design.
6.  **Register Blueprint**: Register the `api_bp` blueprint with the Flask application factory in `csvviz/__init__.py`.
