"""
Handles the configuration of the Flask application.
"""
import os

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class Config:
    """
    Base configuration class for the Flask application.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
