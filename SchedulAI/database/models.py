from datetime import datetime
from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EventCache(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    summary = db.Column(db.String(200), nullable=False)
    start = db.Column(db.String(50), nullable=False)
    end = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FollowUpTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(64), db.ForeignKey('event_cache.id'))
    followup_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
    

