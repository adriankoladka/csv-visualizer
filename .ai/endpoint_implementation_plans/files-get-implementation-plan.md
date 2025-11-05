# API Endpoint Implementation Plan: GET /api/v1/files

## 1. Endpoint Overview
This endpoint provides a secure way for an authenticated user to retrieve a list of all CSV files they have uploaded during their current session. The response includes essential metadata for each file, such as its unique identifier, original name, and a list of its column headers, which is crucial for frontend rendering of data visualization options.

## 2. Request Details
-   **HTTP Method**: `GET`
-   **URL Structure**: `/api/v1/files`
-   **Parameters**:
    -   Required: None.
    -   Optional: None.
-   **Request Body**: None.

## 3. Used Types
The implementation will use the following Python types to ensure data consistency.

```python
from typing import List, Dict, TypedDict

class FileDetails(TypedDict):
    """Represents the details of a single uploaded file."""
    id: str
    original_filename: str
    columns: List[str]

class FilesResponse(TypedDict):
    """Represents the API response payload."""
    files: List[FileDetails]
```

## 4. Response Details
-   **Success Response (200 OK)**:
    -   Description: Returned when the request is successful. The `files` array may be empty if the user has not uploaded any files.
    -   Payload:
        ```json
        {
          "files": [
            {
              "id": "file_1",
              "original_filename": "sales_data.csv",
              "columns": ["Date", "Region", "SalesAmount"]
            },
            {
              "id": "file_2",
              "original_filename": "inventory.csv",
              "columns": ["ProductID", "StockLevel", "Warehouse"]
            }
          ]
        }
        ```
-   **Error Response (401 Unauthorized)**:
    -   Description: Returned if the request is made by a user who is not logged in.
    -   Payload:
        ```json
        {
          "error": "Unauthorized"
        }
        ```

## 5. Data Flow
1.  A `GET` request is sent to `/api/v1/files`.
2.  The `api` blueprint receives the request.
3.  The `@login_required` decorator verifies the user's session. If the user is not authenticated, the request is rejected with a `401` status.
4.  The route handler calls the `FileService.get_files_for_session()` method.
5.  The `FileService` retrieves the list of file metadata from `session.get('files', [])`.
6.  For each file in the list, the service:
    a. Verifies the existence of the file at the `server_path`.
    b. Reads the first row of the CSV file using `pandas.read_csv(..., nrows=0).columns.tolist()` to efficiently get the column headers.
    c. Handles any `FileNotFoundError` or `pandas` parsing errors by logging them and skipping the problematic file.
7.  The service compiles a list of `FileDetails` dictionaries for all valid files.
8.  The route handler receives the list from the service, formats it into the final `FilesResponse` structure, and returns it as a JSON response with a `200 OK` status.

## 6. Security Considerations
-   **Authentication**: Access is strictly limited to authenticated users via the `Flask-Login` `@login_required` decorator.
-   **Authorization**: The endpoint inherently enforces authorization by only accessing data from the user's own session object, preventing data leakage between users.
-   **Data Validation**: The `FileService` will validate that file paths from the session are legitimate and that the files are readable before processing, preventing crashes due to corrupted session data or missing files.

## 7. Error Handling
-   **Unauthenticated Access**: A `401 Unauthorized` response will be returned.
-   **File Not Found**: If a file path from the session does not exist on the filesystem, the error will be logged, and the file will be omitted from the response. The API will still return `200 OK`.
-   **Corrupted File**: If a CSV file cannot be parsed by `pandas`, the error will be logged, and the file will be omitted from the response. The API will still return `200 OK`.
-   **Internal Server Errors**: Any other unexpected exceptions will be caught, logged, and a `500 Internal Server Error` response will be returned with a generic error message.

## 8. Performance Considerations
-   **Efficient Column Extraction**: To get the column headers, the implementation will use `pandas.read_csv(nrows=0)`. This reads only the header row without loading the entire file into memory, ensuring fast performance even for very large CSV files.
-   **Filesystem Access**: The primary performance bottleneck will be filesystem I/O. However, since only the first line of each file is read, the impact is minimal. The number of files is limited to 5 per session, which keeps the total I/O operations low.

## 9. Implementation Steps
1.  **Create API Blueprint**:
    -   Create a new file `app/api/routes.py`.
    -   Define a new `Blueprint` named `api_bp` with the URL prefix `/api/v1`.
    -   Register this blueprint in the main application factory.
2.  **Create File Service**:
    -   Create a new file `app/services/file_service.py`.
    -   Implement a `FileService` class.
    -   Add a static method `get_files_for_session()` that contains the logic for retrieving file details and columns from `pandas`.
3.  **Implement the Endpoint**:
    -   In `app/api/routes.py`, define the route `@api_bp.route('/files', methods=['GET'])`.
    -   Protect the route with the `@login_required` decorator.
    -   Implement the route handler function, which calls `FileService.get_files_for_session()`.
    -   Format the returned data into a JSON response using `jsonify`.
