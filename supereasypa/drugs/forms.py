### drugs forms ###
# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from wtforms.fields.html5 import DateField, IntegerField
# User Based Imports
from flask_login import current_user
from supereasypa.models import Prescriber


class AddDrug(FlaskForm):
    name = StringField('Drug', validators=[DataRequired()])
    cost = StringField('Cost Per Fill', validators=[DataRequired()])
    drug_class = StringField('Drug Class', validators=[DataRequired()])
    strength = StringField('Strength', validators=[DataRequired()])
    dosage_form = StringField('Strength', validators=[DataRequired()])
    measurement = StringField('Unit of Measurement', validators=[DataRequired()])

    submit = SubmitField('Submit')
