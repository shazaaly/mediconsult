
"""
This module initializes the Flask application instance.

It creates a Flask object and sets up any necessary configuration options.
"""

from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

from app import routes
