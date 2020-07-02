# map program views #
import os
import io
from io import BytesIO
import pdfkit
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents, Drugs, Map, MapApplication
from supereasypa.map.forms import AddMap, AddNotesMap
from werkzeug.utils import secure_filename
from datetime import date, time
from datetime import datetime, timedelta
from pytz import timezone

UPLOAD_FOLDER = 'supereasypa/static/user_uploads/map'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Users\matth\source\repos\supereasypa\supereasypa\wkhtmltopdf\bin\wkhtmltopdf.exe")
map = Blueprint('map', __name__)


@map.route('/addmap', methods=['GET', 'POST'])
@login_required
def addmap():
    form = AddMap()
    # user_logged = current_user.client_id
    map = ''
    select_drug = ''
    name_of_selected = ''
    page = request.args.get('page', 1, type=int)
    all_drugs = Drugs.query.order_by(Drugs.name.asc()).paginate(page=page, per_page=500)
    drug_name_pull = ''
    drug_name = ''

    if form.validate_on_submit():
        select_drug = Drugs.query.filter_by(id=form.drug_id.data).first()
        name_of_selected = select_drug.name
        map = Map(name=form.name.data,
                  manufacturer=form.manufacturer.data,
                  income_threshold=form.income_threshold.data,
                  required_docs=form.required_docs.data,
                  drug_id=form.drug_id.data,
                  drug_name=name_of_selected,
                  client_id=current_user.client_id,
                  household_size=form.household_size.data,
                  fax=form.fax.data,
                  phone=form.phone.data,
                  public='Y')

        db.session.add(map)
        db.session.commit()
        return redirect(url_for('map.allmap'))

    return render_template('map/addmap.html', form=form, map=map, all_drugs=all_drugs, select_drug=select_drug,
                           name_of_selected=name_of_selected, drug_name_pull=drug_name_pull)


@map.route('/allmap', methods=['GET', 'POST'])
@login_required
def allmap():
    all_map = Map.query.order_by(Map.name.asc()).all()
    return render_template('map/all_map.html', all_map=all_map)


@map.route('/viewmap/<int:map_id>', methods=['GET', 'POST'])
@login_required
def viewmap(map_id):
    map_record = Map.query.get_or_404(map_id)
    drug_name_current = Drugs.query.filter_by(id=map_record.drug_id).first()

    total = MapApplication.query.filter_by(map_id=map_record.id).count()
    approved = MapApplication.query.filter_by(map_id=map_record.id, status='Approved').count()
    denied = MapApplication.query.filter_by(map_id=map_record.id, status='Denied').count()
    pending = MapApplication.query.filter_by(map_id=map_record.id, status='Pending').count()

    # all applications by status

    all_approved = MapApplication.query.filter_by(map_id=map_record.id, status='Approved').all()
    all_denied = MapApplication.query.filter_by(map_id=map_record.id, status='Denied').all()
    all_pending = MapApplication.query.filter_by(map_id=map_record.id, status='Pending').all()

    form_notes = AddNotesMap()

    # add notes ####
    if form_notes.validate_on_submit():
        notes = Notes(body=form_notes.body.data,
                      client_id=current_user.client_id,
                      created_by=current_user.username,
                      pt_id=0,
                      ins_id=0,
                      md_id=0,
                      pa_id=0,
                      map_id=map_record.id,
                      mapapp_id=0)

        db.session.add(notes)
        db.session.commit()
        return redirect(url_for('map.viewmap', map_id=map_record.id))

    # return notes into page in notes section ####

    notes_map = Notes.query.filter_by(map_id=map_record.id).order_by(Notes.id.desc()).all()

    return render_template('map/map.html', map_record=map_record, total=total, approved=approved, pending=pending,
                           denied=denied,
                           all_denied=all_denied, all_approved=all_approved, all_pending=all_pending,
                           drug_name_current=drug_name_current,form_notes=form_notes, notes_map=notes_map)


# update and delete map

@map.route("/updatemap/<int:map_id>", methods=['GET', 'POST'])
@login_required
def update(map_id):
    form = AddMap()
    user_logged = current_user.client_id
    map_record = Map.query.get_or_404(map_id)
    drug_name_pull = Drugs.query.filter_by(id=map_record.drug_id).first()
    drug_name = f"Current: {drug_name_pull}"
    page = request.args.get('page', 1, type=int)
    all_drugs = Drugs.query.order_by(Drugs.name.asc()).paginate(page=page, per_page=500)

    if form.validate_on_submit():

        map_record.name = form.name.data
        map_record.phone = form.phone.data
        map_record.fax = form.fax.data
        map_record.manufacturer = form.manufacturer.data
        map_record.income_threshold = form.income_threshold.data
        map_record.required_docs = form.required_docs.data
        map_record.drug_id = form.drug_id.data
        map_record.household_size = form.household_size.data
        #  map_record.drug_name = Drugs.query.filter_by(id=form.drug_id.data).first()
        db.session.commit()
        return redirect(url_for('map.viewmap', map_id=map_record.id))
    elif request.method == 'GET':
        form.name.data = map_record.name
        form.phone.data = map_record.phone
        form.fax.data = map_record.fax
        form.manufacturer.data = map_record.manufacturer
        form.income_threshold.data = map_record.income_threshold
        form.required_docs.data = map_record.required_docs
        form.drug_id.data = map_record.drug_id
        form.household_size.data = map_record.household_size

    return render_template('map/addmap.html', title='Update MAP',
                           drug_name=drug_name, drug_name_pull=drug_name_pull, form=form, all_drugs=all_drugs)


@map.route("/deletemap/<int:map_id>", methods=['POST'])
@login_required
def delete_map(map_id):
    map_record = Map.query.get_or_404(map_id)
    db.session.delete(map_record)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('map.allmap'))
