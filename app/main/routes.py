"""
Defines the main routes of the application.
"""

from pathlib import Path

from flask import (
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
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
    update_file_in_session,
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
        active_file = next((f for f in files if f["id"] == active_file_id), None)
        if active_file:
            columns = get_csv_headers(active_file["server_path"])

    chart_filename = session.get("chart_filename")

    return render_template(
        "dashboard.html",
        files=files,
        active_file=active_file,
        columns=columns,
        chart_filename=chart_filename,
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

    # Check file size (1MB = 1048576 bytes)
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    if file_size > 1048576:
        flash("File size exceeds 1MB limit.")
        return redirect(url_for("main.dashboard"))

    if not is_valid_csv(file):
        flash("Invalid CSV file. Ensure it is UTF-8 encoded and has a header row.")
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
    # Check if we're deleting the currently active file
    active_file_id = request.args.get("file_id") or (
        session.get("files", [])[0]["id"] if session.get("files") else None
    )

    if remove_file_from_session(file_id):
        # Clear chart if we deleted the active file
        if file_id == active_file_id:
            session.pop("chart_filename", None)
        flash("File deleted successfully.")
    else:
        flash("Could not delete the file.")

    return redirect(url_for("main.dashboard"))


@main_bp.route("/update_file/<string:file_id>", methods=["POST"])
@login_required
def update_file(file_id: str) -> Response:
    """
    Updates a file in the user's session by replacing it with a new one.
    """
    if "csv_file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("main.dashboard"))

    file: FileStorage = request.files["csv_file"]

    if file.filename == "":
        flash("No file selected for updating.")
        return redirect(url_for("main.dashboard"))

    if not file.filename.lower().endswith(".csv"):
        flash("Invalid file type. Please upload a CSV file.")
        return redirect(url_for("main.dashboard"))

    # Check file size (1MB = 1048576 bytes)
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    if file_size > 1048576:
        flash("File size exceeds 1MB limit.")
        return redirect(url_for("main.dashboard"))

    if not is_valid_csv(file):
        flash("Invalid CSV file. Ensure it is UTF-8 encoded and has a header row.")
        return redirect(url_for("main.dashboard"))

    from app.services.file_service import update_file_in_session

    if update_file_in_session(file_id, file):
        flash("File updated successfully.")
        return redirect(url_for("main.dashboard", file_id=file_id))

    flash("Could not update the file.")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/generate_chart", methods=["POST"])
@login_required
def generate_chart() -> Response:
    """
    Generates a chart based on user selections and stores it in the session.
    """
    file_id = request.form.get("file_id")
    x_axis = request.form.get("x_axis")
    y_axis = request.form.get("y_axis")
    chart_type = request.form.get("chart_type")

    if not all([file_id, x_axis, y_axis, chart_type]):
        flash("Missing required parameters for chart generation.")
        return redirect(url_for("main.dashboard"))

    files = session.get("files", [])
    active_file = next((f for f in files if f["id"] == file_id), None)

    if not active_file:
        flash("Selected file not found.")
        return redirect(url_for("main.dashboard"))

    from app.services.chart_service import create_chart
    from app.services.logging_service import log_event

    chart_filename, error_message = create_chart(
        active_file["server_path"], x_axis, y_axis, chart_type
    )

    if chart_filename:
        session["chart_filename"] = chart_filename
        log_event("chart_generated")
        flash("Chart generated successfully.")
    else:
        flash(error_message or "Could not generate the chart.")

    return redirect(url_for("main.dashboard", file_id=file_id))


@main_bp.route("/charts/<string:filename>")
@login_required
def get_chart(filename: str) -> Response:
    """
    Serves a generated chart image.
    """
    from flask import send_from_directory

    charts_dir = Path(current_app.instance_path) / "charts"
    if request.args.get("download"):
        from app.services.logging_service import log_event

        log_event("chart_downloaded")
        return send_from_directory(charts_dir, filename, as_attachment=True)
    return send_from_directory(charts_dir, filename)
