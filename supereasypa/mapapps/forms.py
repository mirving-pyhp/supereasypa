# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from wtforms.fields.html5 import DateField, IntegerField


class AddMapApp(FlaskForm):
    map_id = IntegerField('MAP', validators=[DataRequired()])
    pt_id = IntegerField('Patient', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    fax = StringField('Fax', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    user_id = IntegerField('Assigned To', validators=[DataRequired()])
    ins_id = IntegerField('Insurance', validators=[DataRequired()])
    drug_id = IntegerField('Drug', validators=[DataRequired()])
    md_id = IntegerField('Prescriber', validators=[DataRequired()])
    init_notes = StringField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')