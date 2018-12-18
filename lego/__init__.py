"""init"""

import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import lego.util as util

# use a helpful error message here as it can be a bit confusing otherwise
try:
    import lego.config as config
except ImportError:
    logging.error('Could not import config module. Please ensure you have copied '
                  'config.sample.py to config.py as detailed in the setup instructions.')
    sys.exit(1)

# create app object and load configuration
app = Flask(__name__)
app.config.from_object(config)

# initialise logging
app.logger.addHandler(util.create_log_handler('app'))

# database
db = SQLAlchemy(app)

# login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.load_stage = util.load_stage

# imports of modules that require app
from lego import cli, routes
from lego.models import User

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
