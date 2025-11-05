# API Endpoint Implementation Plan: GET /api/v1/charts/{chart_filename}

## 1. Endpoint Overview
This endpoint retrieves a generated chart image as a PNG file. It allows clients to either display the image directly or trigger a file download. Access is restricted to authenticated users, and charts are scoped to the user's current session, preventing unauthorized data access.

## 2. Request Details
-   **HTTP Method**: `GET`
-   **URL Structure**: `/api/v1/charts/<string:chart_filename>`
-   **Parameters**:
    -   **Path Parameter**:
        -   `chart_filename` (string): The name of the PNG chart file to be retrieved (e.g., `my_chart.png`).
    -   **Query Parameter**:
        -   `download` (boolean, optional): If set to `true`, the `Content-Disposition` header will be set to `attachment`, prompting the user to download the file. Defaults to `false`.

## 3. Used Types
-   `chart_filename`: `str`
-   `download`: `bool`

## 4. Response Details
-   **Success Response (`200 OK`)**:
    -   **Content-Type**: `image/png`
    -   **Content-Disposition**: `inline; filename="<chart_filename>"` (if `download` is `false` or absent) or `attachment; filename="<chart_filename>"` (if `download` is `true`).
    -   **Body**: The raw binary data of the PNG image.
-   **Error Responses**:
    -   `401 Unauthorized`: If the user is not authenticated.
    -   `404 Not Found`: If the specified `chart_filename` does not exist in the user's session directory.

## 5. Data Flow
1.  A `GET` request is made to `/api/v1/charts/{chart_filename}`.
2.  The Flask-Login `@login_required` decorator verifies the user's authentication status.
3.  The endpoint handler retrieves the `session_dir_id` from the Flask `session` object, which uniquely identifies the user's temporary data directory.
4.  A dedicated service/helper function, `get_chart_path`, is called with the `chart_filename`.
5.  This service constructs the full, secure path to the chart: `instance/charts/<session_dir_id>/<sanitized_chart_filename>`.
6.  The service checks if the file exists at the constructed path and that the path is within the allowed parent directory.
7.  If the file does not exist, a `404 Not Found` error is returned.
8.  If the file exists, the endpoint reads the `download` query parameter.
9.  The `flask.send_file` function is used to send the PNG file back to the client, setting the `as_attachment` argument based on the `download` parameter.

## 6. Security Considerations
-   **Authentication**: The endpoint must be protected with the `@login_required` decorator to ensure only logged-in users can access it.
-   **Authorization**: Data access is implicitly authorized by using the `session_dir_id` stored in the user's session. This ensures a user can only access charts generated during their own session.
-   **Directory Traversal**: The `chart_filename` parameter from the URL must not be trusted. It will be sanitized by combining it with the session-specific base path (`instance/charts/<session_dir_id>`) and ensuring the final resolved path is a child of this base path. Direct use of the input filename to construct a path is forbidden.

## 7. Performance Considerations
-   **File I/O**: The primary performance factor will be disk I/O for reading the chart file. As chart files are expected to be small (under 1MB), this should not be a significant bottleneck.
-   **`send_file` Efficiency**: Flask's `send_file` is efficient and can handle streaming the file, which is suitable for this use case. No further optimization is required for the MVP.

## 8. Implementation Steps
1.  **Create Blueprint**: If not already present, create a new Flask Blueprint for the API (e.g., `api_bp`) to house this endpoint.
2.  **Define Chart Directory**: Establish a convention for storing charts, parallel to the CSV uploads (e.g., in `instance/charts/`).
3.  **Develop Chart Service Logic**:
    -   Create a helper function or a service method `get_chart_path(chart_filename: str) -> Path | None`.
    -   This function will get the session directory ID from `flask.session`.
    -   It will construct the full path to the chart file.
    -   It will perform security checks: verify the file exists and is within the user's session-specific chart directory.
    -   It will return the `Path` object if valid, otherwise `None`.
4.  **Implement the Route**:
    -   Define the route `@api_bp.route('/v1/charts/<string:chart_filename>', methods=['GET'])`.
    -   Protect it with the `@login_required` decorator.
    -   Inside the route handler, call the `get_chart_path` function.
    -   If the path is `None`, return `abort(404)`.
5.  **Handle Query Parameter**:
    -   Read the `download` query parameter using `request.args.get('download', 'false').lower() == 'true'`.
6.  **Send the File**:
    -   Use `send_file(path, mimetype='image/png', as_attachment=is_download_request)` to send the response.
7.  **Add Logging**: Add a log entry when a chart is successfully downloaded (`download=true`).
