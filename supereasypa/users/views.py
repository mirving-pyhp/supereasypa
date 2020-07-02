### user views ###

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from supereasypa import db
from werkzeug.security import generate_password_hash, check_password_hash
from supereasypa.models import User, PriorAuth, Patient, Insurance, Prescriber, Clients
from supereasypa.users.picture_handler import add_profile_pic
from supereasypa.users.forms import RegistrationForm, LoginForm, UpdateUserForm

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    allclients = Clients.query.order_by(Clients.name.desc())

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    fname=form.fname.data,
                    lname=form.lname.data,
                    client_id=form.client_id.data)  ### client id ###

        db.session.add(user)
        db.session.commit()
        # flash('Thanks for registering! Now you can login!')
        return redirect(url_for('users.login'))
    return render_template('admin/register.html', form=form, allclients=allclients)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    style = 'd-none'

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:

            login_user(user)

            next = request.args.get('next')

            if next == None or not next[0] == '/':
                next = url_for('core.index')

            return redirect(next)

        else:
            style = 'alert alert-danger alert-dismissible'
            flash('Invalid email and/or password. Please double check your entry and try again.')


    return render_template('user/login.html', form=form, style=style)


# if current_user.is_authenticated():
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUserForm()

    if form.validate_on_submit():
        print(form)
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('user/account.html', profile_image=profile_image, form=form)


@users.route("/<username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    prior_auths = PriorAuth.query.filter_by(assigned_to=user).order_by(PriorAuth.date.desc()).paginate(page=page,
                                                                                                       per_page=10)
    return render_template('priorauth/priorauth.html', prior_auths=prior_auths, user=user)
