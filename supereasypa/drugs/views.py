### drug views ###
import os
import io
from io import BytesIO
import pdfkit
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents, Drugs, Map
from supereasypa.drugs.forms import AddDrug
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

drug = Blueprint('drug', __name__)


@drug.route('/adddrug', methods=['GET', 'POST'])
@login_required
def adddrug():
    form = AddDrug()
    user_logged = current_user.client_id
    drugs = ''

    if form.validate_on_submit():
        drugs = Drugs(name=form.name.data,
                      cost=form.cost.data,
                      strength=form.strength.data,
                      measurement=form.measurement.data,
                      dosage_form=form.dosage_form.data,
                      drug_class=form.drug_class.data,
                      client_id=user_logged,
                      public='Y')

        db.session.add(drugs)
        db.session.commit()
        return redirect(url_for('drug.alldrugs'))

    return render_template('drugs/adddrug.html', form=form, drugs=drugs)


@drug.route('/alldrugs', methods=['GET', 'POST'])
@login_required
def alldrugs():
    page = request.args.get('page', 1, type=int)
    user_logged = current_user.client_id
    alldrugs = Drugs.query.paginate(page=page, per_page=100)

    return render_template('drugs/all_drugs.html', alldrugs=alldrugs, user_logged=user_logged)


### individual drug record ###
@drug.route('/drug/<int:drug_id>', methods=['GET', 'POST'])
@login_required
def viewdrug(drug_id):
    drug_record = Drugs.query.get_or_404(drug_id)
    user_logged = current_user.client_id  # curent client id #
    map_available = Map.query.filter_by(drug_name=drug_record.name).first()
    disabled = ''

    if map_available is None:
        map_id = 0
        map_available = 'None Available'
        disabled = 'nav-link disabled'  # bootstrap styling to disable link
    else:
        map_id = map_available.id
        disabled = ''
        map_available = Map.query.filter_by(drug_name=drug_record.name).first()

    # pull insurance name #
    rx_id = drug_record.id

    drug_name_pull = Drugs.query.filter_by(id=rx_id).first()

    drug_name = drug_name_pull

    # pull prior auth record #

    prior_auths = PriorAuth.query.filter_by(client_id=current_user.client_id, drug=drug_record.name).all()
    all_pts = PriorAuth.query.filter_by(client_id=current_user.client_id, drug=drug_record.name).distinct().count()

    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id,
                                           drug=drug_record.name).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id,
                                          drug=drug_record.name).count()
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id,
                                            drug=drug_record.name).count()

    total = allapproved + alldenied + allpending

    if total > 0:
        approval_percentage = round(allapproved / total * 100, 2)
        denial_percentage = round(alldenied / total * 100, 2)
    # pending_percentage = round(allpending / total * 100,2)
    # paperpatient = round(total / all_pts,2)
    else:
        approval_percentage = 0
        denial_percentage = 0
    #    pending_percentage = 0

    #    paperpatient = 0
    print(prior_auths)
    return render_template('drugs/drug.html',
                           user_logged=user_logged, drug_name=drug_name,
                           drug_name_pull=drug_name_pull, prior_auths=prior_auths,
                           allpending=allpending, alldenied=alldenied, allapproved=allapproved,
                           drug_record=drug_record, all_pts=all_pts, approval_percentage=approval_percentage,
                           denial_percentage=denial_percentage, map_available=map_available, map_id=map_id,
                           disabled=disabled
                           )


@drug.route("/updatedrug/<int:drug_id>", methods=['GET', 'POST'])
@login_required
def update(drug_id):
    form = AddDrug()
    user_logged = current_user.client_id
    drug = Drugs.query.get_or_404(drug_id)
    if form.validate_on_submit():

        ### commit form data ###
        drug.name = form.name.data
        drug.drug_class = form.drug_class.data
        drug.cost = form.cost.data
        db.session.commit()
        return redirect(url_for('drug.viewdrug', drug_id=drug.id))
    elif request.method == 'GET':
        form.name.data = drug.name
        form.drug_class.data = drug.drug_class
        form.cost.data = drug.cost

    return render_template('drugs/adddrug.html', title='Update Drug',
                           form=form, drug=drug
                           )


@drug.route("/deletedrug/<int:drug_id>", methods=['POST'])
@login_required
def delete_drug(drug_id):
    drug = Drugs.query.get_or_404(drug_id)
    db.session.delete(drug)
    db.session.commit()
    flash('Deleted!')

    return redirect(url_for('drug.alldrugs'))
