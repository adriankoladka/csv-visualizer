# UI Architecture for CsvVisualizer

## 1. UI Structure Overview

The UI architecture for CsvVisualizer is designed for simplicity and efficiency, aligning with the MVP scope. It leverages server-side rendering via Flask and the Jinja2 templating engine, minimizing frontend complexity. The application's state, such as the currently selected file for charting, is managed through URL query parameters, making the UI itself stateless.

The core user experience is centered on a single-page dashboard that provides access to all primary functions: file management, chart configuration, and visualization. This approach reduces navigation and creates a focused workflow. The layout is a fixed, two-column design optimized for standard laptop screens. JavaScript is used sparingly for minor UX enhancements, such as displaying a "Generating..." indicator, without requiring a complex frontend build process.

## 2. View List

### a. Root Route
- **View Path**: `/`
- **Main Purpose**: To act as a smart entry point, directing users to the appropriate page based on their authentication status.
- **Logic**:
    - If the user is authenticated (`current_user.is_authenticated`), redirect to `/dashboard`.
    - If the user is not authenticated, redirect to `/login`.

### b. Base Template

-   **View Name**: `base.html`
-   **Main Purpose**: To provide a consistent HTML structure, header, and styling foundation for all other views.
-   **Key Information to Display**:
    -   Application title in the header.
    -   A conditional "Logout" link, visible only to authenticated users.
-   **Key View Components**:
    -   **Header**: Contains the application title.
    -   **Logout Link**: A link that directs the user to the `/logout` route, terminating their session.
    -   **Content Block**: A Jinja2 block where child templates (`login.html`, `dashboard.html`) will inject their specific content.

### c. Login View

-   **View Name**: `login.html`
-   **View Path**: `/login`
-   **Main Purpose**: To authenticate users before granting access to the application's core features.
-   **Key Information to Display**:
    -   Application title ("CsvVisualizer").
    -   Username and password input fields.
    -   A "Login" button.
    -   Error messages (e.g., "Invalid credentials") via Flask's flash messaging system.
-   **Key View Components**:
    -   **Login Form**: A simple form that submits user credentials to the `/login` route.
-   **UX and Security Considerations**:
    -   **UX**: The view is clean and focused, presenting only the necessary elements for login. Feedback on success or failure is immediate.
    -   **Security**: The form should submit credentials over HTTPS. The actual authentication logic and session management are handled by the backend (Flask-Login), keeping the frontend secure.

### d. Dashboard View

-   **View Name**: `dashboard.html`
-   **View Path**: `/dashboard`
-   **Main Purpose**: To serve as the central hub for all user activities, including file management, chart configuration, and visualization.
-   **Key Information to Display**:
    -   **Left Column**:
        -   File upload form.
        -   A list of files uploaded during the current session.
        -   A message guiding the user if no files are uploaded.
    -   **Right Column**:
        -   Chart configuration controls (dropdowns for X-axis, Y-axis, chart type).
        -   A placeholder area for the chart image.
        -   The generated chart image.
        -   A "Download" button for the generated chart.
-   **Key View Components**:
    -   **File Upload Form**: A `multipart/form-data` form for uploading CSV files, which will be handled by a dedicated view function (e.g., `/upload`).
    -   **Session File List**: A dynamically generated list of uploaded files. Each file entry includes its name and "Update" and "Delete" buttons. The file name is a link that reloads the dashboard with that file selected for charting (e.g., `/dashboard?file_id=<file_id>`).
    -   **Chart Configuration Form**: A form containing dropdowns for X-axis, Y-axis, and chart type. It will submit to a dedicated view function (e.g., `/generate-chart`).
    -   **Chart Display Area**: An `<img>` tag that displays the generated chart by linking to its URL (e.g., `/charts/<chart_filename>`).
    -   **Download Button**: A link pointing to the chart download route (e.g., `/charts/<chart_filename>?download=true`).
-   **UX and Security Considerations**:
    -   **UX**: The two-column layout keeps file management and chart configuration visible simultaneously. Using URL query parameters to manage the selected file state allows for bookmarking and predictable reloads. A loading indicator (e.g., 'Generating...') will be displayed using embedded JavaScript after the user clicks 'Generate Chart'. If the currently active file is deleted, the chart configuration area will be cleared, and the view will default to the next available file or the initial empty state. Upon file selection, the X and Y-axis dropdowns will default to the first and second columns, respectively.
    -   **Security**: All actions are protected by the backend's session management. The UI provides the interface for submitting forms to authenticated routes.

## 3. User Journey Map

The primary user journey is linear and designed to guide the user from authentication to chart creation seamlessly.

1.  **Login**: The user visits the application and is presented with the `login.html` view. They enter their credentials and submit the form.
2.  **Redirection to Dashboard**: Upon successful authentication, the user is redirected to the `dashboard.html` view.
3.  **File Upload**: The user interacts with the file upload form in the left column to upload their first CSV file. The page reloads, and the new file appears in the session file list, automatically selected for charting.
4.  **Chart Configuration**: The file's columns now populate the X-axis and Y-axis dropdowns in the right column. The user selects their desired columns and chart type.
5.  **Chart Generation**: The user clicks the "Generate Chart" button. The page reloads, and the generated chart image appears in the chart display area, along with a "Download" button.
6.  **Chart Download**: The user clicks the "Download" button to save the chart as a PNG file.
7.  **Further Actions (Optional)**:
    -   The user can reconfigure the chart and generate a new version.
    -   The user can upload another file and select it from the list to begin a new visualization.
    -   The user can delete or update files from the session list.
8.  **Logout**: The user clicks the "Logout" link in the header, which clears their session data and redirects them back to the `login.html` view.

## 4. Layout and Navigation Structure

-   **Layout**: The application uses a simple, fixed two-column layout on the main dashboard, which is not responsive, as per the MVP requirements.
    -   **Header**: A persistent header at the top contains the application title and the logout link.
    -   **Left Column**: Dedicated to data input and management (file upload and session file list).
    -   **Right Column**: Dedicated to configuration and output (chart controls and display).
-   **Navigation**: Navigation is minimal and state-driven.
    -   Unauthenticated users are restricted to the `/login` route.
    -   Authenticated users are directed to the `/dashboard`.
    -   The primary "navigation" on the dashboard is not between pages but is achieved by reloading the dashboard with different query parameters (e.g., `?file_id=...`) to change the active context.
    -   Logout is the only explicit navigation action, returning the user to the login page.

## 5. Key Components

-   **Login Form**: A standard HTML form for authentication.
-   **File Management Widget**: A composite component in the dashboard's left column that includes the file upload form and the list of session files. Each item in the list has controls for selection, update, and deletion.
-   **Chart Configuration Panel**: A set of dropdown menus in the dashboard's right column for selecting chart parameters.
-   **Chart Display**: An area that conditionally displays either a placeholder message or the generated chart image with a download button.
-   **Flash Message Display**: A component used on both the login and dashboard pages to display contextual feedback (errors, success messages) to the user.
