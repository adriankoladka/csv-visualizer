# View Implementation Plan: dashboard.html

## 1. Overview
This document outlines the implementation plan for the `dashboard.html` view. This is the main user interface where all core application functionality resides. It serves as the central hub for file management, chart configuration, and visualization. The view is rendered by the `main.dashboard` view function and is only accessible to authenticated users. The template file for this view is `app/templates/dashboard.html`.

## 2. UI Components
The dashboard will have a fixed, two-column layout.
*   **Inheritance:** The template will extend `base.html`.
*   **Left Column (Data Management):**
    *   **File Upload Form:** A `multipart/form-data` form that submits to a `/upload` route. It will contain an `<input type="file" name="csv_file">` and a submit button.
    *   **Session File List:** A section that dynamically displays the list of files uploaded during the session.
        *   It will iterate through the `files` list passed from the backend.
        *   If the list is empty, it will display a message like "No files uploaded yet."
        *   Each file will be displayed as a list item, showing the `original_filename`. The active file will be visually highlighted.
        *   Each file item will have:
            *   A link to select the file for charting (e.g., `<a href="{{ url_for('main.dashboard', file_id=file.id) }}">...</a>`).
            *   A "Delete" button within a small form that posts to a `/delete_file/<file_id>` route.
*   **Right Column (Charting):**
    *   **Chart Configuration Form:** A form that submits to a `/generate_chart` route. This form will only be visible if a file is selected.
        *   **X-Axis Dropdown:** A `<select name="x_axis">` menu populated with the column headers of the selected CSV file.
        *   **Y-Axis Dropdown:** A `<select name="y_axis">` menu, also populated with the column headers.
        *   **Chart Type Dropdown:** A `<select name="chart_type">` menu with options for "Bar", "Line", and "Scatter".
        *   A hidden input `<input type="hidden" name="file_id" value="{{ active_file.id }}">` to pass the active file ID.
        *   A "Generate Chart" submit button.
    *   **Chart Display Area:**
        *   If a chart has been generated, an `<img>` tag will display the chart image by pointing to its URL (e.g., `url_for('main.get_chart', filename=chart_filename)`).
        *   If no chart is generated, a placeholder message like "Configure and generate a chart to see it here" will be shown.
    *   **Download Button:** A link or button that appears only when a chart is displayed, pointing to the download route (e.g., `url_for('main.get_chart', filename=chart_filename, download=True)`).

## 3. Associated Route
*   **View Function:** The primary view is handled by the `dashboard()` function in `app/main/routes.py`.
*   **URL:** The route is accessible at `/dashboard`.
*   **Decorator:** The route must be protected with the `@login_required` decorator.
*   **HTTP Methods:** The `dashboard()` function itself only needs to handle `GET` requests. Other actions (upload, delete, generate) will have their own dedicated routes and view functions.

## 4. Backend Logic
The `dashboard()` view function will contain the following logic for a `GET` request:
1.  Retrieve the list of uploaded file metadata from the session: `files = session.get('files', [])`.
2.  Determine the currently active file by checking the URL query parameter: `active_file_id = request.args.get('file_id')`.
3.  If `active_file_id` is not present, and files exist, default to the first file in the list.
4.  Loop through the `files` list to find the dictionary entry for the `active_file`.
5.  If an `active_file` is found:
    *   Read its header row using a helper function (e.g., `get_csv_headers(active_file['server_path'])`) to get the list of `columns`.
6.  Check the session for information about a previously generated chart: `chart_filename = session.get('chart_filename')`.
7.  Pass all relevant data (`files`, `active_file`, `columns`, `chart_filename`) to the template context.

## 5. Response
*   The server will send a `200 OK` HTTP response containing the fully rendered `dashboard.html` page, populated with the data retrieved in the backend logic.
