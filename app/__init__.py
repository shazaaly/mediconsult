
"""
This module initializes the Flask application instance.

It creates a Flask object and sets up any necessary configuration options.
"""

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate  = Migrate(app, db)

from app import routes, models
