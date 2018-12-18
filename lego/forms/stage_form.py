"""A form for moving up the stages."""

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import Optional


class StageForm(FlaskForm):
    """Stage Form."""
    stage = SelectField('Move to stage:',
                        choices=[('0', 'First Round'),
                                 ('1', 'Second Round (UK Final only)'),
                                 ('2', 'Quarter Final'),
                                 ('3', 'Semi Final'),
                                 ('4', 'Final')],
                        validators=[Optional()])
