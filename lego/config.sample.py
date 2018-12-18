"""
Configuration for the Lego Challenge application.

See the manual for what these do.
"""

from os import path


def db_uri() -> str:
    """
    Generate the path for the database file.
    """
    cur_dir = path.dirname(path.abspath(__file__))
    db_dir = path.join(cur_dir, 'tmp')

    if True:
        db_file = 'app.db'
    else:
        db_file = 'test.db'

    return 'sqlite:///' + path.join(db_dir, db_file)

# ----------------
# Default settings
# ----------------
WTF_CSRF_ENABLED = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = db_uri()

# ---------------------
# Customisable settings
# ---------------------
SECRET_KEY = 'your-secret-key'
LEGO_APP_TYPE = 'bristol'
