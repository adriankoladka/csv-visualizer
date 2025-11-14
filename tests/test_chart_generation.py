"""
Tests for chart generation, display, and download functionality.
"""

import pytest

from conftest import get_chart_filename_from_dashboard, get_file_id_from_session


@pytest.mark.chart
def test_TCG_001_generate_bar_chart(auth_client, sample_csv):
    """
    Test Case: TCG-001
    Description: Generate bar chart with valid X and Y axis selections.
    PRD/US Ref: US-006

    This is a critical end-to-end test that verifies application behavior
    from the user's perspective. It simulates the complete workflow:
    1. User uploads a CSV file
    2. User selects X-axis, Y-axis, and chart type
    3. User generates a chart
    4. Chart is successfully created and displayed

    This test fulfills the requirement to have at least one test verifying
    the application behavior from the user perspective.
    """
    # Step 1: Upload the CSV file
    upload_response = auth_client.post(
        "/upload",
        data={"csv_file": (sample_csv, "sales_data.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert upload_response.status_code == 200
    assert b"File uploaded successfully" in upload_response.data

    # Step 2: Extract file_id from session
    file_id = get_file_id_from_session(auth_client)
    assert file_id is not None, "File ID should be present in session after upload"

    # Step 3: Generate a bar chart
    chart_response = auth_client.post(
        "/generate_chart",
        data={
            "file_id": file_id,
            "x_axis": "Month",
            "y_axis": "Revenue",
            "chart_type": "bar",
        },
        follow_redirects=True,
    )

    # Step 4: Verify chart was generated successfully
    assert chart_response.status_code == 200
    # Success message should be displayed
    assert (
        b"Chart generated successfully" in chart_response.data
        or b"generated" in chart_response.data.lower()
    )


@pytest.mark.chart
def test_TCG_002_chart_displayed_in_dashboard(auth_client, sample_csv):
    """
    Test Case: TCG-002
    Description: Generated chart image displayed in dashboard.
    PRD/US Ref: US-006

    Verifies that after generating a chart, the chart image is
    properly displayed in the dashboard view.
    """
    # Upload a CSV file first
    auth_client.post(
        "/upload",
        data={"csv_file": (sample_csv, "sales_data.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Extract file_id from session
    file_id = get_file_id_from_session(auth_client)
    assert file_id is not None

    # Generate a chart
    auth_client.post(
        "/generate_chart",
        data={
            "file_id": file_id,
            "x_axis": "Month",
            "y_axis": "Revenue",
            "chart_type": "bar",
        },
        follow_redirects=True,
    )

    # Get the dashboard and verify chart is displayed
    dashboard_response = auth_client.get("/dashboard")
    assert dashboard_response.status_code == 200
    # Chart image tag should be present
    assert b"<img" in dashboard_response.data or b"chart" in dashboard_response.data.lower()


@pytest.mark.chart
def test_TCG_003_download_chart_as_png(auth_client, sample_csv):
    """
    Test Case: TCG-003
    Description: Clicking download button serves PNG file with correct headers.
    PRD/US Ref: US-007

    Verifies that the download functionality properly serves the chart
    as a PNG file with the correct HTTP headers.
    """
    # Upload a CSV file
    auth_client.post(
        "/upload",
        data={"csv_file": (sample_csv, "sales_data.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    # Extract file_id from session
    file_id = get_file_id_from_session(auth_client)
    assert file_id is not None

    # Generate a chart
    auth_client.post(
        "/generate_chart",
        data={
            "file_id": file_id,
            "x_axis": "Month",
            "y_axis": "Revenue",
            "chart_type": "bar",
        },
        follow_redirects=True,
    )

    # Extract chart filename from dashboard
    chart_filename = get_chart_filename_from_dashboard(auth_client)
    assert chart_filename is not None, "Chart filename should be found in dashboard HTML"

    # Attempt to download the chart
    download_response = auth_client.get(f"/charts/{chart_filename}?download=true")

    # Verify download response
    assert download_response.status_code == 200
    # Content-Type should be image/png
    assert download_response.content_type == "image/png"
    # Content-Disposition header should indicate attachment
    assert "attachment" in download_response.headers.get("Content-Disposition", "")
