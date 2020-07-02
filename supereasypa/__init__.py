# main folder
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'

#################################
### DATABASE SETUPS ############
###############################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

#### END ####

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "users.login"

from supereasypa.core.views import core
from supereasypa.error_pages.handlers import error_pages
from supereasypa.users.views import users
from supereasypa.priorauth.views import priorauths
from supereasypa.insurance.views import insurance
from supereasypa.patients.views import patient
from supereasypa.clients.views import clients
from supereasypa.prescriber.views import prescriber
from supereasypa.drugs.views import drug
from supereasypa.documents.views import document
from supereasypa.dashboard.views import dashboard
from supereasypa.map.views import map
from supereasypa.mapapps.views import mapapp

app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(priorauths)
app.register_blueprint(insurance)
app.register_blueprint(patient)
app.register_blueprint(clients)
app.register_blueprint(prescriber)
app.register_blueprint(drug)
app.register_blueprint(document)
app.register_blueprint(dashboard)
app.register_blueprint(map)
app.register_blueprint(mapapp)
