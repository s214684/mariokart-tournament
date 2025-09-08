from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed'
    players = db.relationship('Player', backref='tournament', lazy=True)
    matches = db.relationship('Match', backref='tournament', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player3_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player4_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score1 = db.Column(db.Integer, nullable=True)
    score2 = db.Column(db.Integer, nullable=True)
    score3 = db.Column(db.Integer, nullable=True)
    score4 = db.Column(db.Integer, nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    player1 = db.relationship('Player', foreign_keys=[player1_id])
    player2 = db.relationship('Player', foreign_keys=[player2_id])
    player3 = db.relationship('Player', foreign_keys=[player3_id])
    player4 = db.relationship('Player', foreign_keys=[player4_id])
    winner = db.relationship('Player', foreign_keys=[winner_id])
