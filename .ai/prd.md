# Product Requirements Document (PRD) - CsvVisualizer

## 1. Product Overview
The CsvVisualizer is a Minimum Viable Product (MVP) designed to provide a simple, web-based interface for non-technical users to generate basic data visualizations from CSV files. Users can upload one or more CSV files, manage them in a session-based list, and select a file to generate a chart. For a selected file, users can choose data columns for the X and Y axes, pick a chart type (Bar, Line, or Scatter), and generate a static chart image. All uploaded data is processed within the user's session and is not stored persistently. The application focuses on simplicity and speed, allowing users to quickly create and download visualizations for presentations or reports without needing to use complex software.

## 2. User Problem
The CSV (Comma-Separated Values) format is a ubiquitous standard for storing and exchanging tabular data. However, in its raw text form, it is difficult for users to interpret, identify trends, or draw meaningful conclusions from the data. Existing data analysis tools are often powerful but come with a steep learning curve, making them inaccessible to users without a technical background who need to create simple visualizations quickly.

## 3. Functional Requirements
- 3.1. File Upload: A user interface for uploading CSV files. Each uploaded file is added to the user's session list. The interface must clearly state the following constraints for each file:
  - Maximum file size: 1MB
  - Delimiter: Comma-separated
  - Encoding: UTF-8
  - Structure: Headers must be in the first row.
- 3.2. User Access Management: A system to manage user access, requiring users to log in to use the application.
- 3.3. Chart Configuration: After a file is selected from the user's session list, the user is presented with a dashboard containing:
  - A dropdown menu to select a column for the X-axis from the selected file.
  - A dropdown menu to select a column for the Y-axis from the selected file.
  - A dropdown menu to select a chart type from "Bar", "Line", or "Scatter".
- 3.4. Visualization Generation: A backend process that:
  - Reads the data from the uploaded CSV file.
  - Generates a chart image based on the user's axis and chart type selections.
- 3.5. Chart Display and Download:
  - The generated chart image is displayed within the user's browser.
  - A "Download" button allows the user to save the generated chart as a PNG file.
- 3.6. Logging: The application must log two specific events for metric tracking: `chart_generated` and `chart_downloaded`. These events must be written to a dedicated log file in a structured format suitable for post-hoc application success evaluation.
- 3.7. Data Management: A server-side process for managing uploaded data on a temporary basis.
  - Users can view a list of CSV files uploaded during their current session.
  - Users can update a file in the list by replacing it with a new one.
  - Users can delete files from this list.
  - Uploaded CSV files are stored in a temporary directory on the server only for the duration of the user's active session.
  - All temporary data associated with a session is automatically deleted upon user logout or session expiration.
  - This approach allows users to manage multiple datasets within a single session without requiring long-term data persistence.

## 4. Product Boundaries
The following features and functionalities are explicitly outside the scope of the MVP:
- Support for file formats other than CSV (e.g., JSON).
- Interactive visualizations (e.g., tooltips on hover, zooming).
- Generation of advanced or complex chart types (e.g., heatmaps).
- User-defined data transformation or cleaning capabilities within the application.
- Combining data from multiple CSV files into a single visualization.
- Support for multiple simultaneous file uploads.
- Saving, storing, or managing previously uploaded files or generated charts for users. All user data is deleted at the end of a session.
- Persistent storage of user data, uploaded files, or generated charts across sessions.

## 5. User Stories

- ID: US-001
- Title: User Authentication
- Description: As a user, I want to be able to log in to the application so that I can securely access its features.
- Acceptance Criteria:
  - Given I am on the application's landing page, I should see a login form.
  - When I enter my credentials and submit the form, my identity is verified.
  - Upon successful login, I am redirected to the file upload page.
  - If login fails, I am shown an error message and remain on the login page.

- ID: US-002
- Title: CSV File Upload
- Description: As a logged-in user, I want to upload a CSV file from my local machine so that I can prepare it for visualization.
- Acceptance Criteria:
  - Given I am on the file upload page, I can see an upload interface.
  - The interface displays the file constraints (1MB max, CSV, UTF-8, headers in first row).
  - When I select a valid CSV file and click "Upload", the file is successfully sent to the server.
  - Upon successful upload, I am redirected to the chart configuration dashboard.

- ID: US-003
- Title: Handle Invalid File Type Upload
- Description: As a user, I want to be notified if I attempt to upload a file that is not a CSV.
- Acceptance Criteria:
  - Given I am on the file upload page, I attempt to upload a non-CSV file (e.g., .txt, .xlsx).
  - When I submit the file, the system detects the incorrect file type.
  - I am shown a clear error message on the screen stating that only CSV files are permitted.
  - I remain on the file upload page to correct my selection.

- ID: US-004
- Title: Handle Oversized File Upload
- Description: As a user, I want to be notified if my CSV file exceeds the 1MB size limit.
- Acceptance Criteria:
  - Given I am on the file upload page, I attempt to upload a CSV file larger than 1MB.
  - When I submit the file, the system checks its size.
  - I am shown a clear error message stating the file is too large and must be under 1MB.
  - I remain on the file upload page.

- ID: US-005
- Title: Chart Configuration
- Description: As a user who has uploaded a CSV, I want to configure the chart by selecting the data for the axes and the chart type.
- Acceptance Criteria:
  - Given I have successfully uploaded a CSV file, I am on the chart configuration dashboard.
  - I can see three dropdown menus: "X-Axis", "Y-Axis", and "Chart Type".
  - The X-Axis and Y-Axis dropdowns are populated with the header names from my uploaded CSV file.
  - The "Chart Type" dropdown contains the options "Bar", "Line", and "Scatter".
  - I can select one option from each of the three dropdowns.

- ID: US-006
- Title: Chart Generation
- Description: As a user, I want to generate a chart based on my configuration choices.
- Acceptance Criteria:
  - Given I have selected an X-axis, a Y-axis, and a chart type, I can see a "Generate Chart" button.
  - When I click the "Generate Chart" button, the backend process is initiated.
  - The system logs a `chart_generated` event.
  - The page updates to display the newly generated chart image.

- ID: US-007
- Title: Chart Download
- Description: As a user, I want to download the generated chart as a PNG image file.
- Acceptance Criteria:
  - Given a chart is displayed on the page, I can see a "Download Image" button.
  - When I click the "Download Image" button, a PNG file of the chart is downloaded to my local machine.
  - The system logs a `chart_downloaded` event.

- ID: US-008
- Title: User Logout
- Description: As a logged-in user, I want to be able to log out of the application to end my session securely.
- Acceptance Criteria:
  - Given I am logged into the application, I can see a "Logout" button or link.
  - When I click the "Logout" button, my session is terminated.
  - I am redirected to the login page.

- ID: US-009
- Title: Temporary Data Handling
- Description: As a user, I want my uploaded data to be handled securely and deleted after my session ends, so that my information is not stored permanently on the server.
- Acceptance Criteria:
  - Given I have an active session, when I upload a CSV file, it is stored in a temporary location associated with my session.
  - Given my session ends (either by logging out or timing out), the temporary location and the CSV file within it are automatically and permanently deleted.
  - The application does not persist my uploaded CSV data beyond the scope of my active session.

- ID: US-010
- Title: View Uploaded Files
- Description: As a user, I want to see a list of all CSV files I have uploaded during my current session, so I can manage them easily.
- Acceptance Criteria:
  - Given I have uploaded one or more CSV files, I can see a list of these files on my dashboard.
  - Each file in the list is identifiable by its name.
  - This list only shows files from my current active session.

- ID: US-011
- Title: Delete Uploaded File
- Description: As a user, I want to be able to delete a previously uploaded CSV file from my session, so I can remove irrelevant or incorrect data.
- Acceptance Criteria:
  - Given I can see the list of my uploaded files, there is a "Delete" button next to each file name.
  - When I click the "Delete" button for a specific file, that file is removed from the list and deleted from the server.
  - I receive a confirmation that the file has been deleted.

- ID: US-012
- Title: Update Uploaded File
- Description: As a user, I want to be able to replace an uploaded CSV file with a new one, so I can correct an error or use a different dataset without starting over.
- Acceptance Criteria:
  - Given I can see the list of my uploaded files, there is an "Update" button next to each file name.
  - When I click the "Update" button for a specific file, I am prompted to select a new CSV file.
  - Upon selecting a new valid CSV file, the old file is replaced with the new one in my session list and on the server.
  - I receive a confirmation that the file has been updated.

## 6. Success Metrics
The primary success criterion for the MVP is that at least 50% of all generated charts are downloaded by users. This indicates that the tool is not just being used for exploration, but is producing valuable assets for users. The application should log `chart_generated` and `chart_downloaded` events to provide the data for this metric.