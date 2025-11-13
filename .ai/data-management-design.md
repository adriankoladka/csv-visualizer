# CsvVisualizer - Application Data Management Design

## 1. Overview

This document outlines the data management design for the CsvVisualizer application. The design is based on a session-based, non-persistent storage model, aligning with the project's MVP requirements. All user-uploaded data is stored temporarily on the server for the duration of an active session and is automatically purged upon session termination. This approach eliminates the need for a database, simplifying the architecture while ensuring user data privacy.

## 2. Directory Structure

A dedicated temporary directory will be used to store all uploaded files. To ensure data isolation between users, a unique subdirectory will be created for each user session.

-   **Main Upload Directory**: `instance/uploads/`
    -   This directory will be created within the Flask `instance` folder, which is designed for files not under version control.
    -   The web server (e.g., Nginx, Apache) should be configured to deny direct HTTP access to this path.
-   **Session-Specific Directory**: `instance/uploads/<session_id>/`
    -   `<session_id>` will be a unique and securely generated identifier (e.g., using `uuid.uuid4().hex`).
    -   This unique directory is created when a user uploads their first file.
    -   All subsequent files for that session are stored here.

Example: `instance/uploads/b3a1c2d9f0e84a5ab7c6d5e4f3g2h1i0/my_data.csv`

## 3. Session Data Structure

Flask's secure session object (`flask.session`) will be the single source of truth for managing user file metadata. This avoids database dependency and keeps the state tied to the user's session.

The session will store:
1.  `session_dir_id`: The unique identifier (`<session_id>`) for the user's temporary directory.
2.  `files`: A list of dictionaries, where each dictionary represents an uploaded file.

```python
# Example structure of flask.session
{
    'user_id': 123,
    'session_dir_id': 'b3a1c2d9f0e84a5ab7c6d5e4f3g2h1i0',
    'files': [
        {
            'id': 'file_1', # A unique identifier for the file within the session
            'original_filename': 'sales_data_q1.csv',
            'server_path': 'instance/uploads/b3a1c2d9f0e84a5ab7c6d5e4f3g2h1i0/sales_data_q1.csv'
        },
        {
            'id': 'file_2',
            'original_filename': 'customer_feedback.csv',
            'server_path': 'instance/uploads/b3a1c2d9f0e84a5ab7c6d5e4f3g2h1i0/customer_feedback.csv'
        }
    ]
}
```

A limit of **5 files per session uploaded sequentially** will be enforced at the application level to prevent resource exhaustion.

## 4. Core Components

### Data Management Routes

All data management logic will be handled by view functions within the `main` blueprint, to ensure modularity. These view functions will be responsible for handling form submissions for file uploads, deletions, and updates.

### Helper Functions

A set of utility functions will be created to manage file and directory operations cleanly.

-   `get_session_dir() -> Path`: Retrieves the path to the user's session directory. Creates it if it doesn't exist.
-   `clear_session_dir()`: Deletes the user's session directory and all its contents. This will be called on logout.
-   `is_valid_csv(file_stream) -> bool`: Checks if the uploaded file is a valid CSV with UTF-8 encoding and headers in the first row. It will use `pandas.read_csv()` within a `try-except` block to perform validation.

## 5. Workflow and Routes

### 5.1. File Upload

-   **Route**: A `POST` request to a route like `/upload`. This will be handled by a view function.
-   **Workflow**:
    1.  The user submits a file via an HTML form on the dashboard.
    2.  The application checks if the session file limit (5) has been reached. If so, flash an error message.
    3.  The file is read into memory to validate its format (CSV, UTF-8 encoding) using the `is_valid_csv` helper. An error is flashed if validation fails. The validation process must confirm that the file has a header row. An upload will be rejected if the file lacks a proper header.
    4.  The user-provided filename is sanitized using `werkzeug.utils.secure_filename()`.
    5.  The `get_session_dir()` helper is called to get/create the unique session directory.
    6.  The file is saved to the session directory.
    7.  A new file entry (dictionary) is added to the `session['files']` list.
    8.  The user is redirected back to the dashboard, where the page will reload to show the new file in the list.

### 5.2. File Deletion

-   **Route**: A `POST` request to a route like `/delete_file/<file_id>`.
-   **Workflow**:
    1.  The user clicks a "Delete" button within a form, triggering a `POST` request to this endpoint with the unique `file_id`.
    2.  The application finds the file's metadata in `session['files']` using the `file_id`.
    3.  The physical file is deleted from the server using `os.remove()`.
    4.  The corresponding entry is removed from the `session['files']` list.
    5.  A confirmation message is flashed to the user, and they are redirected back to the dashboard.

### 5.3. File Update

-   **Route**: A `POST` request to a route like `/update_file/<file_id>`.
-   **Workflow**:
    1.  The user clicks an "Update" button, which triggers a form submission with the new file to this endpoint.
    2.  The new file is validated just like in the upload process.
    3.  The application finds the old file's metadata in `session['files']`.
    4.  The old physical file is deleted from the server.
    5.  The new file is saved to the session directory (potentially with a new sanitized name).
    6.  The entry in `session['files']` is updated with the new `original_filename` and `server_path`.
    7.  A confirmation message is flashed, and the user is redirected back to the dashboard.

### 5.4. File List Display

-   There is no dedicated route for this. The list of files will be retrieved directly from `session.get('files', [])` within the main dashboard view function.
-   The `dashboard.html` template will iterate through this list to display the files, along with "Delete" and "Update" buttons for each.

## 6. Session Management and Data Cleanup

-   **Session Initialization**: The session directory is created lazily upon the first file upload, not on login. This prevents the creation of empty directories for users who don't upload anything.
-   **Session Teardown (Logout)**: When a user logs out, the following actions must be performed before the standard Flask-Login logout procedure:
    1.  Check if `session_dir_id` exists in the session.
    2.  If it exists, construct the path to the session directory.
    3.  Call a cleanup function (`clear_session_dir()`) that uses `shutil.rmtree()` to recursively and permanently delete the entire session directory and its contents.
    4.  Clear the `session['files']` and `session['session_dir_id']` keys.

This ensures that all user data is purged immediately upon logout, fulfilling requirement US-009.

## 7. Security Considerations

-   **Filename Sanitization**: All filenames from users will be processed with `werkzeug.utils.secure_filename()` to prevent directory traversal attacks (e.g., `../../etc/passwd`).
-   **Direct Access Prevention**: The `instance/uploads` directory will be configured at the web server level (e.g., via Nginx `location` block or Apache `.htaccess`) to block all direct HTTP requests, ensuring files can only be accessed through the application logic.
-   **Resource Limits**: The 5-file limit per session and 1MB file size limit protect against simple resource exhaustion attacks.
