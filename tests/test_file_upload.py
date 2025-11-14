"""
Tests for file upload validation and handling.
"""

import pytest


@pytest.mark.file_ops
def test_TFU_001_upload_valid_csv(auth_client, sample_csv):
    """
    Test Case: TFU-001
    Description: Upload valid CSV file with correct headers and encoding.
    PRD/US Ref: US-002

    Verifies that a valid CSV file can be successfully uploaded and that
    the user is redirected to the dashboard with the file visible.
    """
    response = auth_client.post(
        "/upload",
        data={"csv_file": (sample_csv, "sales_data.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Should successfully upload and redirect to dashboard
    assert response.status_code == 200
    # Success message should be displayed
    assert b"File uploaded successfully" in response.data
    # File should appear in the uploaded files list
    assert b"sales_data.csv" in response.data


@pytest.mark.file_ops
def test_TFU_002_reject_non_csv_file(auth_client, non_csv_file):
    """
    Test Case: TFU-002
    Description: Reject non-CSV file (e.g., .txt, .xlsx).
    PRD/US Ref: US-003

    Verifies that attempting to upload a non-CSV file results in
    rejection with an appropriate error message.
    """
    response = auth_client.post(
        "/upload",
        data={"csv_file": (non_csv_file, "document.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Should reject the file and stay on dashboard
    assert response.status_code == 200
    # Error message should be displayed
    assert b"Invalid file type" in response.data or b"CSV" in response.data
    # File should NOT appear in the uploaded files list
    assert b"document.txt" not in response.data
