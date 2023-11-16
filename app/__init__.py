
"""
This module initializes the Flask application instance.

It creates a Flask object and sets up any necessary configuration options.
"""

from flask import Flask

app = Flask(__name__)

from app import routes
