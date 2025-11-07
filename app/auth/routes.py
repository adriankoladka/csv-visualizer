"""
Defines the routes for authentication.
"""
from flask import Response, jsonify, request
from flask_login import login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.services import authenticate_user


@auth_bp.route("/users/login", methods=["POST"])
def login() -> Response:
    """
    Authenticates a user and starts a session.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Request body must be JSON."}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return (
                jsonify({"message": "Username and password are required."}),
                400,
            )

        user = authenticate_user(username, password)

        if user:
            login_user(user)
            return jsonify({"message": "Login successful."}), 200
        else:
            return jsonify({"message": "Invalid credentials."}), 401

    except Exception:
        # In a real app, you would log this error.
        return jsonify({"message": "An internal server error occurred."}), 500


@auth_bp.route("/users/logout", methods=["POST"])
@login_required
def logout() -> Response:
    """
    Logs out the current user and ends the session.
    """
    logout_user()
    return jsonify({"message": "You have been successfully logged out."}), 200
