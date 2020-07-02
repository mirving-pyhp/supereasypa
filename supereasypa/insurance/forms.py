###insurance forms###
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from supereasypa.models import Insurance

class AddInsurance(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])   
    phone = StringField('Phone', validators=[DataRequired()])
    fax = StringField('Fax', validators=[DataRequired()])
    alt_phone = StringField('Alt Phone')
    alt_fax = StringField('Alt Fax')
    bin = IntegerField('BIN')
    pcn = StringField('PCN')
    group = StringField('Group')
    client_id=IntegerField('Client ID')

    
    submit = SubmitField('Submit')

class AddDocsInsurance(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File')
    submit = SubmitField('Upload')


class AddNotesInsurance(FlaskForm):
    body = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')