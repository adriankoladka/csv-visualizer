"""
Defines the main routes of the application.
"""

from flask import redirect, render_template, session, url_for
from flask_login import current_user, login_required

from app.main import main_bp


@main_bp.route("/")
def index():
    """
    Redirects to the dashboard if the user is logged in,
    otherwise to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Renders the main dashboard page, displaying uploaded files.
    """
    uploaded_files = session.get("uploaded_files", {})
    return render_template("dashboard.html", files=uploaded_files)
