# documents
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from supereasypa.models import Patient, Notes
from wtforms.fields.html5 import DateField, IntegerField
from werkzeug.utils import secure_filename



class AddDocumentsFormulary(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File')
    submit = SubmitField('Upload')