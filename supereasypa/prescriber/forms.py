### prescriber form ###
# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from wtforms.fields.html5 import DateField, IntegerField
# User Based Imports
from flask_login import current_user
from supereasypa.models import Prescriber


class AddPrescriber(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address')
    city = StringField('City')
    state = StringField('State')
    zip = IntegerField('Zip')
    npi = IntegerField('NPI', validators=[DataRequired()])
    dea = StringField('DEA')
    phone = StringField('Phone')
    fax = StringField('Fax')
    alt_phone = StringField('Alt Phone')
    alt_fax = StringField('Alt Fax')

    submit = SubmitField('Submit')

 #   def validate_npi(self, field):

 #       if Prescriber.query.filter_by(npi=field.data).first():
  #          raise ValidationError('This NPI already exists.')
class AddNotesPrescriber(FlaskForm):
    body = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')