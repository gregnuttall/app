"""
A form for resetting team names and numbers.

To be used by Admin accounts.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField
from wtforms.validators import DataRequired


class ResetTeamScoreForm(FlaskForm):
    """Reset Team Score Form."""
    id = HiddenField('Id', validators=[DataRequired()])
    stage = SelectField('Stage',
                        choices=[('attempt_1', 'Round 1 - Attempt 1'),
                                 ('attempt_2', 'Round 1 - Attempt 2'),
                                 ('attempt_3', 'Round 1 - Attempt 3'),
                                 ('round_2', 'Round 2'),
                                 ('quarter', 'Quarter Final'),
                                 ('semi', 'Semi Final'),
                                 ('final_1', 'Final 1'),
                                 ('final_2', 'Final 2')],
                        default='attempt_1',
                        validators=[DataRequired()])
