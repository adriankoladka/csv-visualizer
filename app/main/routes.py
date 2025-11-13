"""
Defines the main routes of the application.
"""
from flask import (
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage

from app.main import main_bp
from app.services.file_service import (
    MAX_FILES_PER_SESSION,
    add_file_to_session,
    get_csv_headers,
    is_valid_csv,
    remove_file_from_session,
)


@main_bp.route("/")
def index() -> Response:
    """
    Redirects to the dashboard if the user is logged in,
    otherwise to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard() -> str:
    """
    Renders the main dashboard page, displaying uploaded files and chart
    configuration.
    """
    files = session.get("files", [])
    active_file_id = request.args.get("file_id")
    active_file = None
    columns = []

    if not active_file_id and files:
        active_file_id = files[0]["id"]

    if active_file_id:
        active_file = next(
            (f for f in files if f["id"] == active_file_id), None
        )
        if active_file:
            columns = get_csv_headers(active_file["server_path"])

    return render_template(
        "dashboard.html",
        files=files,
        active_file=active_file,
        columns=columns,
    )


@main_bp.route("/upload", methods=["POST"])
@login_required
def upload_file() -> Response:
    """
    Handles file uploads, validates them, and adds them to the user's session.
    """
    if "csv_file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("main.dashboard"))

    file: FileStorage = request.files["csv_file"]

    if file.filename == "":
        flash("No file selected for uploading.")
        return redirect(url_for("main.dashboard"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file type. Please upload a CSV file.")
        return redirect(url_for("main.dashboard"))

    if not is_valid_csv(file):
        flash(
            "Invalid CSV file. Ensure it is UTF-8 encoded and has a header row."
        )
        return redirect(url_for("main.dashboard"))

    files = session.get("files", [])
    if len(files) >= MAX_FILES_PER_SESSION:
        flash(f"You can only upload up to {MAX_FILES_PER_SESSION} files.")
        return redirect(url_for("main.dashboard"))

    new_file = add_file_to_session(file)
    if new_file:
        flash("File uploaded successfully.")
        return redirect(url_for("main.dashboard", file_id=new_file["id"]))

    flash("Could not upload the file.")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/delete_file/<string:file_id>", methods=["POST"])
@login_required
def delete_file(file_id: str) -> Response:
    """
    Deletes a file from the user's session.
    """
    if remove_file_from_session(file_id):
        flash("File deleted successfully.")
    else:
        flash("Could not delete the file.")

    return redirect(url_for("main.dashboard"))
