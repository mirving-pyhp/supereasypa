# dashboard views
import sys
import datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from werkzeug.security import generate_password_hash, check_password_hash
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Clients, MapApplication
from flask import render_template, request, Blueprint
from datetime import datetime, date

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def dashboardview():
    allpts = Patient.query.filter_by(client_id=current_user.client_id).count()

    ### prior auth stats ###
    allapproved = PriorAuth.query.filter_by(status='Approved', client_id=current_user.client_id).count()
    alldenied = PriorAuth.query.filter_by(status='Denied', client_id=current_user.client_id).count()
    allpending = PriorAuth.query.filter_by(status='Pending', client_id=current_user.client_id).count()
    ### pull insurance stats ###
    allinsct = Insurance.query.filter_by(client_id=current_user.client_id).count()

    allpas = PriorAuth.query.filter_by(client_id=current_user.client_id).count()
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
        limit(10). \
        all()

    for drug_name, count in drug_counts:
        med_name = drug_name
        count_drug = count
        list_of_drug = [drug_name, count]
    ## number one drug
    no1_drug = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()

    for num_one, count_one in no1_drug:
        one_name = drug_name
        count_one_time = count_one
        list_of_drug = [num_one, count_one]

    ## number one denied drug
    no1_denied_drug = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id, status='Denied'). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()

    for num_one_denied, count_denied in no1_drug:
        list_of_drug = [num_one_denied, count_denied]

        ## number one approved drug
    no1_approved_drug = db.session.query(PriorAuth.drug, db.func.count()). \
        filter_by(client_id=current_user.client_id, status='Approved'). \
        group_by(PriorAuth.drug). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()

    # number of prior authorizations

    ## number one approved drug by plan
    no1_approved_drug_plan = db.session.query(PriorAuth.ins_name, db.func.count()). \
        filter_by(client_id=current_user.client_id, status='Approved'). \
        group_by(PriorAuth.ins_name). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()

    for num_one_approved_plan, count_approved_plan in no1_drug:
        list_of_drug = [num_one_approved_plan, count_approved_plan]

    for num_one_approved_plan, count_approved_plan in no1_drug:
        list_of_drug = [num_one_approved_plan, count_approved_plan]

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

    # map data

    # approved MAP

    no1_approved_map = db.session.query(MapApplication.drug_name, db.func.count()). \
        filter_by(client_id=current_user.client_id, status='Approved'). \
        group_by(MapApplication.drug_name). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()
    no1_med = ''
    no1_med_denied = ''

    for no1_med, count in no1_approved_map:
        drug_name = no1_med
        count_med = count

        list_of_approved_1 = [no1_med, count]

    no1_denied_map = db.session.query(MapApplication.drug_name, db.func.count()). \
        filter_by(client_id=current_user.client_id, status='Denied'). \
        group_by(MapApplication.drug_name). \
        order_by(db.func.count().desc()). \
        limit(1). \
        all()
    for no1_med_denied, count in no1_denied_map:
        drug_name = no1_med_denied
        count_med = count

        list_of_approved_1 = [no1_med_denied, count]

    pending_map = MapApplication.query.filter_by(status='Pending').count()
    print(pending_map)
    ### query prior authorizations by date created ###
    now = datetime.now().year

    start_may = datetime(now, 5, 1)
    end_may = datetime(now, 6, 1)

    may_counts = db.session.query(PriorAuth.date_open, db.func.count()). \
        filter_by(client_id=current_user.client_id). \
        filter(PriorAuth.date_open.between(start_may, end_may)). \
        all()
    # june counts
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

    return render_template('dashboard/dashboard.html', allpts=allpts, allapproved=allapproved,
                           alldenied=alldenied, allpending=allpending, approval_percentage=approval_percentage,
                           denial_percentage=denial_percentage, pending_percentage=pending_percentage,
                           allins=allins, allpas=allpas, allinsct=allinsct, insurance_counts=insurance_counts,
                           drug_counts=drug_counts,
                           paperpatient=paperpatient, may_counts=may_counts, june_counts=june_counts, no1_drug=no1_drug,
                           no1_denied_drug=no1_denied_drug
                           , no1_approved_drug=no1_approved_drug, no1_approved_drug_plan=no1_approved_drug_plan,
                           no1_approved_map=no1_approved_map,
                           no1_med=no1_med, no1_med_denied=no1_med_denied, pending_map=pending_map)
