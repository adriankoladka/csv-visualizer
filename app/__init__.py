"""
Initializes the Flask application and its components.
"""

import os
from typing import Type

from flask import Flask, flash, jsonify, redirect, url_for
from flask_login import LoginManager

from config import Config


def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Creates and configures the Flask application.
    Args:
        config_class (Type[Config]): The configuration class to use.
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Handles unauthorized access by redirecting to the login page.
        """
        flash("You must be logged in to view this page.")
        return redirect(url_for("auth.login"))

    from app.auth.models import get_user

    @login_manager.user_loader
    def load_user(user_id: str):
        """
        Loads a user from the in-memory store.
        """
        return get_user(user_id)

    # Register blueprints
    from app.auth import auth_bp

    app.register_blueprint(auth_bp)

    from app.main import main_bp

    app.register_blueprint(main_bp)

    # Setup event logger
    from app.services.logging_service import setup_event_logger

    with app.app_context():
        setup_event_logger()

    # Run cleanup on startup
    from app.services.cleanup_service import cleanup_expired_sessions

    with app.app_context():
        cleanup_expired_sessions()

    return app
