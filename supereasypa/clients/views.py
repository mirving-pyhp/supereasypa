### client views ###

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from werkzeug.security import generate_password_hash,check_password_hash
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Clients
from supereasypa.users.picture_handler import add_profile_pic
from supereasypa.clients.forms import AddClient

clients = Blueprint('clients', __name__)

@clients.route('/addclients', methods=['GET', 'POST'])
def addclient():
    form = AddClient()
    ##allclients = Clients.query.order_by(Clients.name.desc())

    if form.validate_on_submit():
        client = Clients(name=form.name.data,
                    phone=form.phone.data,
                    fax=form.fax.data,
                    sub_type=form.sub_type.data)### client id ###

        db.session.add(client)
        db.session.commit()
        #flash('Thanks for registering! Now you can login!')
        return redirect(url_for('users.login'))
    return render_template('admin/addclient.html', form=form)
