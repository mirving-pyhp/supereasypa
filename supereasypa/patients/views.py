### patient ###
import os
import io
from io import BytesIO
import pdfkit
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents, Drugs, MapApplication
from supereasypa.patients.forms import AddPatient, AddNotesPatient, AddDocsPatient, AddPAFormPatient
from werkzeug.utils import secure_filename
from datetime import date, time
from datetime import datetime, timedelta
from pytz import timezone

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Users\matth\source\repos\supereasypa\supereasypa\wkhtmltopdf\bin\wkhtmltopdf.exe")

patient = Blueprint('patient', __name__)


@patient.route('/addpatient', methods=['GET', 'POST'])
@login_required
def addpatient():
    form = AddPatient()
    user_logged = current_user.client_id
    allins = Insurance.query.filter_by(client_id=user_logged)
    patient = ''

    if form.validate_on_submit():
        patient = Patient(fname=form.fname.data,
                          lname=form.lname.data,
                          ins_id=form.ins_id.data,
                          phone=form.phone.data,
                          dob=form.dob.data,
                          member_id=form.member_id.data,
                          ins_eff_date=form.ins_eff_date.data,
                          ins_term_date=form.ins_term_date.data,
                          allergies=form.allergies.data,
                          height=form.height.data,
                          weight=form.weight.data,
                          disease_states=form.disease_states.data,
                          address=form.address.data,
                          state=form.state.data,
                          city=form.city.data,
                          zip=form.zip.data,

                          client_id=user_logged)

        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('patient.allpatients'))

    return render_template('patient/addpatient.html', form=form, allins=allins, patient=patient)


@patient.route('/allpatients', methods=['GET', 'POST'])
@login_required
def allpatients():
    page = request.args.get('page', 1, type=int)
    user_logged = current_user.client_id
    allpts = Patient.query.filter_by(client_id=user_logged).paginate(page=page, per_page=100)

    return render_template('patient/all_patients.html', allpts=allpts, user_logged=user_logged)


@patient.route('/printingthis', methods=['GET', 'POST'])
@login_required
def printing():
    allptsct = Patient.query.filter_by(client_id=current_user.client_id).count()
    # prior auth stats #
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id).count()
    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id).count()
    page = request.args.get('page', 1, type=int)
    user_logged = current_user.client_id
    allpts = Patient.query.filter_by(client_id=user_logged).paginate(page=page, per_page=100)
    today = date.today().strftime("%m/%d/%Y")
    print_html = render_template('reports/test-print.html', allpts=allpts, user_logged=user_logged, page=page, today=today,
                                 allapproved=allapproved, alldenied=alldenied, allpending=allpending, allptsct=allptsct)

    # Convert the HTML to PDF, as target filename give 'False'
    pdf = pdfkit.from_string(print_html, False, configuration=config)

    # Convert the bytes to a file(like)
    file = io.BytesIO(pdf)

    filename = f"Patient Report.pdf"

    # Output to the browser
    return send_file(file,
                     attachment_filename=filename,
                     mimetype='application/pdf',
                     # Give this argument to let the user stay on the current page
                     as_attachment=True,
                     # Set a low cache timeout
                     cache_timeout=-1)


@patient.route('/printptpalist/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def printing_pa_list(patient_id):
    patient_record = Patient.query.get_or_404(patient_id)
    pt_id = patient_record.id
    allptsct = Patient.query.filter_by(client_id=current_user.client_id).count()
    prior_auths = PriorAuth.query.filter_by(patient_id=pt_id).all()
    # prior auth stats #
    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id, patient_id=pt_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id, patient_id=pt_id).count()
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id,
                                            patient_id=pt_id).count()
    page = request.args.get('page', 1, type=int)
    user_logged = current_user.client_id
    allpts = Patient.query.filter_by(client_id=user_logged).paginate(page=page, per_page=100)
    today = date.today().strftime("%m/%d/%Y")

    print_html_pa = render_template('reports/pastatus.html', allpts=allpts, user_logged=user_logged, page=page,
                                    today=today,
                                    allapproved=allapproved, alldenied=alldenied, allpending=allpending,
                                    allptsct=allptsct, patient_record=patient_record
                                    , prior_auths=prior_auths, pt_id=pt_id)

    # Convert the HTML to PDF, as target filename give 'False'
    pdf = pdfkit.from_string(print_html_pa, False, configuration=config)

    # Convert the bytes to a file(like)
    file = io.BytesIO(pdf)

    filename = f"Patient Report.pdf"

    # Output to the browser
    return send_file(file,
                     attachment_filename=filename,
                     mimetype='application/pdf',
                     # Give this argument to let the user stay on the current page
                     as_attachment=True,
                     # Set a low cache timeout
                     cache_timeout=-1)


# view individual patient record ####
@patient.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def viewpatient(patient_id):
    form_pa = AddPAFormPatient()
    patient_record = Patient.query.get_or_404(patient_id)
    user_logged = current_user.client_id  ### curent client id ###
    form = AddNotesPatient()  # quickly add a prior authorization while on a patients record #
    all_drugs = Drugs.query.order_by(Drugs.name.asc()).all() #pulls all drugs
    all_mapapp = MapApplication.query.filter_by(client_id=current_user.client_id,pt_id=patient_record.id).order_by(
        MapApplication.id.asc()).all()

    all_users = User.query.filter_by(client_id=user_logged).all()

    #pulls patient prescribers

    patient_md = PriorAuth.query.distinct().filter_by(client_id=current_user.client_id,patient_id=patient_record.id).all()


    # pull insurance name #
    ins_id = patient_record.ins_id

    insurance_name_pull = Insurance.query.filter_by(id=ins_id).first()

    insurance_name = insurance_name_pull

    # pull prior auth record #

    pt_id = patient_record.id

    prior_auths = PriorAuth.query.filter_by(patient_id=pt_id).all()

    doctors = Prescriber.query.filter_by(client_id=user_logged).all()

    doctors_counts = db.session.query(PriorAuth.prescriber_id, db.func.count()). \
        filter_by(patient_id=pt_id). \
        group_by(PriorAuth.prescriber_id). \
        order_by(PriorAuth.prescriber_id.desc()). \
        all()


    for md_name, count in doctors_counts:
        list_of_md = [md_name, count]

    md_names = Prescriber.query.filter_by(client_id=user_logged). \
        group_by(Prescriber.id). \
        order_by(Prescriber.id.desc()). \
        all()

    print(md_names, doctors_counts)



    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id, patient_id=pt_id).count()

    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id, patient_id=pt_id).count()
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id,
                                            patient_id=pt_id).count()

    # add notes ####
    if form.validate_on_submit():
        notes = Notes(body=form.body.data,
                      client_id=current_user.client_id,
                      created_by=current_user.username,
                      pt_id=pt_id,
                      ins_id=0,
                      md_id=0,
                      pa_id=0)

        db.session.add(notes)
        db.session.commit()
        return redirect(url_for('patient.viewpatient', patient_id=pt_id))

    # return notes into page in notes section ####

    notes_pt = Notes.query.filter_by(pt_id=pt_id).order_by(Notes.id.desc()).all()

    # add prior authorization for the patietn #
    ins_name = ''
    ins_named = ''
    if form_pa.validate_on_submit():
        ins_name = Insurance.query.filter_by(client_id=current_user.client_id, id=form_pa.insurance_id.data).first()
        ins_named = ins_name.name

        priorauth = PriorAuth(drug=form_pa.drug.data,
                              prescriber_id=form_pa.prescriber_id.data,
                              ins_id=form_pa.insurance_id.data,
                              ins_name=ins_named,
                              patient_id=form_pa.patient_id.data,
                              status=form_pa.status.data,
                              user_id=form_pa.user_id.data,
                              notes_init=form_pa.notes_init.data,
                              eff_date=form_pa.eff_date.data,
                              term_date=form_pa.term_date.data,
                              client_id=user_logged)

        db.session.add(priorauth)
        db.session.commit()
        return redirect(url_for('patient.viewpatient', patient_id=pt_id))
    # check to see if the patient has active coverage #
    today = date.today().strftime("%m/%d/%Y")

    current_term_date = patient_record.ins_term_date.strftime("%m/%d/%Y")
    current_eff_date = patient_record.ins_eff_date.strftime("%m/%d/%Y")

    if current_term_date < today or current_eff_date > today:
        status_coverage = 'fa fa-times'
        style = 'btn btn-danger'
        status_message = 'is not active.'
    else:
        status_coverage = 'fas fa-check'
        style = 'btn btn-success'
        status_message = 'is active.'
    # logic to notify user of expiring prior authorizations #

    auth_exp = patient_record.ins_term_date.strftime("%d")
    today_month = date.today().strftime("%d")
    testing = int(today_month) - int(auth_exp)
    if testing == 21:
        alert = 'PA is expiring in 3 weeks'
    elif testing == 14:
        alert = 'PA is expiring in 2 weeks'
    elif testing == 7:
        alert = 'PA is expiring in 1 week'

    else:
        alert = 'PA expired!'

    return render_template('patient/patient.html',
                           patient_record=patient_record, user_logged=user_logged, insurance_name=insurance_name,
                           insurance_name_pull=insurance_name_pull, prior_auths=prior_auths,
                           allpending=allpending, alldenied=alldenied, allapproved=allapproved, pt_id=pt_id, form=form,
                           notes_pt=notes_pt, form_pa=form_pa, all_users=all_users, ins_name=ins_name,
                           ins_named=ins_named, status_coverage=status_coverage, style=style, doctors=doctors,
                           doctors_counts=doctors_counts
                           , md_names=md_names, all_drugs=all_drugs, status_message=status_message,all_mapapp=all_mapapp,
                           patient_md=patient_md)


# view individual patient documents #
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@patient.route('/patientdocs/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def viewpatientdocs(patient_id):
    form = AddDocsPatient()
    patient_record = Patient.query.get_or_404(patient_id)
    user_logged = current_user.client_id  # current client id #

    pt_id = patient_record.id
    docs_module = Documents.query.filter_by(pt_id=pt_id).order_by(Documents.id.desc()).all()
    # pull prior auth record #
    # upload documents for patient, allowed file types: pdf only!!! #
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # return redirect(request.url)
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
    if form.validate_on_submit():
        # commit info to database #
        document = Documents(name=form.name.data,
                             created_by=current_user.username,
                             client_id=current_user.client_id,
                             doc_path='/static/user_uploads/patients/' + filename,
                             description=form.description.data,
                             pt_id=pt_id,
                             ins_id=0,
                             md_id=0,
                             pa_id=0,
                             public='Y')

        db.session.add(document)
        db.session.commit()

        return redirect(url_for('patient.viewpatientdocs', patient_id=pt_id))

    return render_template('documents/docs.html',
                           patient_record=patient_record, user_logged=user_logged, pt_id=pt_id, form=form,
                           docs_module=docs_module
                           )


@patient.route("/updatepatient/<int:patient_id>", methods=['GET', 'POST'])
@login_required
def update(patient_id):
    form = AddPatient()
    user_logged = current_user.client_id
    patient = Patient.query.get_or_404(patient_id)
    ### add insurance ###
    allins = Insurance.query.filter_by(client_id=user_logged)
    ### pulls related patient information ###

    insurance_name_pull = Insurance.query.filter_by(id=patient.ins_id).first()

    insurance_name = f"Current: {insurance_name_pull}"

    allpts = Patient.query.filter_by(client_id=user_logged).all()
    all_users = User.query.filter_by(client_id=user_logged).all()

    if form.validate_on_submit():

        ### insurance name ###

        ### commit form data ###
        patient.fname = form.fname.data
        patient.lname = form.lname.data
        patient.ins_id = form.ins_id.data
        patient.phone = form.phone.data
        patient.dob = form.dob.data
        patient.ins_eff_date = form.ins_eff_date.data
        patient.ins_term_date = form.ins_term_date.data
        patient.allergies = form.allergies.data
        patient.height = form.height.data
        patient.weight = form.weight.data
        patient.address = form.address.data
        patient.state = form.state.data
        patient.city = form.city.data
        patient.zip = form.zip.data
        patient.member_id = form.member_id.data

        db.session.commit()
        return redirect(url_for('patient.viewpatient', patient_id=patient.id))
    elif request.method == 'GET':
        form.fname.data = patient.fname
        form.lname.data = patient.lname
        form.ins_id.data = patient.ins_id
        form.phone.data = patient.phone
        form.dob.data = patient.dob
        form.ins_eff_date.data = patient.ins_eff_date
        form.ins_term_date.data = patient.ins_term_date
        form.allergies.data = patient.allergies
        form.height.data = patient.height
        form.weight.data = patient.weight
        form.address.data = patient.address
        form.state.data = patient.state
        form.city.data = patient.city
        form.zip.data = patient.zip
        form.member_id.data = patient.member_id

    return render_template('patient/addpatient.html', title='Update Patient',
                           form=form, allins=allins, all_users=all_users, patient=patient,
                           insurance_name=insurance_name)


@patient.route("/deletepatient/<int:patient_id>", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient_record = Patient.query.get_or_404(patient_id)
    db.session.delete(patient_record)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('patient.allpatients'))
