"""A form for moving up the stages."""

from flask_wtf import FlaskForm
from wtforms import BooleanField

from lego.models import Team


def generate_manage_active_teams_form():
    """Generates manage active teams form."""
    class ManageActiveTeamsForm(FlaskForm):
        pass

    form = ManageActiveTeamsForm
    form.teams = Team.query.filter_by(is_practice=False).order_by('number ASC').all()

    for t in form.teams:
        setattr(form, str(t.id) + '_active', BooleanField('Active', default=t.active))

    return form()
