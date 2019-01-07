"""
The form used for scoring the active round.

Needs to be updated each year with the new tasks.
"""

from flask_wtf import FlaskForm
from wtforms import RadioField, BooleanField, SelectField, IntegerField, StringField, HiddenField, Form, FormField, FieldList
from wtforms.compat import text_type
from wtforms.validators import InputRequired, Optional
import json
import os
from collections import OrderedDict


def parse_json(path):
    """
    Parses json file and generates a FieldList full of FieldLists for all the missions
    """
    json_data = json.load(open(path))
    # ordered dict to ensure that missions are displayed in the correct order
    missions = OrderedDict()
    # sorts the json return based on the mission name as json libraries do not preserve order
    for key, mission_data in sorted(json_data.items()):
        # ordered dict to ensure that objectives for the mission are displayed in the correct order
        mission = OrderedDict()
        # enumerates the missions so that each field will be given a unique name
        for task_no, data in enumerate(mission_data):
            # converts the task_no to a string to avoid a crash
            task_no = str(task_no)
            # checks the data type and instantiates the fields based on the data type
            if data['type'] == 'StringField':
                mission['label'] = globals()[data['type']](data['string'])
            elif data['type'] == 'BooleanField':
                mission[task_no] = globals()[data['type']](data['string'])
            elif data['type'] == 'BonusField':
                mission[task_no] = globals()[data['type']](data['string'],
                                                           value=data['value'])
            else:
                mission[task_no] = globals()[data['type']](data['string'],
                                                           choices=[(choice['value'], choice['string'])
                                                                    for choice in data['choices']],
                                                           default=0,
                                                           validators=[Optional()])
        # generates the mission specific FieldList and adds it to the dict to be used for creating the full list
        missions[key] = FieldList(FormField(type(str(task_no), (ScoredForm,), mission)), min_entries=1)

    # generates FiledList containing each missions FieldList
    return FieldList(FormField(type('Missions', (Form,), missions)), min_entries=1)


class BonusField(BooleanField):
    """Bonus Field."""
    def __init__(self, label=None, validators=None, false_values=None, value=None, **kwargs):
        super().__init__(label, validators, false_values, **kwargs)
        self.value = value

    def _value(self):
        if self.raw_data:
            return text_type(self.raw_data[0])

        if self.value:
            return self.value

        return 'y'

class ScoredForm(Form):
    """Form."""
    def score(self):
        """
        Extension to the form class to allow the form to generate a score based on the fields it contains.
        """
        score = 0

        # gets the score for every type of field and returns the result for the mission
        for _, task in self._fields.items():
            if isinstance(task, StringField):
                # strings do not carry any score
                continue
            elif isinstance(task, BonusField):
                score += task.data * int(task.value)
            elif isinstance(task, BooleanField):
                # boolean fields used when score is conditional on a factor occurring
                if task.data is False:
                    return 0
            else:
                score += int(task.data)

        return score


class ScoreRoundForm(FlaskForm):
    """ Fields """
    team = SelectField('Team:', validators=[InputRequired(message='Please select a team.')])
    yellow_card = BooleanField('Yellow card')
    confirm = HiddenField(default=0)
    score = IntegerField('Total score', validators=[Optional()])

    # parses json into FieldList
    missions = parse_json(os.path.dirname(__file__) + '/../missions.json')

    def points_scored(self) -> (int, str):
        """Calculate the points scored for this round."""
        # keeps individual mission scores saved separately for score disputes
        score_breakdown = {}
        # loops through every mission and adds the score to the score breakdown dictionary
        for mission_name, mission in self.missions.entries[0].form._fields.items():
            score_breakdown[mission_name] = mission.entries[0].form.score()

        if sum(score_breakdown.values()):
            score = sum(score_breakdown.values())
        else:
            score = 0
        # ensure score is not less than 0    
        if score < 0:
            score = 0
        score_breakdown = str(score_breakdown)

        return score, score_breakdown
