# prescriber views #
import os
import io
from io import BytesIO
import pdfkit
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents
from supereasypa.prescriber.forms import AddPrescriber, AddNotesPrescriber
from werkzeug.utils import secure_filename
from datetime import date, time
from datetime import datetime, timedelta
from pytz import timezone

UPLOAD_FOLDER = 'supereasypa/static/user_uploads/patients'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Users\matth\source\repos\supereasypa\supereasypa\wkhtmltopdf\bin\wkhtmltopdf.exe")

prescriber = Blueprint('prescriber', __name__)


@prescriber.route('/addprescriber', methods=['GET', 'POST'])
@login_required
def addmd():
    form = AddPrescriber()
    user_logged = current_user.client_id
    md = ''
    if form.validate_on_submit():
        md = Prescriber(fname=form.fname.data,
                        lname=form.lname.data,
                        phone=form.phone.data,
                        fax=form.fax.data,
                        alt_phone=form.alt_phone.data,
                        alt_fax=form.alt_fax.data,
                        dea=form.dea.data,
                        npi=form.npi.data,
                        address=form.address.data,
                        state=form.state.data,
                        city=form.city.data,
                        zip=form.zip.data,
                        client_id=user_logged)

        db.session.add(md)
        db.session.commit()
        return redirect(url_for('prescriber.allprescribers'))
    else:
        print(user_logged)
        print(form.errors)

    return render_template('prescriber/addprescriber.html', form=form, md=md)

@prescriber.route('/allprescribers', methods=['GET', 'POST'])
@login_required
def allprescribers():
    user_logged = current_user.client_id
    page = request.args.get('page', 1, type=int)
    prescribers = Prescriber.query.filter_by(client_id=user_logged).paginate(page=page,
                                                                          per_page=30000)  ###this works perfectly
    return render_template('prescriber/all_md.html', prescribers=prescribers)

### individual prescriber record ###
@prescriber.route('/prescriber/<int:prescriber_id>', methods=['GET', 'POST'])
@login_required
def viewprescriber(prescriber_id):
    prescriber_record = Prescriber.query.get_or_404(prescriber_id)
    user_logged = current_user.client_id  ### curent client id ###

    ### pull insurance name ###
    md_id = prescriber_record.id

    prescriber_name_pull = Prescriber.query.filter_by(id=md_id).first()

    prescriber_name = prescriber_name_pull

    ### pulls drug count ###

    ### number of drugs per PA ###

    drug_counts = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id, prescriber_id=md_id). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(5). \
        all()

    for drug_name, count in drug_counts:
        med_name = drug_name
        count_drug = count
        list_of_drug = [drug_name, count]

    ### pull prior auth record ###

    prior_auths = PriorAuth.query.filter_by(prescriber_id=md_id).all()
    all_pts = PriorAuth.query.filter_by(prescriber_id=md_id).distinct().count()

    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id, prescriber_id=md_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id, prescriber_id=md_id).count()
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id, prescriber_id=md_id).count()

    total = allapproved + alldenied + allpending

    if total > 0:
        approval_percentage = round(allapproved / total * 100, 2)
        denial_percentage = round(alldenied / total * 100, 2)
    # pending_percentage = round(allpending / total * 100,2)
    # paperpatient = round(total / all_pts,2)
    else:
        approval_percentage = 0
        denial_percentage = 0
        pending_percentage = 0
        paperpatient = 0

    form_notes = AddNotesPrescriber()

    # add notes ####
    if form_notes.validate_on_submit():
        notes = Notes(body=form_notes.body.data,
                      client_id=current_user.client_id,
                      created_by=current_user.username,
                      pt_id=0,
                      ins_id=0,
                      md_id=md_id,
                      pa_id=0)

        db.session.add(notes)
        db.session.commit()
        return redirect(url_for('prescriber.viewprescriber', prescriber_id=md_id))

    # return notes into page in notes section ####

    notes_pa = Notes.query.filter_by(md_id=md_id).order_by(Notes.id.desc()).all()
    # alternative faxes

    if prescriber_record.alt_fax == '':
        alt_fax_num = ''
    else:
        alt_fax_num = f"OR {prescriber_record.alt_fax}"

    if prescriber_record.alt_phone == '':
        alt_phone_num = ''
    else:
        alt_phone_num = f"OR {prescriber_record.alt_phone}"

    return render_template('prescriber/prescriber.html',
                           user_logged=user_logged, prescriber_name=prescriber_name,
                           prescriber_name_pull=prescriber_name_pull, prior_auths=prior_auths,
                           allpending=allpending, alldenied=alldenied, allapproved=allapproved,
                           prescriber_record=prescriber_record, all_pts=all_pts, approval_percentage=approval_percentage,
                           denial_percentage=denial_percentage, drug_counts=drug_counts, notes_pa=notes_pa,
                           form_notes=form_notes, alt_fax_num=alt_fax_num, alt_phone_num=alt_phone_num)

@prescriber.route("/updateprescriber/<int:prescriber_id>", methods=['GET', 'POST'])
@login_required
def update(prescriber_id):
    form = AddPrescriber()
    user_logged = current_user.client_id
    prescriber = Prescriber.query.get_or_404(prescriber_id)
    all_users = User.query.filter_by(client_id=user_logged).all()


    if form.validate_on_submit():

        ### commit form data ###
        prescriber.fname = form.fname.data
        prescriber.lname = form.lname.data
        prescriber.phone = form.phone.data
        prescriber.alt_phone = form.alt_phone.data
        prescriber.fax = form.fax.data
        prescriber.alt_fax = form.alt_fax.data
        prescriber.npi = form.npi.data
        prescriber.dea = form.dea.data
        prescriber.address = form.address.data
        prescriber.state = form.state.data
        prescriber.city = form.city.data
        prescriber.zip = form.zip.data


        db.session.commit()
        return redirect(url_for('prescriber.viewprescriber', prescriber_id=prescriber.id))
    elif request.method == 'GET':
        form.fname.data = prescriber.fname
        form.lname.data = prescriber.lname
        form.phone.data = prescriber.phone
        form.alt_phone.data = prescriber.alt_phone
        form.fax.data = prescriber.fax
        form.alt_fax.data = prescriber.alt_fax
        form.npi.data = prescriber.npi
        form.dea.data = prescriber.dea
        form.address.data = prescriber.address
        form.state.data = prescriber.state
        form.city.data = prescriber.city
        form.zip.data = prescriber.zip

    return render_template('prescriber/addprescriber.html', title='Update Prescriber',
                           form=form, all_users=all_users, prescriber=prescriber
                           )

@prescriber.route("/deleteprescriber/<int:prescriber_id>", methods=['POST'])
@login_required
def delete_prescriber(prescriber_id):
    prescriber = Prescriber.query.get_or_404(prescriber_id)
    db.session.delete(prescriber)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('prescriber.allprescribers'))