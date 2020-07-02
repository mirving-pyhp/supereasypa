# core views
import sys
import datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from werkzeug.security import generate_password_hash, check_password_hash
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Clients
from flask import render_template, request, Blueprint
from datetime import datetime, date

core = Blueprint('core', __name__)


@core.route('/')
@login_required
def index():
    allpts = Patient.query.filter_by(client_id=current_user.client_id).count()

    ### prior auth stats ###
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id).count()
    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id).count()
    ### pull insurance stats ###
    allinsct = Insurance.query.filter_by(client_id=current_user.client_id).count()

    allpas = PriorAuth.query.filter_by(client_id=current_user.client_id)
    allins = Insurance.query.filter_by(client_id=current_user.client_id)

    ### pulls all prior authorizations by id number ###

    insurance_counts = db.session.query(PriorAuth.ins_name, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        group_by(PriorAuth.ins_name). \
        order_by(db.func.count().desc()). \
        limit(5). \
        all()

    ### count of prior authorizations per insurance plan ###

    for ins_name, count in insurance_counts:
        plan_name = ins_name
        count_plan = count

        list_of_plans = [ins_name, count]
    ### number of drugs per PA ###

    drug_counts = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(5). \
        all()

    for drug_name, count in drug_counts:
        med_name = drug_name
        count_drug = count
        list_of_drug = [drug_name, count]

    # count_of = PriorAuth.query.filter_by(ins_id=insname).count

    total = allapproved + alldenied + allpending

    if total > 0:
        approval_percentage = round(allapproved / total * 100, 2)
        denial_percentage = round(alldenied / total * 100, 2)
        pending_percentage = round(allpending / total * 100, 2)
        paperpatient = round(total / allpts, 2)
    else:
        approval_percentage = 0
        denial_percentage = 0
        pending_percentage = 0
        paperpatient = 0

    ### query prior authorizations by date created ###
    now = datetime.now().year
    print(now)

    start_may = datetime(now, 5, 1)
    end_may = datetime(now, 6, 1)

    may_counts = db.session.query(PriorAuth.date_open, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        filter(PriorAuth.date_open.between(start_may, end_may)). \
        all()
    #june counts
    start_june = datetime(now, 6, 1)
    end_june = datetime(now, 6, 30)

    june_counts = db.session.query(PriorAuth.date_open, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        filter(PriorAuth.date_open.between(start_june, end_june)). \
        all()

    for pa_may, count in may_counts:
        pa_month = pa_may
        count_may = count
        list_of_may = [pa_may, count]
    for pa_june, count in june_counts:
        pa_month_6 = pa_june
        count_june = count
        list_of_may = [pa_june, count]


    return render_template('index.html', allpts=allpts, allapproved=allapproved,
                           alldenied=alldenied, allpending=allpending, approval_percentage=approval_percentage,
                           denial_percentage=denial_percentage, pending_percentage=pending_percentage,
                           allins=allins, allpas=allpas, allinsct=allinsct, insurance_counts=insurance_counts,
                           drug_counts=drug_counts,
                           paperpatient=paperpatient, may_counts=may_counts,june_counts=june_counts)


