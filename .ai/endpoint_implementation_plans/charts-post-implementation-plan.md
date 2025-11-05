# API Endpoint Implementation Plan: POST /api/v1/charts

## 1. Endpoint Overview
This endpoint generates a static chart image based on data from a user-uploaded CSV file. It requires the user to specify the file, the columns for the x and y axes, and the chart type. On success, it returns URLs for accessing and downloading the generated chart.

## 2. Request Details
-   **HTTP Method**: `POST`
-   **URL Structure**: `/api/v1/charts`
-   **Parameters**: None in URL.
-   **Request Body**: A JSON object with the following structure:
    ```json
    {
      "file_id": "string",
      "x_axis": "string",
      "y_axis": "string",
      "chart_type": "string"
    }
    ```
    -   **Required**: `file_id`, `x_axis`, `y_axis`, `chart_type`.

## 3. Used Types
-   **ChartType**: `Literal['bar', 'line', 'scatter']`
-   **Request Payload (TypedDict)**:
    ```python
    class ChartData(TypedDict):
        file_id: str
        x_axis: str
        y_axis: str
        chart_type: ChartType
    ```
-   **Response Payload (TypedDict)**:
    ```python
    class ChartResponse(TypedDict):
        chart_url: str
        download_url: str
    ```

## 4. Data Flow
1.  The client sends a `POST` request to `/api/v1/charts` with the JSON payload.
2.  The route handler, protected by `@login_required`, receives the request.
3.  The request JSON is parsed and validated.
4.  The `file_id` is used to look up the file's metadata in `session['files']`. If not found, a `404` error is returned. The server-side path to the CSV file is retrieved.
5.  The `ChartService` is called with the file path, axis information, and chart type.
6.  The `ChartService` performs the following:
    a. Reads the CSV file into a pandas DataFrame.
    b. Validates that `x_axis` and `y_axis` exist as columns in the DataFrame.
    c. Checks for data type compatibility between the columns and the requested `chart_type`.
    d. Uses Matplotlib to generate the chart image. The chart title will be the original filename.
    e. Creates a unique directory for the user's charts if it doesn't exist: `static/charts/<session_dir_id>/`.
    f. Saves the chart as a PNG file with a unique name (e.g., using `uuid.uuid4()`) into that directory.
    g. Returns the path to the newly created chart image.
7.  The route handler constructs the `chart_url` (a public-facing URL to the static image) and a `download_url` (a separate endpoint that will serve the file with a `Content-Disposition: attachment` header).
8.  The `chart_generated` event is logged with relevant metadata.
9.  A JSON response containing `chart_url` and `download_url` is returned to the client with a `201 Created` status code.

## 5. Security Considerations
-   **Authentication**: The endpoint must be decorated with `@login_required` to ensure only authenticated users can generate charts.
-   **Authorization**: The `file_id` from the request must be validated against the list of files in the current user's session (`session['files']`) to prevent a user from accessing another user's data.
-   **Input Sanitization**: While the `file_id` is an internal identifier, the `x_axis` and `y_axis` strings will be used to query a pandas DataFrame and are considered safe in that context. The `chart_type` is validated against a strict allowlist.
-   **File System Access**: Chart images will be saved to a designated `static/charts/` directory. The path will be constructed safely using the session directory ID to prevent path traversal attacks.

## 6. Error Handling
-   **400 Bad Request**:
    -   If the JSON payload is missing required fields or is malformed.
    -   If `chart_type` is not one of `'bar'`, `'line'`, or `'scatter'`.
    -   If `x_axis` or `y_axis` are not found in the CSV file's headers.
    -   If the column data types are not suitable for the selected `chart_type` (e.g., non-numeric data for a scatter plot).
-   **401 Unauthorized**:
    -   If the request is made by an unauthenticated user.
-   **404 Not Found**:
    -   If the `file_id` does not correspond to any file in the user's session.
-   **500 Internal Server Error**:
    -   If the chart generation process fails for an unexpected reason (e.g., Matplotlib internal error, disk I/O error).

## 7. Performance Considerations
-   **Image Caching**: Generated charts are static files. Standard HTTP caching headers (e.g., `ETag`, `Cache-Control`) can be configured on the web server (e.g., Nginx) serving the `/static` directory to reduce load for repeated requests to the same chart URL.

## 8. Implementation Steps
1.  **Create API Blueprint**: Create a new file `csvviz/api/routes.py` and define a `Blueprint` named `api_bp` with a URL prefix of `/api/v1`.
2.  **Define Endpoint Route**: In `csvviz/api/routes.py`, create a new route `POST /charts` under the `api_bp` blueprint.
3.  **Add Authentication**: Apply the `@login_required` decorator to the route.
4.  **Implement Request Validation**:
    -   Get the JSON data from the request.
    -   Check for the presence and basic type of all required fields (`file_id`, `x_axis`, `y_axis`, `chart_type`). Return `400` if invalid.
    -   Validate `chart_type` against the allowed values.
5.  **Implement File Lookup**:
    -   Retrieve the list of files from `session.get('files', [])`.
    -   Find the dictionary entry where `id` matches the request's `file_id`. If not found, return `404`.
    -   Extract the `server_path` and `original_filename` from the file's metadata.
6.  **Create Chart Service**:
    -   Create a new file `csvviz/services/chart_service.py`.
    -   Implement a `ChartService` class with a method `generate_chart(file_path, x_axis, y_axis, chart_type, title)`.
    -   Inside this method, use `pandas.read_csv()` to load the data.
    -   Validate column existence and data type compatibility.
    -   Use `matplotlib.pyplot` to create the chart.
    -   Ensure the output directory `static/charts/<session_dir_id>` exists, creating it if necessary.
    -   Save the figure to a unique filename in the output directory and return the file path.
7.  **Integrate Service in Route**:
    -   Instantiate and call the `ChartService` from the route handler.
    -   Wrap the service call in a `try...except` block to catch specific validation errors (returning `400`) and general exceptions (returning `500`).
8.  **Construct Response**:
    -   Use `url_for()` to generate the public-facing `chart_url` for the static image.
    -   Create a new endpoint `GET /charts/download/<filename>` and use `url_for()` to generate the `download_url`. This new endpoint will use `send_from_directory` to serve the file as an attachment.
9.  **Logging**: Implement logging for the `chart_generated` event.
10. **Register Blueprint**: Register the new `api_bp` blueprint in the application factory in `csvviz/__init__.py`.
