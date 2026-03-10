# src/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Link to sessions
    sessions = db.relationship('ProjectSession', backref='owner', lazy=True)

class ProjectSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Link to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_state = db.relationship('SessionData', backref='project_session', uselist=False, lazy=True, cascade='all, delete-orphan')


class SessionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('project_session.id'), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=True)
    data_json = db.Column(db.Text, nullable=False, default='[]')
    file_metadata_json = db.Column(db.Text, nullable=False, default='[]')
    visuals_json = db.Column(db.Text, nullable=False, default='[]')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def add_user(email, password):
    if not User.query.filter_by(email=email).first():
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return "User created successfully."
    return "User already exists."

def create_session(session_name, user_id):
    new_session = ProjectSession(name=session_name, user_id=user_id)
    db.session.add(new_session)
    db.session.commit()
    return new_session.id


def save_session_data(session_id, filename, records, file_metadata):
    state = SessionData.query.filter_by(session_id=session_id).first()
    if not state:
        state = SessionData(session_id=session_id)
        db.session.add(state)

    state.filename = filename
    state.data_json = json.dumps(records or [])
    state.file_metadata_json = json.dumps(file_metadata or [])
    db.session.commit()


def load_session_data(session_id):
    state = SessionData.query.filter_by(session_id=session_id).first()
    if not state:
        return None

    return {
        'filename': state.filename,
        'records': json.loads(state.data_json or '[]'),
        'file_metadata': json.loads(state.file_metadata_json or '[]'),
        'visuals': json.loads(state.visuals_json or '[]')
    }


def save_visuals(session_id, visuals):
    state = SessionData.query.filter_by(session_id=session_id).first()
    if not state:
        state = SessionData(session_id=session_id, data_json='[]', file_metadata_json='[]')
        db.session.add(state)
    state.visuals_json = json.dumps(visuals or [])
    db.session.commit()