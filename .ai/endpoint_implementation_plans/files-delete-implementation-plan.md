# API Endpoint Implementation Plan: DELETE /api/v1/files/{file_id}

## 1. Endpoint Overview
This endpoint is responsible for deleting a single CSV file from the current user's session. It removes the physical file from the server's temporary storage and updates the session data to reflect the deletion. Access is restricted to authenticated users.

## 2. Request Details
-   **HTTP Method**: `DELETE`
-   **URL Structure**: `/api/v1/files/{file_id}`
-   **Parameters**:
    -   **Required**:
        -   `file_id` (Path Parameter, `string`): The unique identifier of the file to be deleted.
    -   **Optional**: None.
-   **Request Body**: None.

## 3. Used Types
-   `flask.session`: For accessing and modifying the list of files stored in the user's session.
-   `os`: For using `os.remove()` to delete the physical file from the filesystem.
-   `Dict[str, Any]`: For building the JSON response payload.

## 4. Response Details
-   **Success Response (`200 OK`)**:
    -   Indicates the file was successfully deleted.
    -   **JSON Payload**:
        ```json
        {
          "message": "File deleted successfully."
        }
        ```
-   **Error Responses**:
    -   `401 Unauthorized`: The user is not authenticated.
    -   `404 Not Found`: No file matching the provided `file_id` was found in the user's session.
    -   `500 Internal Server Error`: An unexpected server-side error occurred (e.g., filesystem permission error).

## 5. Data Flow
1.  A `DELETE` request is sent to `/api/v1/files/{file_id}`.
2.  The `Flask-Login` `@login_required` decorator verifies that the user is authenticated. If not, it aborts with a `401` status.
3.  The view function retrieves the `file_id` from the URL path.
4.  The view function calls the `FileService.delete_file` method, passing the `file_id` and the current `session`.
5.  The `FileService` searches the `session.get('files', [])` list for a dictionary with a matching `id`.
6.  If no match is found, the service raises a `FileNotFoundError`.
7.  If a match is found, the service retrieves the `server_path` from the file's metadata.
8.  The service attempts to delete the physical file from the filesystem using `os.remove()`. If the file doesn't exist, it logs a warning but continues.
9.  The service removes the file's metadata dictionary from the `session['files']` list.
10. The view function catches any exceptions from the service and returns the appropriate JSON error response (`404` or `500`).
11. If the service completes successfully, the view function returns a `200 OK` response with a success message.

## 6. Security Considerations
-   **Authentication**: The endpoint will be protected using the `@login_required` decorator from `Flask-Login` to ensure only authenticated users can access it.
-   **Authorization**: The operation is inherently authorized correctly because the file lookup is scoped to the list of files stored within the user's own session object. There is no risk of a user deleting another user's files.
-   **Data Validation**: The `file_id` is validated for existence within the session's file list. The actual file path is never constructed from user input, preventing path traversal attacks.

## 7. Performance Considerations
-   The performance impact of this operation is minimal and directly related to the number of files in a user's session (maximum of 5).
-   The file list search is a linear scan (`O(n)`) over a very small list.
-   The primary latency will come from the filesystem I/O for the delete operation, which is expected to be negligible for the allowed file sizes. No performance optimizations are required.

## 8. Implementation Steps
1.  **Create API Blueprint**:
    -   In `csvviz/api/__init__.py`, create a new Flask `Blueprint` named `api_bp` with the URL prefix `/api/v1`.

2.  **Create File Service**:
    -   Create a new file `csvviz/services/file_service.py`.
    -   Implement a `FileService` class with a static method `delete_file(file_id: str, session: session) -> None`.
    -   This method will contain the logic to find the file metadata, delete the physical file, and update the session. It should raise a `FileNotFoundError` if the `file_id` is not found and handle cases where the physical file might already be gone.

3.  **Implement the Endpoint**:
    -   Create a new file `csvviz/api/routes.py`.
    -   Add the route `DELETE /files/<file_id>` to the `api_bp` blueprint.
    -   Decorate the view function with `@login_required`.
    -   Implement the view function, which will call `FileService.delete_file`.
    -   Add `try...except` blocks to handle `FileNotFoundError` (returning a 404) and any other exceptions (returning a 500).

4.  **Register Blueprint**:
    -   In the application factory (`csvviz/__init__.py`), import and register the `api_bp` blueprint with the Flask app instance.
