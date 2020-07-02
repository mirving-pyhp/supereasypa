# models for DB
from supereasypa import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


#### client id for the user, will be appended to every record the user enters to keep records separated in the database
class Clients(db.Model):
    __clients__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(64))
    fax = db.Column(db.String(64))
    sub_type = db.Column(db.String(64))

    def __init__(self, name, phone, fax, sub_type):
        self.name = name
        self.phone = phone
        self.fax = fax
        self.sub_type = sub_type

    def __repr__(self):
        return f"{self.name}"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    profile_image = db.Column(db.String(20), nullable=False, default='default_profile.png')
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    prior_auth = db.relationship('PriorAuth', backref='assigned_to', lazy=True)
    # user client - for all records
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    def __init__(self, email, username, password, client_id, fname, lname):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.client_id = client_id
        self.fname = fname
        self.lname = lname

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.username}"


class Insurance(db.Model):
    __tablename__ = 'insurance'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(64))
    fax = db.Column(db.String(64))
    alt_phone = db.Column(db.String(64))
    alt_fax = db.Column(db.String(64))
    bin = db.Column(db.String(64))
    pcn = db.Column(db.String(64))
    group = db.Column(db.String(64))
    #### client id ####
    clients = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    def __init__(self, name, phone, fax, alt_phone, alt_fax, bin, pcn, group, client_id):
        self.name = name
        self.phone = phone
        self.fax = fax
        self.alt_phone = alt_phone
        self.alt_fax = alt_fax
        self.bin = bin
        self.pcn = pcn
        self.group = group
        self.client_id = client_id

    def __repr__(self):
        return f"{self.name}"


###prescriber###
class Prescriber(db.Model):
    __tablename__ = 'prescriber'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    address = db.Column(db.String(640))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    zip = db.Column(db.Integer)
    npi = db.Column(db.Integer, unique=True)
    dea = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(64))
    fax = db.Column(db.String(64))
    alt_phone = db.Column(db.String(64))
    alt_fax = db.Column(db.String(64))
    # client id ####
    clients = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    def __init__(self, fname, lname, address, city, state, zip, phone, fax, alt_phone, alt_fax, npi, dea, client_id):
        self.fname = fname
        self.lname = lname
        self.phone = phone
        self.fax = fax
        self.alt_phone = alt_phone
        self.alt_fax = alt_fax
        self.npi = npi
        self.dea = dea
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.client_id = client_id

    def __repr__(self):
        return f"{self.fname} {self.lname}"


###end###

###patient###

class Patient(db.Model):
    __tablename__ = 'patient'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    dob = db.Column(db.DateTime)
    phone = db.Column(db.String(64))
    ins_eff_date = db.Column(db.DateTime)
    ins_term_date = db.Column(db.DateTime)
    allergies = db.Column(db.String(640))
    height = db.Column(db.Integer())
    weight = db.Column(db.String(640))
    disease_states = db.Column(db.String(640))
    address = db.Column(db.String(640))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    zip = db.Column(db.Integer())
    #### client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    # patient insurance
    insurance = db.relationship(Insurance)
    ins_id = db.Column(db.Integer, db.ForeignKey('insurance.id'), nullable=False)
    member_id = db.Column(db.Integer())
    date_last_mod = db.Column(db.DateTime, default=datetime.utcnow)
    date_closed = db.Column(db.DateTime)

    # patient name

    def __init__(self, fname, lname, dob, height, weight, ins_eff_date, ins_term_date, ins_id, phone, address, city,
                 state, zip, allergies, disease_states, client_id, member_id):
        self.height = height
        self.weight = weight
        self.fname = fname
        self.lname = lname
        self.allergies = allergies
        self.dob = dob
        self.ins_eff_date = ins_eff_date
        self.ins_term_date = ins_term_date
        self.ins_id = ins_id
        self.phone = phone
        self.address = address
        self.fname = fname
        self.lname = lname
        self.city = city
        self.state = state
        self.zip = zip
        self.disease_states = disease_states
        self.client_id = client_id
        self.member_id = member_id

    def __repr__(self):
        return f"{self.fname} {self.lname}"


##end###
class PriorAuth(db.Model):
    __tablename__ = 'priorauth'

    __searchable__ = ['drug', 'patient', 'date_open', 'status']

    id = db.Column(db.Integer, primary_key=True)
    # user assigned to PA
    users = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # patient insurance

    ins_id = db.Column(db.Integer, db.ForeignKey('insurance.id'), nullable=False)
    ins_name = db.Column(db.String(64), db.ForeignKey('insurance.name'))
    insurance_id = db.relationship(Insurance, foreign_keys=[ins_id])
    insurance_name = db.relationship(Insurance, foreign_keys=[ins_name])

    # patient prescriber
    prescriber = db.relationship(Prescriber)
    prescriber_id = db.Column(db.Integer, db.ForeignKey('prescriber.id'), nullable=False)

    # patient 
    patient = db.relationship('Patient', backref='patient_assigned', lazy=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

    #### client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    date_open = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_last_mod = db.Column(db.DateTime, default=datetime.utcnow)
    # date_closed = db.Column(db.DateTime)
    eff_date = db.Column(db.DateTime)
    term_date = db.Column(db.DateTime)
    # approval_through = db.Column(db.DateTime)
    status = db.Column(db.String(64))
    drug = db.Column(db.String(64))

    notes_init = db.Column(db.String(255))

    def __init__(self, user_id, ins_id, prescriber_id, drug, notes_init, status, patient_id, client_id, ins_name,
                 eff_date, term_date):
        self.patient_id = patient_id
        self.drug = drug
        self.user_id = user_id
        self.prescriber_id = prescriber_id
        self.notes_init = notes_init
        self.ins_id = ins_id
        self.patient_id = patient_id
        self.status = status
        self.client_id = client_id
        self.ins_name = ins_name
        self.eff_date = eff_date
        self.term_date = term_date

    def __repr__(self):
        return f"Patient ID: {self.patient_id} --- Prior Auth For: {self.drug}"


class Documents(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    doc_path = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    created_by = db.Column(db.String(64))
    #### client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    # insurance docs
    insurance = db.relationship(Insurance)
    ins_id = db.Column(db.Integer, db.ForeignKey('insurance.id'))
    # patient docs
    patient = db.relationship(Patient)
    pt_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    # prior auth docs
    priorauth = db.relationship(PriorAuth)
    pa_id = db.Column(db.Integer, db.ForeignKey('priorauth.id'))
    # prescriber docs
    prescriber = db.relationship(Prescriber)
    md_id = db.Column(db.Integer, db.ForeignKey('prescriber.id'))
    public = db.Column(db.String(2))

    def __init__(self, name, doc_path, created_by, client_id, ins_id, pt_id, pa_id, md_id, description, public):
        self.public = public
        self.doc_path = doc_path
        self.name = name

        self.created_by = created_by
        self.client_id = client_id
        self.ins_id = ins_id
        self.pt_id = pt_id
        self.pa_id = pa_id
        self.md_id = md_id
        self.description = description

    def __repr__(self):
        return f"{self.path} uploaded by {self.created_by}"


class Drugs(db.Model):
    __tablename__ = 'drugs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    strength = db.Column(db.Integer)
    measurement = db.Column(db.String(255))
    dosage_form = db.Column(db.String(255))
    cost = db.Column(db.Integer)
    drug_class = db.Column(db.String(255))
    public = db.Column(db.String(2))
    client_id = db.Column(db.Integer)

    def __init__(self, name, cost, drug_class, public, strength, measurement, dosage_form, client_id):
        self.public = public
        self.name = name
        self.cost = cost
        self.strength = strength
        self.measurement = measurement
        self.dosage_form = dosage_form
        self.drug_class = drug_class
        self.client_id = client_id

    def __repr__(self):
        return f"{self.name} {self.strength} {self.measurement} {self.dosage_form}"


class Map(db.Model):
    __tablename__ = 'map'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    manufacturer = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    income_threshold = db.Column(db.Integer)
    household_size = db.Column(db.Integer)
    required_docs = db.Column(db.String(255))
    # drug
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    drug_name = db.Column(db.String(64), db.ForeignKey('drugs.name'), nullable=False)
    drug_name_map = db.relationship(Drugs, foreign_keys=[drug_name])
    drug_id_map = db.relationship(Drugs, foreign_keys=[drug_id])
    # client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, default='1')

    public = db.Column(db.String(2))

    def __init__(self, name, manufacturer, income_threshold, required_docs, drug_id, drug_name, public, client_id,
                 household_size, phone, fax):
        self.public = public
        self.name = name
        self.manufacturer = manufacturer
        self.income_threshold = income_threshold
        self.required_docs = required_docs
        self.drug_id = drug_id
        self.drug_name = drug_name
        self.client_id = client_id
        self.household_size = household_size
        self.phone = phone
        self.fax = fax

    def __repr__(self):
        return f"{self.name}"


class MapApplication(db.Model):
    __tablename__ = 'mapapplication'

    id = db.Column(db.Integer, primary_key=True)
    # MAP program
    map = db.relationship(Map)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), nullable=False)
    map_name = db.Column(db.String(255))
    # application info
    init_notes = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    fax = db.Column(db.String(255))
    status = db.Column(db.String(255))
    # user assigned to MAP
    users = db.relationship(User)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    # patient insurance
    ins_id = db.Column(db.Integer, db.ForeignKey('insurance.id'), nullable=False)
    ins_name = db.Column(db.String(64), db.ForeignKey('insurance.name'))
    insurance_id = db.relationship(Insurance, foreign_keys=[ins_id])
    insurance_name = db.relationship(Insurance, foreign_keys=[ins_name])
    # patient
    patient = db.relationship(Patient)
    pt_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    pt_info = db.Column(db.String(255))
    # drug
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    drug_name = db.Column(db.String(64), db.ForeignKey('drugs.name'), nullable=False)
    drug_name_map = db.relationship(Drugs, foreign_keys=[drug_name])
    drug_id_map = db.relationship(Drugs, foreign_keys=[drug_id])
    # prescriber
    prescriber = db.relationship(Prescriber)
    md_id = db.Column(db.Integer, db.ForeignKey('prescriber.id'))
    date_open = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, map_id, init_notes, phone, user_id, client_id, ins_id, ins_name, pt_id, drug_id, drug_name,
                 md_id,
                 status, fax, map_name, pt_info):
        self.map_id = map_id
        self.map_name = map_name
        self.phone = phone
        self.fax = fax
        self.user_id = user_id
        self.ins_id = ins_id
        self.client_id = client_id
        self.init_notes = init_notes
        self.ins_name = ins_name
        self.pt_id = pt_id
        self.drug_id = drug_id
        self.drug_name = drug_name
        self.md_id = md_id
        self.status = status
        self.pt_info = pt_info

    def __repr__(self):
        return f"{self.map}"


#### notes for all modules ####

class Notes(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(64))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(64))
    #### client id ####
    client = db.relationship(Clients)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    # insurance notes
    insurance = db.relationship(Insurance)
    ins_id = db.Column(db.Integer, db.ForeignKey('insurance.id'))
    # patient notes
    patient = db.relationship(Patient)
    pt_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    # prior auth notes
    priorauth = db.relationship(PriorAuth)
    pa_id = db.Column(db.Integer, db.ForeignKey('priorauth.id'))
    # prescriber notes
    prescriber = db.relationship(Prescriber)
    md_id = db.Column(db.Integer, db.ForeignKey('prescriber.id'))
    # map notes
    map = db.relationship(Map)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'))
    # map app notes
    mapapp = db.relationship(MapApplication)
    mapapp_id = db.Column(db.Integer, db.ForeignKey('mapapplication.id'))

    def __init__(self, body, created_by, client_id, ins_id, pt_id, pa_id, md_id, map_id, mapapp_id):
        self.body = body
        self.map_id = map_id
        self.mapp_id = mapapp_id
        self.created_by = created_by
        self.client_id = client_id
        self.ins_id = ins_id
        self.pt_id = pt_id
        self.pa_id = pa_id
        self.md_id = md_id

    def __repr__(self):
        return f"{self.body} written by {self.created_by}"
