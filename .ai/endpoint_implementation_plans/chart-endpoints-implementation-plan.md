# API Endpoint Implementation Plan: Chart Endpoints

This document outlines the implementation plan for chart generation and retrieval endpoints.

---

## 1. POST /api/v1/charts

### 1.1. Endpoint Overview
Generates a static chart image from a user-uploaded CSV file. It requires the file ID, axis columns, and chart type.

### 1.2. Request Details
- **HTTP Method**: `POST`
- **URL Structure**: `/api/v1/charts`
- **Request Body**:
  ```json
  {
    "file_id": "string",
    "x_axis": "string",
    "y_axis": "string",
    "chart_type": "string"
  }
  ```

### 1.3. Response Details
- **Success (201 Created)**:
  ```json
  {
    "chart_url": "string",
    "download_url": "string"
  }
  ```
- **Errors**: `400`, `401`, `404`, `500`.

### 1.4. Data Flow
1. Client sends a `POST` request with chart parameters.
2. The route handler, protected by `@login_required`, validates the request.
3. The `file_id` is used to look up the file path from the user's session.
4. A `ChartService` is called with the file path and chart parameters.
5. The service reads the CSV, validates columns and data types, and generates the chart using Matplotlib.
6. The chart is saved as a PNG to a session-specific directory: `static/charts/<session_dir_id>/`.
7. The route handler constructs the `chart_url` and `download_url`.
8. The `chart_generated` event is logged.
9. A `201 Created` response is returned.

---

## 2. GET /api/v1/charts/{chart_filename}

### 2.1. Endpoint Overview
Retrieves a generated chart image. It can either be displayed inline or downloaded as an attachment.

### 2.2. Request Details
- **HTTP Method**: `GET`
- **URL Structure**: `/api/v1/charts/<string:chart_filename>`
- **Query Parameter**: `download` (boolean, optional).

### 2.3. Response Details
- **Success (200 OK)**:
  - **Content-Type**: `image/png`
  - **Body**: Raw binary data of the PNG image.
- **Errors**: `401`, `404`.

### 2.4. Data Flow
1. A `GET` request is made to the endpoint.
2. `@login_required` verifies authentication.
3. The handler retrieves the `session_dir_id` from the session.
4. A helper function constructs the secure path to the chart: `instance/charts/<session_dir_id>/<chart_filename>`.
5. It checks if the file exists and is within the user's directory.
6. `flask.send_file` is used to send the image, setting `as_attachment` based on the `download` query parameter.
7. If `download=true`, the `chart_downloaded` event is logged.

---

## 3. Shared Components

### 3.1. Used Types
- **ChartType**: `Literal['bar', 'line', 'scatter']`
- **TypedDicts**: For structuring request and response payloads.
  ```python
  from typing import TypedDict, Literal

  class ChartData(TypedDict):
      file_id: str
      x_axis: str
      y_axis: str
      chart_type: Literal['bar', 'line', 'scatter']

  class ChartResponse(TypedDict):
      chart_url: str
      download_url: str
  ```

### 3.2. Security Considerations
- **Authentication**: Both endpoints must be protected with `@login_required`.
- **Authorization**: Access is scoped to the user's session via `session_dir_id`, preventing one user from accessing another's charts or data.
- **Directory Traversal**: The `chart_filename` from the URL must be sanitized and validated to ensure it resolves to a path within the user's designated chart directory.

### 3.3. Performance Considerations
- **Image Caching**: Generated charts are static files, so standard HTTP caching headers (`ETag`, `Cache-Control`) can be used to reduce server load.
- **`send_file` Efficiency**: Flask's `send_file` is efficient for streaming small files like the generated charts.

### 3.4. Implementation Steps
1. **Create API Blueprint**: Define an `api_bp` blueprint if it doesn't exist.
2. **Create Chart Service**: Implement a `ChartService` in `csvviz/services/chart_service.py` to handle chart generation logic.
3. **Implement Routes**:
   - Add the `POST /charts` route to call the `ChartService`.
   - Add the `GET /charts/<chart_filename>` route to retrieve chart images.
4. **Handle File Paths**:
   - Use a helper function to securely construct and validate chart file paths based on the `session_dir_id`.
5. **Construct URLs**: Use `url_for()` to generate the `chart_url` and `download_url`.
6. **Logging**: Implement logging for `chart_generated` and `chart_downloaded` events.
7. **Register Blueprint**: Register the `api_bp` with the Flask application factory.
