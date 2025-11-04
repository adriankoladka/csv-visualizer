# REST API Plan

This document outlines the REST API for the CsvVisualizer application, designed to support session-based data management, chart generation, and user authentication.

## 1. Resources

-   **Users**: Represents application users for authentication purposes.
-   **Files**: Represents user-uploaded CSV files within a session.
-   **Charts**: Represents the generated visualizations from CSV data.

## 2. Endpoints

### Users

#### **POST /api/v1/users/login**

-   **Description**: Authenticates a user and starts a session.
-   **JSON Request Payload**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
-   **JSON Response Payload**:
    ```json
    {
      "message": "string"
    }
    ```
-   **Success Codes**: `200 OK`
-   **Error Codes**: `401 Unauthorized` (Invalid credentials), `400 Bad Request` (Missing fields)

#### **POST /api/v1/users/logout**

-   **Description**: Logs out the current user, ends the session, and cleans up all associated temporary files.
-   **JSON Response Payload**:
    ```json
    {
      "message": "string"
    }
    ```
-   **Success Codes**: `200 OK`
-   **Error Codes**: `401 Unauthorized` (No active session)

### Files

#### **GET /api/v1/files**

-   **Description**: Retrieves a list of all CSV files uploaded by the user in the current session.
-   **JSON Response Payload**:
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
-   **Success Codes**: `200 OK`
-   **Error Codes**: `401 Unauthorized` (User not logged in)

#### **POST /api/v1/files**

-   **Description**: Uploads a new CSV file. The request must be `multipart/form-data`.
-   **Request Payload**: `file` (the CSV file being uploaded).
-   **JSON Response Payload**:
    ```json
    {
      "message": "string",
      "file": {
        "id": "string",
        "original_filename": "string",
        "columns": ["string"]
      }
    }
    ```
-   **Success Codes**: `201 Created`
-   **Error Codes**: `400 Bad Request` (Invalid file type, missing headers), `401 Unauthorized`, `413 Payload Too Large` (File exceeds 1MB), `429 Too Many Requests` (Session file limit of 5 reached).

#### **PUT /api/v1/files/{file_id}**

-   **Description**: Replaces an existing CSV file with a new one. The request must be `multipart/form-data`.
-   **Request Payload**: `file` (the new CSV file).
-   **JSON Response Payload**:
    ```json
    {
      "message": "string",
      "file": {
        "id": "string",
        "original_filename": "string",
        "columns": ["string"]
      }
    }
    ```
-   **Success Codes**: `200 OK`
-   **Error Codes**: `400 Bad Request` (Invalid file type), `401 Unauthorized`, `404 Not Found` (File ID does not exist), `413 Payload Too Large`.

#### **DELETE /api/v1/files/{file_id}**

-   **Description**: Deletes a specific CSV file from the user's session.
-   **JSON Response Payload**:
    ```json
    {
      "message": "string"
    }
    ```
-   **Success Codes**: `200 OK`
-   **Error Codes**: `401 Unauthorized`, `404 Not Found` (File ID does not exist).

### Charts

#### **POST /api/v1/charts**

-   **Description**: Generates a chart from a specified file and logs the `chart_generated` event.
-   **JSON Request Payload**:
    ```json
    {
      "file_id": "string",
      "x_axis": "string",
      "y_axis": "string",
      "chart_type": "string"
    }
    ```
-   **JSON Response Payload**:
    ```json
    {
      "chart_url": "string",
      "download_url": "string"
    }
    ```
-   **Success Codes**: `201 Created`
-   **Error Codes**: `400 Bad Request` (Invalid parameters), `401 Unauthorized`, `404 Not Found` (File ID does not exist), `500 Internal Server Error` (Chart generation failed).

#### **GET /api/v1/charts/{chart_filename}**

-   **Description**: Retrieves the generated chart image. If the `download` query parameter is set to `true`, it triggers a file download and logs the `chart_downloaded` event.
-   **Query Parameters**:
    -   `download` (boolean, optional): If `true`, sets `Content-Disposition` to `attachment`.
-   **Response**: The response body is the PNG image data.
-   **Success Codes**: `200 OK`
-   **Error Codes**: `401 Unauthorized`, `404 Not Found` (Chart file does not exist).

## 3. Authentication and Authorization

-   **Mechanism**: Session-based authentication managed by Flask-Login.
-   **Implementation**:
    1.  A user authenticates via the `POST /api/v1/users/login` endpoint.
    2.  Upon successful login, Flask-Login creates a secure, server-side session and sets a session cookie in the user's browser.
    3.  Subsequent requests to protected endpoints must include this session cookie. The `@login_required` decorator from Flask-Login will be used to protect these endpoints.
    4.  The `POST /api/v1/users/logout` endpoint will clear the session, effectively logging the user out.

## 4. Business Logic

-   **Temporary Data Management**: All file operations are tied to the user's session. The `data-management-design.md` is implemented through the `/api/v1/files` endpoints. A unique directory `instance/uploads/<session_id>` is created on the first file upload.
-   **Data Cleanup**: The `POST /api/v1/users/logout` endpoint is responsible for triggering the cleanup process. It will locate the session-specific directory and delete it entirely, ensuring no user data persists after logout.
-   **File Validation**: The `POST` and `PUT` endpoints for `/api/v1/files` will validate uploads against the PRD constraints (1MB size, CSV format, UTF-8 encoding, header in the first row) before saving the file.
-   **Metric Logging**:
    -   `chart_generated`: This event is logged within the `POST /api/v1/charts` endpoint logic after a chart is successfully created but before the response is sent.
    -   `chart_downloaded`: This event is logged within the `GET /api/v1/charts/{chart_filename}` endpoint logic, specifically when the `?download=true` query parameter is present and valid.
-   **Rate Limiting**: A file limit of 5 per session is enforced at the application level within the `POST /api/v1/files` endpoint.
