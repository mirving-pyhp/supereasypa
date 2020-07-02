# document views #
import os
import io
from io import BytesIO
from operator import or_

import pdfkit
from supereasypa import app
from flask import render_template, url_for, flash, redirect, request, Blueprint, make_response, send_file
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Notes, Documents, Drugs
from supereasypa.documents.forms import AddDocumentsFormulary
from werkzeug.utils import secure_filename
from datetime import date, time
from datetime import datetime, timedelta
from pytz import timezone

UPLOAD_FOLDER = 'supereasypa/static/user_uploads/formularies'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

document = Blueprint('document', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@document.route('/formularies', methods=['GET', 'POST'])
@login_required
def viewformularydocs():
    success = ''
    form = AddDocumentsFormulary()
    user_logged = current_user.client_id  # current client id #
    docs_module = Documents.query.filter(or_(Documents.client_id == user_logged, Documents.public == 'Y')).order_by(
        Documents.id.desc()).all()
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
                             doc_path='/static/user_uploads/formularies/' + filename,
                             description=form.description.data,
                             pt_id=0,
                             ins_id=0,
                             md_id=0,
                             pa_id=0,
                             public='Y')
        flash('Added successfully!')
        db.session.add(document)
        db.session.commit()
        return redirect(url_for('document.viewformularydocs'))


    return render_template('documents/formularydocs.html',
                           user_logged=user_logged, docs_module=docs_module,
                           form=form, success=success
                           )
