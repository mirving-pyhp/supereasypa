###Client Form###

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from supereasypa.models import Patient
from wtforms.fields.html5 import DateField, IntegerField
    
     
class AddClient(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone')
    fax = StringField('Fax')
    sub_type = SelectField(
        'Sub Type',validators=[DataRequired()],
        choices=[('1', 'PA Pro'), ('2', 'Premium'), ('3', 'Executive')]
    )

    
    submit = SubmitField('Submit')
