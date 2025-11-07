"""
Defines the User model for authentication.
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """
    Represents a user of the application.
    """

    def __init__(self, id: str, username: str, password: str) -> None:
        """
        Initializes a User object.

        Args:
            id (str): The unique identifier for the user.
            username (str): The user's username.
            password (str): The user's plain-text password.
        """
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verifies the provided password against the stored hash.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)


# In-memory user store (temporary solution)
_users = [
    User(id="1", username="testuser", password="password123"),
]

_user_by_id = {user.id: user for user in _users}
_user_by_username = {user.username: user for user in _users}


def get_user(user_id: str) -> User | None:
    """
    Retrieves a user by their ID.
    This function is required by Flask-Login's user_loader.

    Args:
        user_id (str): The ID of the user to retrieve.

    Returns:
        User | None: The User object if found, otherwise None.
    """
    return _user_by_id.get(user_id)


def get_user_by_username(username: str) -> User | None:
    """
    Retrieves a user by their username.

    Args:
        username (str): The username to look up.

    Returns:
        User | None: The User object if found, otherwise None.
    """
    return _user_by_username.get(username)
