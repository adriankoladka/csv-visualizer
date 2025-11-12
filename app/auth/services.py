"""
Contains the business logic for authentication.
"""

from app.auth.models import User, get_user_by_username


def authenticate_user(username: str, password: str) -> User | None:
    """
    Authenticates a user by username and password.

    Args:
        username (str): The user's username.
        password (str): The user's password.

    Returns:
        User | None: The User object if authentication is successful,
                     otherwise None.
    """
    user = get_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None
