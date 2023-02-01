from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///maindata.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Maps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    #game_id = db.relationship("id", back_populates="games")
    
class Rulesets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    #game_id = db.relationship("id", back_populates="games")
    

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # check how datetime is done, use string as a placeholder
    date = db.Column(db.String(64), nullable=False)
    turns = db.Column(db.Integer, nullable=False)
    
    #game_id = db.relationship("id", back_populates="games")
    #ruleset_id = db.relationship("id", back_populates="rulesets")
    #map_id = db.relationship("id", back_populates="maps")

class Player_results(db.Model):
    row = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, nullable=False)
    
class Team_results(db.Model):
    row = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, nullable=False)
