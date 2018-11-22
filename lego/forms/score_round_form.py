# -----------------------------------------------------------------------------
# The form used for scoring the active round.
#
# Needs to be updated each year with the new tasks.
# -----------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import RadioField, BooleanField, SelectField, IntegerField, HiddenField
from wtforms.compat import text_type
from wtforms.validators import InputRequired, Optional


# A boolean field (checkbox) with an associated non-bool value (e.g. an int) 
# class CheckboxValueField(BooleanField):
#     def __init__(self, label=None, validators=None, false_values=None, value=None, **kwargs):
#         super(CheckboxValueField, self).__init__(label, validators, false_values, **kwargs)
#         self.value = value


#     def _value(self):
#         if self.raw_data:
#             return text_type(self.raw_data[0])

#         if self.value:
#             return self.value

#         return 'y'
class BonusField(BooleanField):
    def __init__(self, label=None, validators=None, false_values=None, value=None, **kwargs):
        super(BonusField, self).__init__(label, validators, false_values, **kwargs)
        self.value = value


    def _value(self):
        if self.raw_data:
            return text_type(self.raw_data[0])

        if self.value:
            return self.value

        return 'y'

# used to combine several checkbox field values into one object
class CompleteField():
    def __init__(self, components, label):
        self.components = components
        self.data = 0
        for component in components:
            # if the checkbox is a scoring one add its value to the total
            if isinstance(component.value, int):
                self.data += component.value
            # if its an essential condition that wasn't met, set it to 0
            elif isinstance(component.value, bool):
                if component.value == False:
                    self.data = 0
                    break
            
        self.label = label


class ScoreRoundForm(FlaskForm):
    m01_title = 'M01 - Space Travel'
    m02_title = 'M02 - Solar Panel Array'
    m03_title = 'M03 - 3D Printing'
    m04_title = 'M04 - Crater Crossing'
    m05_title = 'M05 - Extraction'
    m06_title = 'M06 - Space Station Modules'
    m07_title = 'M07 - Space Walk Emergency'
    m08_title = 'M08 - Aerobic Exercise'
    m09_title = 'M09 - Strength Exercise'
    m10_title = 'M10 - Food Production'
    m11_title = 'M11 - Escape Velocity'
    m12_title = 'M12 - Satellite Orbits'
    m13_title = 'M13 - Observatory'
    m14_title = 'M14 - Meteoroid Deflection'
    m15_title = 'M15 - Landing Touch-Down'
    penalties_title = 'Penalties'

    # fields
    team = SelectField('Team:', validators=[InputRequired(message='Please select a team.')])
    yellow_card = BooleanField('Yellow card')
    confirm = HiddenField(default='0')
    score = IntegerField('Total score', validators=[Optional()])

    # example before

    # and after desired changes
    m01_label = 'Send Payload rockets (carts) down the Space Travel Ramp.'
    m01_independent = BonusField('Cart was independent by the time it made the first track connection', value='true')
    m01_crew = BonusField('Crew Payload', value='10')
    m01_supply = BonusField('Supply payload', value='14')
    m01_vehicle = BonusField('Vehicle payload', value='22')


    m02_complete = RadioField('Solar Panels need to be angled toward or away from you, '
                              'depending on strategy and conditions.',
                              choices=[('18', 'Your Solar Panel is Angled toward the other team’s field'),
                                       ('22', 'Both Solar Panels are angled towards the same field')],
                               validators=[Optional()])

    # m03_complete = SelectField('The Regolith Core must be placed into the 3D Printer, '
    #                           'the ejected 2x4 Brick can be delivered for more points.',
    #                           choices=[('18', '2x4 Brick completely ejected from the printer by placing a Regolith Core Sample into it'),
    #                                    ('4', 'Brick completely in Northeast Planet Area ')],
    #                           validators=[Optional()])

    m03_label = 'The Regolith Core must be placed into the 3D Printer, the ejected 2x4 Brick can be delivered for more points.'
    m03_ejected = BonusField('2x4 Brick completely ejected from the printer by placing a Regolith Core Sample into it', value=18)
    m03_planet_area = BonusField('Brick completely in Northeast Planet Area ', value=4)

    # m04_complete = SelectField('The Robot or whatever agent-craft it sends out needs to cross '
    #                           'the Craters Model, by driving directly over it.',
    #                           choices=[('0', 'Robot or Agent crossed completely east to west between the towers'),
    #                                    ('20', 'Gate completely flattened')], # TODO both must be selected to score points
    #                           validators=[Optional()])

    m04_label = 'The Robot or whatever agent-craft it sends out needs to cross the Craters Model, by driving directly over it.'
    m04_crossed = BonusField('Robot or Agent crossed completely east to west between the towers')
    m04_gate = BonusField('Gate completely flattened', value='20')

    # m05_complete = SelectField('The Robot must get all the Core Samples out of the Core Site.',
    #                           choices=[('16', 'All samples moved no longer touching Core Site Model Axis'),
    #                             # TODO add logic so only one of the below choices are available
    #                                    ('12', 'Gas Core Sample touching the mat and completely in the Lander’s Target Circle'), # Option 1
    #                                    ('10', 'Gas Core Sample completely in Base'), # Option 2
    #                                    ('12', 'Water Core Sample supported only by the Food Growth Chamber')
    #                                    ],
    #                           validators=[Optional()])

    m05_label = 'The Robot must get all the Core Samples out of the Core Site.'
    m05_all_samples = BonusField('All samples moved no longer touching Core Site Model Axis', value=16)
    m05_gas_core_touching = BonusField('Gas Core Sample touching the mat and completely in the Lander’s Target Circle', value=12)
    m05_gas_core_completely = BonusField('Gas Core Sample completely in Base', value=12)
    m05_water_core = BonusField('Water Core Sample supported only by the Food Growth Chamber', value=12)

    # m06_complete = SelectField('The Robot needs to remove and insert Modules among the '
    #                           'Habitation Hub port holes.',
    #                           choices=[('16', 'Cone Module completely in base'),
    #                                    ('16', 'Tube Module in Habitation Hub Port West Side, touching nothing but the Habitation Hub'),
    #                                    ('14', 'Docking Module in Habitation Hub Port East Side, touching nothing but the Habitation Hub')],
    #                           validators=[Optional()])

    m06_label = 'The Robot needs to remove and insert Modules among the Habitation Hub port holes.'
    m06_completely = BonusField('Cone Module completely in base', value=16)
    m06_tube = BonusField('Tube Module in Habitation Hub Port West Side, touching nothing but the Habitation Hub', value=16)
    m06_docking = BonusField('Docking Module in Habitation Hub Port East Side, touching nothing but the Habitation Hub', value=14)

    m07_complete = RadioField('The Robot needs to get Gerhard’s body into the Airlock Chamber.',
                              choices=[('0', 'Gerhard’s body not in airlock chamber'),
                                       ('18', 'Gerhard’s body partially in airlock chamber'),
                                       ('22', 'Gerhard’s body completely in airlock chamber')],
                              default='0',
                              validators=[InputRequired('Please make a choice for M07')])

    m08_complete = SelectField('The Robot needs to repeatedly move one or both of the '
                               'Exercise Machine’s Handle Assemblies to make the Pointer advance.',
                                        # TODO the first choice must be checked for the others to count
                                        # Make this a checkbox
                               choices=[('0', 'Exercise Machine Pointer advanced only by moving one or both of the Handle Assemblies'),
                                        # Make these an unlocked radio choice if above checkbox is ticked
                                        ('18', 'Pointer completely in gray, or partly covering either of gray’s end-borders'),
                                        ('20', 'Pointer completely in white'),
                                       ('22', 'Pointer completely in orange, or partly covering either of orange’s end-borders')],
                               validators=[Optional()])

    m09_complete = RadioField('The Robot lifted the Strength Bar to a scoring height so that the tooth-strip’s'
                              ' 4th hole comes at least partly into view?',
                               choices=[('16', 'Yes'),
                                        ('0', 'No')],
                               default='0',
                               validators=[InputRequired('Please make a choice for M09')])

    m10_complete = RadioField('Food Growth Chamber’s colors spun, by moving the Push Bar,'
                              ' so the gray weight is DROPPED after green, but before tan?',
                              choices=[('16', 'Yes'),
                                       ('0', 'No')],
                              default='0',
                              validators=[InputRequired('Please make a choice for M10')])

    m11_complete = RadioField('The Robot hit the Strike Pad hard enough to '
                               'keep the spacecraft from dropping back down?',
                               choices=[('24', 'Yes'),
                                       ('0', 'No')],
                               default='0',
                               validators=[InputRequired('Please make a choice for M11')])

    m12_complete = RadioField('The Robot needs to move one or more Satellites to the Outer Orbit.',
                              choices=[('0', 'No satellites moved into orbit'),
                                       ('8', '1 moved between the two lines of the Outer Orbit'),
                                       ('16', '2 moved between the two lines of the Outer Orbit'),
                                       ('24', '3 moved between the two lines of the Outer Orbit')],
                              default='0',
                              validators=[InputRequired('Please make a choice for M12')])

    m13_complete = RadioField('Rotate the Observatory to a precise direction.',
                              choices=[('0', 'Tip not in any coloured section'),
                                       ('16', 'Tip completely in gray, or partly covering either of gray’s end-borders'),
                                       ('18', 'Tip completely in white'),
                                       ('20', 'Tip completely in orange, or partly covering either of orange’s end-borders')],
                              default='0',
                              validators=[InputRequired('Please make a choice for M13')])

    m14_complete = SelectField('Send Meteoroids over the Free-Line to touch the mat in the Meteoroid Catcher.',
                                        # TODO this conditional
                               choices=[('True', 'Meteoroids hit/released while clearly and completely west of free line'),
                                        ('True', 'Meteoroids clearly independent whilst west of the free-line'),
                                        # TODO two dropdowns for side and center
                                        # validate with side + centre <= 2
                                        ('12', 'One meteoroid in the Center Section'),
                                        ('24', 'Two meteoroids in the Center Section'),
                                        ('8', 'One in Side section'),
                                        ('16', 'Both in Side section(s)'),
                                        ('20', 'Side and Center')],
                               default='0',
                               validators=[InputRequired('Please make a choice for M14')])

    m15_complete = RadioField('Get the Lander to one of its targets intact, or at least '
                              'get it to Base.',
                              choices=[('0', 'Failed to get lander to target or base'),
                                       ('16', 'Both parts of the Lander completely into Base'),
                                       ('20', 'Lander  intact, touching the Mat, and completely in the Northeast Planet Area'),
                                       ('22', 'Lander intact, touching the Mat, and completely in its Target Circle')],
                              default='0',
                              validators=[InputRequired('Please make a choice for M15')])


    penalties_chosen = SelectField('Number of penalties',
                             choices=[('0', '0'),
                                      ('3', '1 (-3 points)'),
                                      ('6', '2 (-6 points)'),
                                      ('9', '3 (-9 points)'),
                                      ('12', '4 (-12 points)'),
                                      ('15', '5 (-15 points)'),
                                      ('18', '6 (-18 points)')],
                             validators=[Optional()])

    def points_scored(self) -> (int, str):
        """Calculate the points scored for this round."""
        score_breakdown = {
            'm02_score': int(self.m02_complete.data),
            'm03_score': (self.m03_ejected.data * self.m03_ejected.value) + (self.m03_planet_area.data * self.m03_planet_area.value),
            'm04_score': self.m04_crossed.data * self.m04_gate.data * self.m04_gate.value,
            'm05_score': (self.m05_all_samples.data * self.m05_all_samples.value) + (self.m05_water_core.data * self.m05_water_core.value) + (self.m05_gas_core_completely.data * self.m05_gas_core_completely.value) + (self.m05_gas_core_touching.data * self.m05_gas_core_touching.value),
            'm06_score': (self.m06_completely.data * self.m06_completely.value) + (self.m06_tube.data * self.m06_tube.value) + (self.m06_docking.data * self.m06_docking.value),
            'm07_score': int(self.m07_complete.data),
            'm08_score': int(self.m08_complete.data),
            'm09_score': int(self.m09_complete.data),
            'm10_score': int(self.m10_complete.data),
            'm11_score': int(self.m11_complete.data),
            'm12_score': int(self.m12_complete.data),
            'm13_score': int(self.m13_complete.data),
            # 'm14_score': int(self.m14_complete.data),
            'm15_score': int(self.m15_complete.data),
            'penalties': -int(self.penalties_chosen.data)
        }

        score = sum(score_breakdown.values()) if sum(score_breakdown.values()) else 0
        score_breakdown = str(score_breakdown)
        return score, score_breakdown
