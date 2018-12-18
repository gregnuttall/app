"""
A form for editing team names and numbers.

To be used by Admin accounts.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField
from wtforms.validators import DataRequired


class EditTeamForm(FlaskForm):
    """Edit Team Form."""
    id = HiddenField('Id', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    number = IntegerField('Number', validators=[DataRequired()])
