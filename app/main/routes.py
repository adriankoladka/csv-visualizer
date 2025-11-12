"""
Defines the main routes of the application.
"""

from flask import render_template
from flask_login import login_required

from app.main import main_bp


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Renders the main dashboard page.
    """
    return render_template("dashboard.html")
