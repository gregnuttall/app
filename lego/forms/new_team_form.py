"""
A form for adding team names and numbers.

To be used by Admin accounts.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class NewTeamForm(FlaskForm):
    """New Team Form."""
    name = StringField('Name', validators=[DataRequired()])
    number = IntegerField('Number', validators=[DataRequired()])
