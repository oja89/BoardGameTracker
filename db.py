from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
DATABASE = "sqlite:///maindata.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    # games by player
    results = db.relationship("Player_results", back_populates="player")


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

class Maps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("games.id", ondelete="SET NULL")
        )

class Rulesets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("games.id", ondelete="SET NULL")
        )

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    turns = db.Column(db.Integer, nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("games.id", ondelete="SET NULL")
        )
    ruleset_id = db.Column(
        db.Integer,
        db.ForeignKey("rulesets.id", ondelete="SET NULL")
        )
    map_id = db.Column(
        db.Integer,
        db.ForeignKey("maps.id", ondelete="SET NULL")
        )

class Player_results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Float, nullable=False)

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id", ondelete="CASCADE")
        )
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("players.id", ondelete="SET NULL")
        )
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="SET NULL")
        )

    # games by player
    player = db.relationship("Players", back_populates="results")
    
    
class Team_results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Float, nullable=False)
    order = db.Column(db.Integer, nullable=False)

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id", ondelete="CASCADE")
        )
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="SET NULL")
        )
