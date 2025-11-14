"""
Tests for authentication and authorization functionality.
"""

import pytest


@pytest.mark.auth
def test_TAU_001_login_with_valid_credentials(client):
    """
    Test Case: TAU-001
    Description: Login with valid credentials redirects to dashboard.
    PRD/US Ref: US-001

    Verifies that a user can successfully log in with correct credentials
    and is redirected to the dashboard.
    """
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )

    # Should redirect to dashboard (200 OK after redirect)
    assert response.status_code == 200
    # Dashboard content should be present
    assert (
        b"Data Management" in response.data
        or b"dashboard" in response.data.lower()
    )


@pytest.mark.auth
def test_TAU_002_login_with_invalid_credentials(client):
    """
    Test Case: TAU-002
    Description: Login with invalid credentials shows error message.
    PRD/US Ref: US-001

    Verifies that attempting to log in with incorrect credentials
    results in an error message being displayed to the user.
    """
    response = client.post(
        "/login",
        data={"username": "wronguser", "password": "wrongpassword"},
        follow_redirects=True,
    )

    # Should stay on login page
    assert response.status_code == 200
    # Error message should be displayed
    assert (
        b"Invalid credentials" in response.data
        or b"error" in response.data.lower()
    )
