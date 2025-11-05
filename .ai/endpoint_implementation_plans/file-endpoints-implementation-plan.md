# API Endpoint Implementation Plan: File Endpoints

This document outlines the implementation plan for file management endpoints, covering file uploads, retrieval, updates, and deletion.

---

## 1. POST /api/v1/files

### 1.1. Endpoint Overview
Allows authenticated users to upload a CSV file. The file is validated, saved to a session-specific directory, and its metadata is stored in the user's session.

### 1.2. Request Details
- **HTTP Method**: `POST`
- **URL Structure**: `/api/v1/files`
- **Headers**: `Content-Type: multipart/form-data`
- **Request Body**: `file` (the CSV file).

### 1.3. Response Details
- **Success (201 Created)**:
  ```json
  {
    "message": "File uploaded successfully.",
    "file": {
      "id": "string",
      "original_filename": "string",
      "columns": ["string"]
    }
  }
  ```
- **Errors**: `400`, `401`, `413`, `429`.

### 1.4. Data Flow
1. User sends a `POST` request with the CSV file.
2. The route handler, protected by `@login_required`, extracts the file.
3. A `FileService` validates the file (session limit < 5, size < 1MB, valid CSV with header).
4. If valid, the service saves the file to `instance/uploads/<session_dir_id>/`.
5. A unique `file_id` is generated, and metadata is added to `flask.session['files']`.
6. A `201 Created` response is returned with file details.

---

## 2. GET /api/v1/files

### 2.1. Endpoint Overview
Retrieves a list of all CSV files uploaded by the user during the current session, including metadata like column headers.

### 2.2. Request Details
- **HTTP Method**: `GET`
- **URL Structure**: `/api/v1/files`
- **Request Body**: None.

### 2.3. Response Details
- **Success (200 OK)**:
  ```json
  {
    "files": [
      {
        "id": "string",
        "original_filename": "string",
        "columns": ["string"]
      }
    ]
  }
  ```
- **Error**: `401 Unauthorized`.

### 2.4. Data Flow
1. User sends a `GET` request to `/api/v1/files`.
2. `@login_required` verifies the session.
3. `FileService.get_files_for_session()` is called.
4. The service retrieves file metadata from `session['files']`.
5. For each file, it reads the header row to get column names using `pandas.read_csv(nrows=0)`.
6. A list of file details is compiled and returned in a `200 OK` response.

---

## 3. PUT /api/v1/files/{file_id}

### 3.1. Endpoint Overview
Allows a user to replace an existing CSV file with a new one.

### 3.2. Request Details
- **HTTP Method**: `PUT`
- **URL Structure**: `/api/v1/files/{file_id}`
- **Request Type**: `multipart/form-data`
- **Parameters**: `file_id` (URL path), `file` (body).

### 3.3. Response Details
- **Success (200 OK)**:
  ```json
  {
    "message": "File updated successfully.",
    "file": {
      "id": "string",
      "original_filename": "string",
      "columns": ["string"]
    }
  }
  ```
- **Errors**: `400`, `401`, `404`, `413`.

### 3.4. Data Flow
1. User sends a `PUT` request with the new file.
2. `@login_required` verifies authentication.
3. `FileService.update_file` is called with `file_id` and the new file.
4. The service finds the file metadata in the session, deletes the old file, validates and saves the new one, and updates the session metadata.
5. A `200 OK` response is returned with the new file details.

---

## 4. DELETE /api/v1/files/{file_id}

### 4.1. Endpoint Overview
Deletes a single CSV file from the user's session and the server's storage.

### 4.2. Request Details
- **HTTP Method**: `DELETE`
- **URL Structure**: `/api/v1/files/{file_id}`
- **Request Body**: None.

### 4.3. Response Details
- **Success (200 OK)**:
  ```json
  {
    "message": "File deleted successfully."
  }
  ```
- **Errors**: `401`, `404`, `500`.

### 4.4. Data Flow
1. User sends a `DELETE` request.
2. `@login_required` verifies authentication.
3. `FileService.delete_file` is called with `file_id`.
4. The service finds the file metadata in the session, deletes the physical file, and removes the metadata from the session.
5. A `200 OK` response is returned.

---

## 5. Shared Components

### 5.1. Used Types
- `werkzeug.datastructures.FileStorage`: For the uploaded file object.
- `pathlib.Path`: For handling filesystem paths.
- `TypedDict`: For structuring request and response payloads.
  ```python
  from typing import List, Dict, TypedDict

  class FileDetails(TypedDict):
      id: str
      original_filename: str
      columns: List[str]
  ```

### 5.2. Security Considerations
- **Authentication**: All endpoints must be protected with `@login_required`.
- **Authorization**: Logic must be scoped to the user's session to prevent unauthorized access to other users' files.
- **Input Validation**:
    - **Filename Sanitization**: Use `werkzeug.utils.secure_filename()` to prevent directory traversal.
    - **File Content**: Validate files as legitimate CSVs to prevent processing of malicious files.
- **Resource Management**: Enforce file size (1MB) and count (5 per session) limits to prevent resource exhaustion.

### 5.3. Performance Considerations
- **Efficient Column Extraction**: Use `pandas.read_csv(nrows=0)` to read only the header row for column extraction, ensuring fast performance regardless of file size.
- **Filesystem I/O**: Given the small file size and count limits, filesystem operations are expected to have minimal performance impact.

### 5.4. Implementation Steps
1. **Create API Blueprint**: Define a new `Blueprint` named `api_bp` for `/api/v1`.
2. **Create File Service**: Implement a `FileService` class in `csvviz/services/file_service.py` to encapsulate all business logic (upload, update, delete, list).
3. **Implement Routes**: Add the routes to `csvviz/api/routes.py` under the `api_bp` blueprint, calling the appropriate `FileService` methods.
4. **Handle Errors**: Use `try...except` blocks in route handlers to catch service-layer exceptions and return appropriate HTTP error responses.
5. **Register Blueprint**: Register `api_bp` with the Flask application factory.
