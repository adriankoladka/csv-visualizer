"""
Shared pytest fixtures for the CsvVisualizer test suite.
"""

import os
import tempfile
from io import BytesIO

import pytest

from app import create_app
from config import Config


class TestConfig(Config):
    """
    Test-specific configuration for Flask application.
    """

    TESTING = True
    SECRET_KEY = "test-secret-key-for-testing-only"
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


@pytest.fixture
def app():
    """
    Creates a Flask application configured for testing.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Create a temporary directory for the instance path
    temp_instance = tempfile.mkdtemp()

    # Create app with test config and custom instance path
    test_app = create_app(TestConfig)
    test_app.instance_path = temp_instance

    yield test_app

    # Cleanup: Remove temporary instance directory
    import shutil

    if os.path.exists(temp_instance):
        shutil.rmtree(temp_instance)


@pytest.fixture
def client(app):
    """
    Creates a Flask test client for making HTTP requests.

    Args:
        app: Flask application fixture.

    Returns:
        FlaskClient: Test client for the application.
    """
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """
    Creates a pre-authenticated test client with an active session.

    Args:
        client: Flask test client fixture.

    Returns:
        FlaskClient: Authenticated test client.
    """
    # Log in the test user
    client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def sample_csv():
    """
    Creates a valid CSV file as a BytesIO object.

    Returns:
        BytesIO: In-memory CSV file with headers and numeric data.
    """
    csv_content = b"Month,Revenue,Units\nJanuary,10000,150\nFebruary,12000,180\nMarch,15000,200\n"
    csv_file = BytesIO(csv_content)
    csv_file.name = "sales_data.csv"
    csv_file.seek(0)
    return csv_file


@pytest.fixture
def non_csv_file():
    """
    Creates a non-CSV text file as a BytesIO object.

    Returns:
        BytesIO: In-memory text file for upload rejection testing.
    """
    text_content = b"This is a text file, not a CSV."
    text_file = BytesIO(text_content)
    text_file.name = "document.txt"
    text_file.seek(0)
    return text_file


def get_file_id_from_session(client):
    """
    Helper function to extract the first file ID from the Flask session.

    Args:
        client: Flask test client with an active session.

    Returns:
        str: The file ID of the first uploaded file, or None if no files exist.
    """
    with client.session_transaction() as sess:
        files = sess.get("files", [])
        if files:
            return files[0]["id"]
        return None


def get_chart_filename_from_dashboard(client):
    """
    Helper function to extract the chart filename from the dashboard HTML.

    Args:
        client: Flask test client with an active session.

    Returns:
        str: The chart filename (e.g., 'sales_data_bar.png'), or None if not found.
    """
    import re

    response = client.get("/dashboard")
    if response.status_code == 200:
        # Look for chart URL in img src or download link
        # Pattern: /charts/<filename>.png or url_for result
        patterns = [
            rb'/charts/([^"\'?\s]+\.png)',  # Standard URL pattern
            rb'filename=([^"\'?\s]+\.png)',  # Download link pattern
            rb'src="[^"]*?/charts/([^"]+\.png)"',  # img src pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.data)
            if match:
                return match.group(1).decode("utf-8")
    return None
