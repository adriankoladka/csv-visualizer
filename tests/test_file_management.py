"""
Tests for file management (CRUD operations on uploaded files).
"""

import pytest


@pytest.mark.file_ops
def test_TFM_001_display_uploaded_files_list(auth_client, sample_csv):
    """
    Test Case: TFM-001
    Description: Dashboard displays list of uploaded files for current session.
    PRD/US Ref: US-010

    Verifies that the dashboard correctly displays a list of all files
    that have been uploaded during the current user session.
    """
    # Upload first CSV file
    auth_client.post(
        "/upload",
        data={"csv_file": (sample_csv, "sales_data.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Create a second CSV file
    csv_content = b"Product,Price,Stock\nWidget,29.99,100\nGadget,49.99,50\n"
    from io import BytesIO

    second_csv = BytesIO(csv_content)
    second_csv.name = "inventory.csv"
    second_csv.seek(0)

    # Upload second CSV file
    auth_client.post(
        "/upload",
        data={"csv_file": (second_csv, "inventory.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Get dashboard and verify both files are listed
    response = auth_client.get("/dashboard")
    assert response.status_code == 200

    # Both filenames should appear in the file list
    assert b"sales_data.csv" in response.data
    assert b"inventory.csv" in response.data

    # File list header should be present
    assert b"Uploaded Files" in response.data or b"files" in response.data.lower()
