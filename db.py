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
    name = db.Column(db.String(64), nullable=False)

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Maps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    game_id = db.Column(db.Integer, db.ForeignKey("games.id", ondelete="SET NULL"))
    
class Rulesets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    game_id = db.Column(db.Integer, db.ForeignKey("games.id", ondelete="SET NULL"))
    

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # check how datetime is done, use string as a placeholder
    date = db.Column(db.String(64), nullable=False)
    turns = db.Column(db.Integer, nullable=False)
    
    game_id = db.Column(db.Integer, db.ForeignKey("games.id", ondelete="SET NULL"))
    ruleset_id = db.Column(db.Integer, db.ForeignKey("rulesets.id", ondelete="SET NULL"))
    map_id = db.Column(db.Integer, db.ForeignKey("maps.id", ondelete="SET NULL"))

class Player_results(db.Model):
    row = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, nullable=False)
    
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id", ondelete="SET NULL"))
    player_id = db.Column(db.Integer, db.ForeignKey("players.id", ondelete="SET NULL"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="SET NULL"))
    
class Team_results(db.Model):
    row = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id", ondelete="SET NULL"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="SET NULL"))