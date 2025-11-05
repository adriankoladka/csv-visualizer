# API Endpoint Implementation Plan: User Endpoints

This document outlines the implementation plan for user-related endpoints, including authentication and session management.

---

## 1. POST /api/v1/users/login

### 1.1. Endpoint Overview
This endpoint authenticates a user by validating their `username` and `password`. On successful validation, it initiates a user session using Flask-Login, allowing the user to access protected parts of the application. The endpoint is designed to be the primary entry point for user authentication.

### 1.2. Request Details
- **HTTP Method:** `POST`
- **URL Structure:** `/api/v1/users/login`
- **Request Body:** The request body must be a JSON object with the following structure:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

### 1.3. Response Details
- **Success Response:**
  - **Status Code:** `200 OK`
  - **Body:**
    ```json
    {
      "message": "Login successful."
    }
    ```
- **Error Responses:**
  - **Status Code:** `400 Bad Request` (for missing or invalid fields)
  - **Status Code:** `401 Unauthorized` (for incorrect credentials)
  - **Status Code:** `500 Internal Server Error` (for unexpected server issues)

### 1.4. Data Flow
1. The client sends a `POST` request with the user's credentials in the JSON body.
2. The API endpoint receives the request and validates the presence and format of the `username` and `password` fields.
3. The endpoint calls an `AuthService` to perform the core authentication logic.
4. The `AuthService` retrieves the user data from a user store (e.g., a dictionary or database).
5. It securely compares the provided password with the stored password hash.
6. If authentication is successful, the service returns the `User` object.
7. The endpoint uses `flask_login.login_user(user)` to create a secure session.
8. A `200 OK` response is sent to the client. If authentication fails, an appropriate error response is returned.

### 1.5. Implementation Steps
1. **Create Blueprint:** Create a new Flask Blueprint named `auth_bp` under a new `csvviz/auth` module.
2. **Define User Model:** Implement a `User` class compatible with Flask-Login.
3. **Create AuthService:** Create an `auth_service.py` with a method `authenticate_user(username, password)`.
4. **Implement Route:** Add the `/api/v1/users/login` route to the `auth_bp` blueprint.
5. **Add Input Validation:** Validate the incoming JSON payload.
6. **Integrate AuthService:** Call the `AuthService` to authenticate the user.
7. **Handle Login:** If successful, call `flask_login.login_user()`.
8. **Return Responses:** Return the appropriate JSON response and status code.
9. **Add Error Handling:** Wrap logic in a `try...except` block for `500` errors.
10. **Register Blueprint:** Register the `auth_bp` with the main Flask application factory.

---

## 2. POST /api/v1/users/logout

### 2.1. Endpoint Overview
This endpoint securely logs out the currently authenticated user. It terminates the user's session and triggers a cleanup of all temporary data associated with that session.

### 2.2. Request Details
- **HTTP Method**: `POST`
- **URL Structure**: `/api/v1/users/logout`
- **Request Body**: Empty.

### 2.3. Response Details
- **Success Response (200 OK):**
  ```json
  {
    "message": "You have been successfully logged out."
  }
  ```
- **Error Responses:**
  - `401 Unauthorized`: No active session.
  - `500 Internal Server Error`: Logout successful, but data cleanup failed.

### 2.4. Data Flow
1. A `POST` request is sent to `/api/v1/users/logout`.
2. The `@login_required` decorator ensures a user is authenticated.
3. The endpoint retrieves the `session_dir_id` from `flask.session`.
4. A helper function (`clear_session_dir`) is called to delete the session directory.
5. `flask_login.logout_user()` is called to invalidate the session.
6. A `200 OK` response is returned.

### 2.5. Implementation Steps
1. **Create Helper Function**: In `csvviz/utils/file_helpers.py`, create `clear_session_dir()` to delete the session directory.
2. **Implement Logout Route**: In the `auth_bp` blueprint, create the `logout` function for `POST /api/v1/users/logout`.
3. **Apply Decorators**: Protect the route with `@login_required`.
4. **Implement Route Logic**: Call `clear_session_dir()` and `flask_login.logout_user()`.
5. **Return Response**: Return a `200 OK` JSON response.

---

## 3. Shared Components

### 3.1. Used Types
- **LoginRequestDTO:** A `TypedDict` to validate the login request body.
  ```python
  from typing import TypedDict

  class LoginRequestDTO(TypedDict):
      username: str
      password: str
  ```
- **User Model:** A `UserMixin` compatible class for user representation.
  ```python
  from flask_login import UserMixin
  from werkzeug.security import check_password_hash, generate_password_hash

  class User(UserMixin):
      def __init__(self, id, username, password):
          self.id = id
          self.username = username
          self.password_hash = generate_password_hash(password)

      def check_password(self, password: str) -> bool:
          return check_password_hash(self.password_hash, password)
  ```
- **Flask/Werkzeug Types**: `flask.Response`, `flask.session`, `flask.jsonify`, `pathlib.Path`.

### 3.2. Security Considerations
- **Authentication:** All endpoints must be protected with `@login_required` from Flask-Login, except for the login endpoint itself.
- **Password Hashing:** Passwords must be stored as hashes. Comparisons must use `check_password_hash` to prevent timing attacks.
- **Data Cleanup:** The logout cleanup logic must only delete files within the designated `instance/uploads` directory to prevent path traversal vulnerabilities.

### 3.3. Performance Considerations
- The user lookup process should be optimized.
- Password hashing is computationally intensive by design and is the primary factor in login response time.
- I/O operations for data cleanup on logout are expected to be fast due to file size and count limits.
