# API Endpoint Implementation Plan: POST /api/v1/users/logout

## 1. Endpoint Overview
This endpoint is responsible for securely logging out the currently authenticated user. Its primary function is to terminate the user's session and trigger a comprehensive cleanup of all temporary data associated with that session, including uploaded CSV files. This ensures that no user data persists on the server after logout, aligning with the application's stateless data management design.

## 2. Request Details
- **HTTP Method**: `POST`
- **URL Structure**: `/api/v1/users/logout`
- **Parameters**:
  - **Required**: None.
  - **Optional**: None.
- **Request Body**: The request body is expected to be empty. Authentication is verified via the session cookie managed by Flask-Login.

## 3. Used Types
- `flask.Response`: To construct the final JSON response object.
- `flask.session`: The session proxy to access and clear session-specific data like `session_dir_id`.
- `flask.jsonify`: A helper function to create a JSON response.
- `pathlib.Path`: To build robust and OS-agnostic paths to the user's temporary data directory.
- `werkzeug.wrappers.Response`: The underlying response class used by Flask.

## 4. Data Flow
1. A `POST` request is sent to `/api/v1/users/logout` from a client with a valid session cookie.
2. The `@login_required` decorator intercepts the request to ensure a user is authenticated. If not, it aborts with a `401 Unauthorized` error.
3. The endpoint retrieves the `session_dir_id` from the `flask.session` object.
4. If a `session_dir_id` exists, a helper function (`clear_session_dir`) is called with this ID.
5. The helper function constructs the full path to the session directory (e.g., `instance/uploads/<session_dir_id>`).
6. The helper function uses `shutil.rmtree()` to recursively and permanently delete the entire session directory and its contents from the server's file system.
7. The `flask_login.logout_user()` function is called to invalidate the user's session and clear the session cookie.
8. The endpoint returns a `200 OK` response with a JSON payload confirming successful logout.

## 5. Security Considerations
- **Authentication**: The endpoint must be protected with the `@login_required` decorator from Flask-Login to ensure only authenticated users can access it.
- **Authorization**: No special roles are required; any authenticated user can log themselves out.
- **Data Cleanup**: The file cleanup logic must ensure it only deletes files within the designated `instance/uploads` directory. The use of `session_dir_id` prevents any possibility of path traversal, as the user has no control over this value.

## 6. Error Handling
- **No Active Session**:
  - **Trigger**: A request is made without a valid session cookie.
  - **Response**: The `@login_required` decorator will automatically respond with a `401 Unauthorized` status. The response body should be `{"message": "No active session to log out from."}`.
- **Cleanup Failure**:
  - **Trigger**: An `OSError` (e.g., permission denied) occurs while deleting the session directory.
  - **Action**: The error should be logged. The `logout_user()` function should still be called to ensure the user is logged out.
  - **Response**: A `500 Internal Server Error` with the body `{"message": "Logout successful, but a server error occurred during data cleanup."}`.
- **Directory Not Found**:
  - **Trigger**: The `session_dir_id` is in the session, but the corresponding directory is not on the disk.
  - **Action**: The cleanup function should handle this gracefully (e.g., with a `try...except FileNotFoundError` or `path.exists()` check) and not raise an error. The logout proceeds normally.
  - **Response**: `200 OK`.

## 7. Performance Considerations
- **I/O Operations**: The primary performance consideration is the file system I/O for deleting the session directory. Since the number of files per session is capped at 5 and the size is limited to 1MB each, the deletion process (`shutil.rmtree`) is expected to be very fast and should not introduce any noticeable delay.

## 8. Implementation Steps
1. **Create Helper Function**: In a new `csvviz/utils/file_helpers.py` module, create a function `clear_session_dir() -> None`.
   - This function will take no arguments.
   - It will check for `'session_dir_id'` in `flask.session`.
   - If found, it will construct the path using `current_app.config['UPLOAD_FOLDER']` and the session ID.
   - It will use `shutil.rmtree()` to delete the directory, wrapped in a `try...except` block to handle `FileNotFoundError` gracefully and log other `OSError` exceptions.
2. **Create API Blueprint**: If it doesn't exist, create a new blueprint for user-related API endpoints in `csvviz/api/users.py`.
3. **Implement Logout Route**: Within the `users.py` blueprint, create the `logout` function for the `POST /api/v1/users/logout` route.
4. **Apply Decorators**: Protect the route with `@login_required` and a CSRF protection decorator (e.g., `@csrf.exempt` if handled globally, or a specific one if not).
5. **Implement Route Logic**:
   - Call the `clear_session_dir()` helper function.
   - Call `flask_login.logout_user()` to terminate the session.
   - Return a `200 OK` response using `jsonify({"message": "You have been successfully logged out."})`.
6. **Register Blueprint**: Register the new users API blueprint with the Flask application factory in `csvviz/__init__.py`.
