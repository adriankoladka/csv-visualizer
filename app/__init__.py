"""
Initializes the Flask application and its components.
"""
import os
from typing import Type

from flask import Flask

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

    return app
