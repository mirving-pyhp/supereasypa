### prior authorization forms ###
# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import DateField, IntegerField


# User Based Imports
from flask_login import current_user
from supereasypa.models import PriorAuth


class AddPAForm(FlaskForm):
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
    client_id = IntegerField('Client ID')
    notes_init = TextAreaField(u'Notes')
    eff_date = DateField('Effective Date', validators=[DataRequired()])
    term_date = DateField('Termination Date:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddNotesPriorAuth(FlaskForm):
    body = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddDocsPriorAuth(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File')
    submit = SubmitField('Upload')