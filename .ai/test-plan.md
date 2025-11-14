# Test Plan - CsvVisualizer

## 1. Overview

This document defines the testing strategy for the CsvVisualizer application. The test plan ensures that key functional requirements from the Product Requirements Document (PRD) are validated through automated tests using pytest. The testing approach focuses on integration tests that verify application behavior from the user's perspective.

## 2. Test Environment Setup

### 2.1. Test Configuration

Tests will use a separate configuration to isolate test execution from development/production:

-   **Instance Path**: Temporary directory created per test session
-   **Secret Key**: Test-specific secret key for session management
-   **Testing Mode**: Flask app configured with `TESTING=True`
-   **Session Management**: In-memory sessions isolated per test

### 2.2. Test Data

Sample CSV files will be created as pytest fixtures to support various test scenarios:

-   **Valid CSV**: Standard CSV with headers, numeric data (e.g., sales data)
-   **Non-CSV File**: Text file with .txt extension

## 3. Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── test_auth.py                   # Authentication and authorization tests
├── test_file_upload.py            # File upload validation and handling tests
├── test_file_management.py        # File CRUD operations tests
└── test_chart_generation.py       # Chart creation and rendering tests
```

## 4. Test Cases by Functional Requirement

### 4.1. File Upload (Requirement 3.1)

**Test Module**: `test_file_upload.py`

| Test Case ID | Description | PRD/US Ref |
|--------------|-------------|------------|
| TFU-001 | Upload valid CSV file with correct headers and encoding | US-002 |
| TFU-002 | Reject non-CSV file (e.g., .txt, .xlsx) | US-003 |

### 4.2. User Access Management (Requirement 3.2)

**Test Module**: `test_auth.py`

| Test Case ID | Description | PRD/US Ref |
|--------------|-------------|------------|
| TAU-001 | Login with valid credentials redirects to dashboard | US-001 |
| TAU-002 | Login with invalid credentials shows error message | US-001 |

### 4.3. Visualization Generation (Requirement 3.4)

**Test Module**: `test_chart_generation.py`

| Test Case ID | Description | PRD/US Ref |
|--------------|-------------|------------|
| TCG-001 | Generate bar chart with valid X and Y axis selections | US-006 |
| TCG-002 | Generated chart image displayed in dashboard | US-006 |
| TCG-003 | Clicking download button serves PNG file with correct headers | US-007 |

### 4.4. Data Management (Requirement 3.7)

**Test Module**: `test_file_management.py`

| Test Case ID | Description | PRD/US Ref |
|--------------|-------------|------------|
| TFM-001 | Dashboard displays list of uploaded files for current session | US-010 |

## 5. Test Execution Strategy

### 5.1. Test Organization

Tests are organized by functional area. Each test module focuses on a specific feature set.

### 5.2. Fixture Strategy

**Shared Fixtures** (in `conftest.py`):
-   `app`: Configured Flask application instance with test settings
-   `client`: Flask test client for making HTTP requests
-   `auth_client`: Pre-authenticated test client with active session
-   `sample_csv`: In-memory BytesIO object containing valid CSV data
-   `non_csv_file`: Text file for upload rejection testing
-   `temp_instance_path`: Temporary directory for test instance files

**Module-Specific Fixtures**:
-   Chart generation fixtures for pre-uploaded files
-   Mock file objects for upload testing
-   Session state fixtures for state-dependent tests

### 5.3. Test Markers

Tests will use pytest markers for categorization:

-   `@pytest.mark.auth`: Authentication and authorization tests
-   `@pytest.mark.file_ops`: File upload/delete/update operations
-   `@pytest.mark.chart`: Chart generation and download tests

## 6. Test Data Management

### 6.1. Sample CSV Files

Tests will use fixture-based CSV data rather than external files:

**Valid Sales Data CSV**:
```csv
Month,Revenue,Units
January,10000,150
February,12000,180
March,15000,200
```

**Non-CSV File**:
```text
This is a text file, not a CSV.
```

### 6.2. Test Instance Directory

Each test run creates a temporary instance directory that is automatically cleaned up after test execution. This ensures test isolation and prevents test pollution.
