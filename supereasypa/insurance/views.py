### insurance views ###
import os
import io
from supereasypa import app
from io import BytesIO
import pdfkit
from flask import render_template, url_for, flash, redirect, request, Blueprint, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Documents, Notes
from supereasypa.insurance.forms import AddInsurance, AddDocsInsurance, AddNotesInsurance
from werkzeug.utils import secure_filename
from datetime import date, time
from datetime import datetime, timedelta
from pytz import timezone

UPLOAD_FOLDER = 'supereasypa/static/user_uploads/insurances'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Users\matth\source\repos\supereasypa\supereasypa\wkhtmltopdf\bin\wkhtmltopdf.exe")

insurance = Blueprint('insurance', __name__)


@insurance.route('/addinsurance', methods=['GET', 'POST'])
@login_required
def addins():
    form = AddInsurance()
    user_logged = current_user.client_id

    if form.validate_on_submit():
        insurance = Insurance(name=form.name.data,
                              phone=form.phone.data,
                              fax=form.fax.data,
                              alt_phone=form.alt_phone.data,
                              alt_fax=form.alt_fax.data,
                              bin=form.bin.data,
                              pcn=form.pcn.data,
                              group=form.group.data,
                              client_id=user_logged)
        ## test print(Insurance.query.all())
        db.session.add(insurance)
        db.session.commit()
        return redirect(url_for('insurance.allinsurance'))

    return render_template('insurance/addins.html', form=form)


@insurance.route('/allinsurance')
@login_required
def allinsurance():
    page = request.args.get('page', 1, type=int)
    insurance = Insurance.query.filter_by(client_id=current_user.client_id).paginate(page=page, per_page=30000)
    return render_template('insurance/all_insurance.html', insurance=insurance)


### individual insurance record ###
@insurance.route('/insurance/<int:insurance_id>', methods=['GET', 'POST'])
@login_required
def viewinsurance(insurance_id):
    insurance_record = Insurance.query.get_or_404(insurance_id)
    user_logged = current_user.client_id  ### curent client id ###

    ### pull insurance name ###
    ins_id = insurance_record.id

    insurance_name_pull = Insurance.query.filter_by(id=ins_id).first()

    insurance_name = insurance_name_pull

    ### pulls drug count ###

    ### number of drugs per PA ###

    drug_counts = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id, ins_id=ins_id). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(5). \
        all()

    for drug_name, count in drug_counts:
        med_name = drug_name
        count_drug = count
        list_of_drug = [drug_name, count]

    ### pull prior auth record ###

    prior_auths = PriorAuth.query.filter_by(ins_id=ins_id).all()
    all_pts = Patient.query.filter_by(ins_id=ins_id).count()

    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id, ins_id=ins_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id, ins_id=ins_id).count()
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id, ins_id=ins_id).count()

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

    form_notes = AddNotesInsurance()

    # add notes ####
    if form_notes.validate_on_submit():
        notes = Notes(body=form_notes.body.data,
                      client_id=current_user.client_id,
                      created_by=current_user.username,
                      pt_id=0,
                      ins_id=ins_id,
                      md_id=0,
                      pa_id=0)

        db.session.add(notes)
        db.session.commit()
        return redirect(url_for('insurance.viewinsurance', insurance_id=ins_id))

    # return notes into page in notes section ####

    notes_pa = Notes.query.filter_by(ins_id=ins_id).order_by(Notes.id.desc()).all()

    return render_template('insurance/insurance.html',
                           user_logged=user_logged, insurance_name=insurance_name,
                           insurance_name_pull=insurance_name_pull, prior_auths=prior_auths,
                           allpending=allpending, alldenied=alldenied, allapproved=allapproved,
                           insurance_record=insurance_record, all_pts=all_pts, approval_percentage=approval_percentage,
                           denial_percentage=denial_percentage, drug_counts=drug_counts, notes_pa=notes_pa, form_notes=form_notes)


# view insurance documents #
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@insurance.route('/insurancedocs/<int:insurance_id>', methods=['GET', 'POST'])
@login_required
def viewinsurancedocs(insurance_id):
    form = AddDocsInsurance()
    insurance = Insurance.query.get_or_404(insurance_id)
    ins_id = insurance.id
    user_logged = current_user.client_id  # current client id #
    docs_module = Documents.query.filter_by(ins_id=ins_id).order_by(Documents.id.desc()).all()
    # pull prior auth record #
    # upload documents for insurance, allowed file types: pdf only!!! #
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
            file.save(os.path.join('supereasypa/static/user_uploads/insurances', filename))

            # return redirect(request.url)
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
    if form.validate_on_submit():
        # commit info to database #
        document = Documents(name=form.name.data,
                             created_by=current_user.username,
                             client_id=current_user.client_id,
                             doc_path='/static/user_uploads/insurances/' + filename,
                             description=form.description.data,
                             pt_id=0,
                             ins_id=ins_id,
                             md_id=0,
                             pa_id=0,
                             public='N')

        db.session.add(document)
        db.session.commit()

        return redirect(url_for('insurance.viewinsurancedocs', insurance_id=ins_id))

    return render_template('documents/docsinsurance.html',
                           insurance=insurance, user_logged=user_logged, ins_id=ins_id, form=form,
                           docs_module=docs_module
                           )


### update and delete records ###

@insurance.route("/update/<int:insurance_id>", methods=['GET', 'POST'])
@login_required
def update(insurance_id):
    form = AddInsurance()
    user_logged = current_user.client_id
    insurance = Insurance.query.get_or_404(insurance_id)
    if form.validate_on_submit():
        ### commit form data ###
        insurance.name = form.name.data
        insurance.phone = form.phone.data
        insurance.fax = form.fax.data
        insurance.alt_fax = form.alt_fax.data
        insurance.alt_phone = form.alt_phone.data
        insurance.bin = form.bin.data
        insurance.pcn = form.pcn.data
        insurance.group = form.group.data

        db.session.commit()
        return redirect(url_for('insurance.viewinsurance', insurance_id=insurance.id))
    elif request.method == 'GET':
        form.name.data = insurance.name
        form.phone.data = insurance.phone
        form.fax.data = insurance.fax
        form.alt_fax.data = insurance.alt_fax
        form.alt_phone.data = insurance.alt_phone
        form.bin.data = insurance.bin
        form.pcn.data = insurance.pcn
        form.group.data = insurance.group

    return render_template('insurance/addins.html', title='Update Insurance',
                           form=form, insurance=insurance, user_logged=user_logged)


@insurance.route("/delete/<int:insurance_id>", methods=['POST'])
@login_required
def delete_insurance(insurance_id):
    insurance = Insurance.query.get_or_404(insurance_id)
    db.session.delete(insurance)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('insurance.allinsurance', insurance=insurance))
