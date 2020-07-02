### prior auth views ###
import sys
import os
from supereasypa import app
import pdfkit
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Drugs, Notes, Documents, Map
from supereasypa.priorauth.forms import AddPAForm, AddNotesPriorAuth, AddDocsPriorAuth
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'supereasypa/static/user_uploads/priorauths'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Users\matth\source\repos\supereasypa\supereasypa\wkhtmltopdf\bin\wkhtmltopdf.exe")

priorauths = Blueprint('priorauth', __name__)


@priorauths.route('/addpriorauth', methods=['GET', 'POST'])
@login_required
def addpa():
    form = AddPAForm()

    user_logged = current_user.client_id
    allins = Insurance.query.filter_by(client_id=user_logged)
    priorauth_id = 0
    current_auth = PriorAuth.query.filter_by(client_id=user_logged, id=priorauth_id).first()
    allpts = Patient.query.filter_by(client_id=user_logged).all()
    all_users = User.query.filter_by(client_id=user_logged).all()
    all_drugs = Drugs.query.order_by(Drugs.name.asc()).all()
    allmd = Prescriber.query.filter_by(client_id=user_logged)



    #current client id based on user login

    if form.validate_on_submit():
        plan_name = Insurance.query.filter_by(client_id=current_user.client_id, id=form.insurance_id.data).first()
        plan_named = plan_name.name

        priorauth = PriorAuth(drug=form.drug.data,
                              prescriber_id=form.prescriber_id.data,
                              ins_id=form.insurance_id.data,
                              ins_name=plan_named,
                              patient_id=form.patient_id.data,
                              status=form.status.data,
                              eff_date=form.eff_date.data,
                              term_date=form.term_date.data,
                              user_id=form.user_id.data,
                              notes_init=form.notes_init.data,
                              client_id=user_logged)

        db.session.add(priorauth)
        db.session.commit()
        return redirect(url_for('priorauth.allpriorauths'))

    return render_template('priorauth/addpa.html', form=form, user_logged=user_logged, allins=allins, current_auth=current_auth,
                           allpts=allpts, all_users=all_users, all_drugs=all_drugs, allmd=allmd)


######################### view prior auths #############################
@priorauths.route('/allpriorauths', methods=['GET', 'POST'])
@login_required
def allpriorauths():
    user_logged = current_user.client_id
    page = request.args.get('page', 1, type=int)
    priorauth = PriorAuth.query.filter_by(client_id=user_logged).paginate(page=page,
                                                                          per_page=30000)  ###this works perfectly
    return render_template('priorauth/all_priorauths.html', priorauth=priorauth)


@priorauths.route('/priorauth/<int:priorauth_id>', methods=['GET', 'POST'])
@login_required
def viewpa(priorauth_id):
    ### prevent customers from accessing each others records ###

    priorauth = PriorAuth.query.get_or_404(priorauth_id)
    pa_id = priorauth.id
    auth_status = priorauth.status
    start_date = ''
    thru_date = ''
    style_approval = 'display:none;'
    eff_date = priorauth.eff_date.strftime('%m-%d-%Y')
    term_date = priorauth.term_date.strftime('%m-%d-%Y')
    pull_drug_map = Map.query.filter_by(drug_name=priorauth.drug).first()
    map_available = ''
    disabled = ''
    map_id = ''
    if pull_drug_map is not None:
        map_available = pull_drug_map.name

        map_id = pull_drug_map.id
        disabled = ''

    else:
        map_available = 'None'
        disabled = 'disabled'
        map_id = 0




    if auth_status == 'Approved':
        thru_date = '1/1/2021'
        start_date = '1/1/2022'

    form_notes = AddNotesPriorAuth()

    # add notes ####
    if form_notes.validate_on_submit():
        notes = Notes(body=form_notes.body.data,
                      client_id=current_user.client_id,
                      created_by=current_user.username,
                      pt_id=0,
                      ins_id=0,
                      md_id=0,
                      pa_id=pa_id)

        db.session.add(notes)
        db.session.commit()
        return redirect(url_for('priorauth.viewpa', priorauth_id=pa_id))

    # return notes into page in notes section ####

    notes_pa = Notes.query.filter_by(pa_id=pa_id).order_by(Notes.id.desc()).all()

    # getid = PriorAuth.query.filter_by(id=priorauth_id)

    # if (current_user.client_id is not PriorAuth.client_id):
    #    sys.exit("You do not have access to this record")

    return render_template('priorauth/priorauth.html',
                           priorauth=priorauth, auth_status=auth_status, thru_date=thru_date, start_date=start_date,
                           style_approval=style_approval, form_notes=form_notes, notes_pa=notes_pa, eff_date=eff_date, term_date=term_date
                           ,map_available=map_available, pull_drug_map=pull_drug_map,disabled=disabled,map_id=map_id
                           )
# view individual patient documents #
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@priorauths.route('/priorauthdocs/<int:priorauth_id>', methods=['GET', 'POST'])
@login_required
def viewpriorauthdocs(priorauth_id):
    form = AddDocsPriorAuth()
    priorauth = PriorAuth.query.get_or_404(priorauth_id)
    pa_id = priorauth.id
    user_logged = current_user.client_id  # current client id #
    docs_module = Documents.query.filter_by(pa_id=pa_id).order_by(Documents.id.desc()).all()
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
            file.save(os.path.join('supereasypa/static/user_uploads/priorauths', filename))

            # return redirect(request.url)a
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
    if form.validate_on_submit():
        # commit info to database #
        document = Documents(name=form.name.data,
                             created_by=current_user.username,
                             client_id=current_user.client_id,
                             doc_path='/static/user_uploads/priorauths/' + filename,
                             description=form.description.data,
                             pt_id=0,
                             ins_id=0,
                             md_id=0,
                             pa_id=pa_id,
                             public='Y')

        db.session.add(document)
        db.session.commit()

        return redirect(url_for('priorauth.viewpriorauthdocs', priorauth_id=pa_id))

    return render_template('documents/docspriorauth.html',
                           priorauth=priorauth, user_logged=user_logged, pa_id=pa_id, form=form,
                           docs_module=docs_module
                           )

@priorauths.route("/<int:priorauth_id>/update", methods=['GET', 'POST'])
@login_required
def update(priorauth_id):
    form = AddPAForm()
    user_logged = current_user.client_id
    priorauth = PriorAuth.query.get_or_404(priorauth_id)
    allins = Insurance.query.filter_by(client_id=user_logged)
    current_auth = PriorAuth.query.filter_by(client_id=user_logged, id=priorauth_id).first()
    current_auth_ins = current_auth.ins_name
    current_auth_drug = current_auth.drug
    current_status = current_auth.status
    current_auth_status = current_status
    current_auth_assigned_to = current_auth.assigned_to
    current_auth_patient = current_auth.patient
    current_ins = f"Current: {current_auth_ins}"
    current_drug = f"Current: {current_auth_drug}"
    current_status = f"Current: {current_auth_status}"
    current_patient = f"Current: {current_auth_patient}"
    current_assigned_to = f"Current: {current_auth_assigned_to}"
    allpts = Patient.query.filter_by(client_id=user_logged).all()
    all_users = User.query.filter_by(client_id=user_logged).all()
    allmd = Prescriber.query.filter_by(client_id=user_logged)
    current_prescriber = f"Current: {priorauth.prescriber}"
    #print(current_drug)

    if form.validate_on_submit():

        plan_name = Insurance.query.filter_by(client_id=current_user.client_id, id=form.insurance_id.data).first()
        plan_named = plan_name.name
        priorauth.drug = form.drug.data
        priorauth.prescriber_id = form.prescriber_id.data
        priorauth.ins_id = form.insurance_id.data
        priorauth.ins_name = plan_named  ### insurance name ###
        priorauth.patient_id = form.patient_id.data
        priorauth.status = form.status.data
        priorauth.user_id = form.user_id.data
        priorauth.notes_init = form.notes_init.data
        priorauth.eff_date = form.eff_date.data
        priorauth.term_date = form.term_date.data
        db.session.commit()
        return redirect(url_for('priorauth.viewpa', priorauth_id=priorauth.id))
    elif request.method == 'GET':
        form.notes_init.data = priorauth.notes_init
        form.drug.data = priorauth.drug
        form.insurance_id.data = priorauth.ins_name
        form.eff_date.data = priorauth.eff_date
        form.term_date.data = priorauth.term_date

    return render_template('priorauth/addpa.html', title='Update',
                           form=form, allins=allins, current_auth=current_auth, current_ins=current_ins,
                           current_auth_ins=current_auth_ins, current_status=current_status
                           , allpts=allpts, current_patient=current_patient, current_assigned_to=current_assigned_to,
                           all_users=all_users, current_drug=current_drug, current_auth_drug=current_auth_drug, allmd=allmd
                           , current_prescriber=current_prescriber)


@priorauths.route("/<int:priorauth_id>/delete", methods=['POST'])
@login_required
def delete_priorauth(priorauth_id):
    priorauth = PriorAuth.query.get_or_404(priorauth_id)
    db.session.delete(priorauth)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('priorauth.allpriorauths'))
