###Patient Form###

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from supereasypa.models import Patient, Notes
from wtforms.fields.html5 import DateField, IntegerField
from werkzeug.utils import secure_filename




class AddPatient(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    ins_id = IntegerField('Insurance')
    phone = StringField('Phone')
    dob = DateField('DOB', format='%Y-%m-%d', validators=[DataRequired()])
    ins_eff_date = DateField('Effective Date', format='%Y-%m-%d', validators=[DataRequired()])
    ins_term_date = DateField('Term Date', format='%Y-%m-%d', validators=[DataRequired()])
    member_id = StringField('Member ID', validators=[DataRequired()])

    allergies = StringField('Allergies', validators=[DataRequired()])
    height = StringField('Height')
    weight = IntegerField('Weight')
    disease_states = StringField('Disease State(s)')
    address = StringField('Address')
    state = StringField('State')
    city = StringField('City')
    zip = IntegerField('Zip')

    submit = SubmitField('Submit')


class AddNotesPatient(FlaskForm):
    body = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddDocsPatient(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File')
    submit = SubmitField('Upload')


class AddPAFormPatient(FlaskForm):
    drug = StringField('Drug', validators=[DataRequired()])

    insurance_id = IntegerField()
    prescriber_id = IntegerField()
    patient_id = IntegerField()
    user_id = IntegerField()
    status = SelectField(
        'Status', validators=[DataRequired()],
        choices=[('Approved', 'Approved'), ('Denied', 'Denied'), ('Pending', 'Pending'), ('Appeal', 'Appeal'),
                 ('2nd Appeal', '2nd Appeal'), ('3rd Party Review', '3rd Party Review')]
    )
    eff_date = DateField('Effective Date', validators=[DataRequired()])
    term_date = DateField('Termination Date:', validators=[DataRequired()])
    client_id = IntegerField('Client ID')
    notes_init = TextAreaField(u'Notes')
    submit = SubmitField('Submit')
