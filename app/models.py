from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
from flask_login import UserMixin


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    matricule = db.Column(db.String(15), unique=True, nullable=False)
    fonction = db.Column(db.String(150), nullable=False)
    prenom = db.Column(db.String(150), nullable=False)
    shift = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    profile_image = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    # Ensure this is a boolean field
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)  # New field
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    # New column for approval
    is_approved = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Todo', backref='user',
                            lazy=True, cascade="all, delete-orphan")
    is_pending = db.Column(db.Boolean, default=True)

    def update_last_seen(self):
        self.last_update = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return str(self.id)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Consider if this should be nullable
    content = db.Column(db.String(200), nullable=True)
    shift = db.Column(db.String(50))
    poste = db.Column(db.String(50))
    navire = db.Column(db.String(50))
    grue = db.Column(db.String(50))
    marchandise = db.Column(db.String(50))
    nb_cs_pcs = db.Column(db.String(50))
    unite = db.Column(db.String(50))
    raclage = db.Column(db.String(50))
    comentaire = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key relationship to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Track if the task is validated
    is_validated = db.Column(db.Boolean, default=False)
    # Name of the admin who validated it
    validated_by = db.Column(db.String(150), nullable=True)
    # Track task status
    status = db.Column(db.String(50), default='pending')
    remark = db.Column(db.String(255), nullable=True)
    Escale = db.Column(db.String(15), nullable=True)  # Make nullable

    execution_time = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Task {self.id}>'


class Conference(db.Model):
    __tablename__ = 'conference'  # Specific table name for Conference

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pm = db.Column(db.String(50))
    marchandise = db.Column(db.String(50))
    navire = db.Column(db.String(50))
    poste = db.Column(db.String(50))
    grue = db.Column(db.String(50))
    tonnage_manif = db.Column(db.String(50))
    tonnage_rest = db.Column(db.String(50))
    consignataire = db.Column(db.String(50))
    receptionnaire = db.Column(db.String(50))
    elevateur = db.Column(db.String(50))
    materiel_a_bord = db.Column(db.String(50))
    Date_debut_travail = db.Column(db.Date, default=datetime.utcnow().date)
    Date_fin_travail = db.Column(db.Date, default=datetime.utcnow().date)
    Heure_Terminaison_Travail_Prévue = db.Column(db.Time, nullable=True)
    observation = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship to ConferenceDetail
    details = db.relationship(
        'ConferenceDetail', backref='conference', lazy='dynamic')

    def __repr__(self):
        return f'<Conference {self.id}, poste: {self.poste}>'


class ConferenceDetail(db.Model):
    __tablename__ = 'conferenceDetails'  # Specific table name for ConferenceDetails

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pm = db.Column(db.String(50))
    marchandise = db.Column(db.String(50))
    navire = db.Column(db.String(50))
    poste = db.Column(db.String(50))
    grue = db.Column(db.String(50))
    tonnage_manif = db.Column(db.String(50))
    tonnage_rest = db.Column(db.String(50))
    consignataire = db.Column(db.String(50))
    receptionnaire = db.Column(db.String(50))
    elevateur = db.Column(db.String(50))
    materiel_a_bord = db.Column(db.String(50))
    Date_debut_travail = db.Column(db.Date, default=datetime.utcnow().date)
    Date_fin_travail = db.Column(db.Date, default=datetime.utcnow().date)
    Heure_Terminaison_Travail_Prévue = db.Column(db.Time, nullable=True)
    observation = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Foreign key referencing the Conference table
    conference_id = db.Column(db.Integer, db.ForeignKey(
        'conference.id'), nullable=False)

    def __repr__(self):
        return f'<ConferenceDetail {self.id}, poste: {self.poste}>'
