"""
Defines the routes for authentication.
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.wrappers.response import Response

from app.auth import auth_bp
from app.auth.services import authenticate_user
from app.services.file_service import clear_session_dir


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """
    Authenticates a user and starts a session.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for("auth.login"))

        user = authenticate_user(username, password)

        if user:
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid credentials.")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout() -> Response:
    """
    Logs out the current user and ends the session.
    """
    clear_session_dir()
    logout_user()
    flash("You have been successfully logged out.")
    return redirect(url_for("auth.login"))
