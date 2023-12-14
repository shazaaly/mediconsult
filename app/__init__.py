
"""
This module initializes the Flask application instance.

It creates a Flask object and sets up any necessary configuration options.
"""

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler
from flask_bootstrap import Bootstrap
import moment
from flask_moment import Moment


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
migrate  = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
Bootstrap(app)
moment=Moment(app)

# Make  models searchable


from app import routes, models, errors


