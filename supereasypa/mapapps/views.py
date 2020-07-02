# map applications
import os
import io
from io import BytesIO
import pdfkit
from operator import or_
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents, Drugs, Map, \
    MapApplication
from supereasypa.mapapps.forms import AddMapApp
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
mapapp = Blueprint('mapapp', __name__)


@mapapp.route('/addmapapp', methods=['GET', 'POST'])
@login_required
def addmapapp():
    form = AddMapApp()
    # user_logged = current_user.client_id
    mapapp = ''
    select_drug = ''
    name_of_selected = ''
    page = request.args.get('page', 1, type=int)
    user_logged = current_user.client_id
    all_maps = Map.query.filter(or_(Map.client_id == current_user.client_id, Map.public == 'Y')).order_by(
        Map.name.asc()).paginate(page=page, per_page=500)
    all_drugs = Drugs.query.filter(or_(Drugs.client_id == current_user.client_id, Drugs.public == 'Y')).order_by(
        Drugs.name.asc()).paginate(page=page, per_page=500)
    allpts = Patient.query.filter_by(client_id=user_logged).all()
    all_users = User.query.filter_by(client_id=user_logged).all()
    all_drugs = Drugs.query.order_by(Drugs.name.asc()).all()
    allmd = Prescriber.query.filter_by(client_id=user_logged)
    allins = Insurance.query.filter_by(client_id=user_logged)
    if form.validate_on_submit():
        select_drug = Drugs.query.filter_by(id=form.drug_id.data).first()
        name_of_selected = select_drug.name
        select_ins = Insurance.query.filter_by(id=form.ins_id.data).first()
        name_of_selected_ins = select_ins.name
        select_map = Map.query.filter_by(id=form.map_id.data).first()
        name_of_selected_map = select_map.name
        # pull patient information
        select_patient = Patient.query.filter_by(id=form.pt_id.data).first()
        insurance_id = select_patient.member_id
        fname = select_patient.fname
        lname = select_patient.lname
        dob = select_patient.dob.strftime('%m-%d-%Y')
        name_of_selected_patient = f"ID: {insurance_id} | {fname} {lname} | DOB:{dob}"
        mapapp = MapApplication(map_id=form.map_id.data,
                                map_name=name_of_selected_map,
                                user_id=form.user_id.data,
                                ins_id=form.ins_id.data,
                                phone=form.phone.data,
                                fax=form.fax.data,
                                client_id=current_user.client_id,
                                init_notes=form.init_notes.data,
                                ins_name=name_of_selected_ins,
                                pt_id=form.pt_id.data,
                                pt_info=name_of_selected_patient,
                                drug_id=form.drug_id.data,
                                drug_name=name_of_selected,
                                md_id=form.md_id.data,
                                status=form.status.data)

        db.session.add(mapapp)
        db.session.commit()
        return redirect(url_for('mapapp.allmapapps'))

    return render_template('mapapp/addmapapp.html', form=form, all_drugs=all_drugs, select_drug=select_drug,
                           name_of_selected=name_of_selected, all_maps=all_maps, allpts=allpts, all_users=all_users,
                           allmd=allmd, allins=allins)


@mapapp.route('/allmapapps', methods=['GET', 'POST'])
@login_required
def allmapapps():
    all_mapapp = MapApplication.query.filter_by(client_id=current_user.client_id).order_by(
        MapApplication.id.asc()).all()
    return render_template('mapapp/all_mappapps.html', all_mapapp=all_mapapp)


@mapapp.route('/viewmapapp/<int:mapapp_id>', methods=['GET', 'POST'])
@login_required
def viewmapapp(mapapp_id):
    mapapp_record = MapApplication.query.get_or_404(mapapp_id)
    status = mapapp_record.status
    if status == 'Approved':
        icon = 'fa-check'
        border_style = 'border-left-success'
        header_font = 'text-success'
    if status == 'Denied':
        icon =  'fa-times'
        border_style = 'border-left-danger'
        header_font = 'text-danger'
    if status == 'Pending':
        icon = 'fa-clock'
        border_style = 'border-left-warning'
        header_font = 'text-warning'
    md = Prescriber.query.filter_by(id=mapapp_record.md_id).first()
    md_info = f"{md.fname} {md.lname} NPI:{md.npi}"
    return render_template('mapapp/mappapp.html', mapapp_record=mapapp_record, md_info=md_info,
                           icon=icon,border_style=border_style,header_font=header_font)
