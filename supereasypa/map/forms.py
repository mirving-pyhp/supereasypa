# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from wtforms.fields.html5 import DateField, IntegerField
# User Based Imports
from flask_login import current_user
from supereasypa.models import Prescriber


class AddMap(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    income_threshold = IntegerField('Income Threshold', validators=[DataRequired()])
    required_docs = StringField('Required Docs', validators=[DataRequired()])
    drug_id = IntegerField('Income Threshold', validators=[DataRequired()])
    household_size = IntegerField('Household Size', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    fax = StringField('Fax', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddNotesMap(FlaskForm):
    body = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')