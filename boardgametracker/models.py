### from sensorhub example 
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py

import click
import datetime
import hashlib
from flask.cli import with_appcontext
from boardgametracker import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    # results by player
    player_result = db.relationship("Player_result", back_populates="player")

    def serialize(self, long=False):
        # get all results of the player listed too
        
        if not long: 
            return {"name": self.name}
        else:
            result_list = []
            # self.result is a Player_result class object
            for i in self.player_result:
                result = i.serialize(long=True)
                result_list.append(result)
            return {
                "name": self.name,
                "id": self.id,
                "list_of_results": result_list
            }
        
    def deserialize(self, doc):
        self.name = doc["name"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Player's  name",
            "type": "string"
        }
        return schema

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)
    
    # result - team relation
    team_result = db.relationship("Team_result", back_populates="team")
    
    def serialize(self, long=False):
        if not long:
            return {"name": self.name}
        else:
            result_list = []
            # result is a Team_result class object
            for i in self.team_result:
                result = i.serialize(long=True)
                result_list.append(result)
            return {
                "name": self.name,
                "id": self.id,
                # user serializer to get team_result database
                "results": result_list
            }
        
    def deserialize(self, doc):
        self.name = doc["name"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Teams's  name",
            "type": "string"
        }
        return schema

class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id", ondelete="SET NULL")
        )
        
    # map - game relationship
    game = db.relationship("Game", back_populates="map")
        
    # match - map relationship
    match = db.relationship("Match", back_populates="map")
    
    def serialize(self, long=False):
        if not long:
            return {"name": self.name}
        
    def deserialize(self, doc):
        self.name = doc["name"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Map's  name",
            "type": "string"
        }
        return schema

class Ruleset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id", ondelete="SET NULL")
        )
    
    # ruleset - game relationship
    game = db.relationship("Game", back_populates="ruleset")
    match = db.relationship("Match", back_populates="ruleset")
        
    def serialize(self, long=False):
        if not long:
            return {"name": self.name}
        
    def deserialize(self, doc):
        self.name = doc["name"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Ruleset's  name",
            "type": "string"
        }
        return schema

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)
    
    # map - game relationship
    map = db.relationship("Map", back_populates="game")
    # ruleset - game relationship
    ruleset = db.relationship("Ruleset", back_populates="game")
    # match - game relationship
    match = db.relationship("Match", back_populates="game")
    
    def serialize(self, long=False):
        if not long:
            return {"name": self.name}
        else:
            return {
                "name": self.name,
                "id": self.id,
            }           
        
    def deserialize(self, doc):
        self.name = doc["name"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Game's name",
            "type": "string"
        }
        return schema

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    turns = db.Column(db.Integer, nullable=False)
    
    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id", ondelete="SET NULL")
        )
    ruleset_id = db.Column(
        db.Integer,
        db.ForeignKey("ruleset.id", ondelete="SET NULL")
        )
    map_id = db.Column(
        db.Integer,
        db.ForeignKey("map.id", ondelete="SET NULL")
        )
        
    game = db.relationship("Game", back_populates="match")
    map = db.relationship("Map", back_populates="match")
    ruleset = db.relationship("Ruleset", back_populates="match")
    team_result = db.relationship("Team_result", back_populates="match")
    player_result = db.relationship("Player_result", back_populates="match")
        
    def serialize(self, long=False):
        if not long:
            return {"date": self.date.isoformat()}
        else:
            # get results
            p_result_list = []
            t_result_list = []
            # self.player_result is a Player_result class object
            for i in self.player_result:
                p_result = i.serialize(long=False)
                p_result_list.append(p_result)
            # self.team is a Team_result class object
            for i in self.team_result:
                t_result = i.serialize(long=False)
                t_result_list.append(t_result)
            return {
                "date": self.date.isoformat(),
                "turns": self.turns,
                "results": {
                    "player_results": p_result_list,
                    "team_results": t_result_list
                    },
                
                
                # serializers to get more details
                "game_name": self.game.serialize()["name"],
                "map_name": self.map.serialize()["name"],
                "ruleset_name": self.ruleset.serialize()["name"]
            }
        
    def deserialize(self, doc):
        self.date = datetime.fromisoformat(doc["date"])
        self.turns = doc["turns"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["date", "turns"]
        }
        props = schema["properties"] = {}
        props["date"] = {
            "description": "Match's date",
            "type": "string",
            "format": "date-time"
        }
        props["turns"] = {
            "description": "Match's turns",
            "type": "number"
                    
        }   
        return schema    

class Player_result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Float, nullable=False)
    
    match_id = db.Column(
        db.Integer,
        db.ForeignKey("match.id", ondelete="CASCADE")
        )
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("player.id", ondelete="SET NULL")
        )
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("team.id", ondelete="SET NULL")
        )

    # result - player relation
    player = db.relationship("Player", back_populates="player_result")
    # result - match relation
    match = db.relationship("Match", back_populates="player_result")
    
    def serialize(self, long=False):
        if not long:
            return {
            "player": self.player.serialize()["name"],
            "points": self.points
            }
        else:
            return {
                "points": self.points,
                "match_id": self.match_id,
                "player_id": self.player_id,
                "team_id": self.team_id,
                # use match-serializer
                "match_info": self.match.serialize(long=True)
            }

        
    def deserialize(self, doc):
        self.points = doc["points"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["points"]
        }
        props = schema["properties"] = {}
        props["points"] = {
            "description": "Player's points",
            "type": "number"
        }
        
        return schema
 
    
class Team_result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Float, nullable=False)
    order = db.Column(db.Integer, nullable=False)

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("match.id", ondelete="CASCADE")
        )
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("team.id", ondelete="SET NULL")
        )
       
    # result - team relation
    team = db.relationship("Team", back_populates="team_result")
    # result - match relation
    match = db.relationship("Match", back_populates="team_result")
       
    def serialize(self, long=False):
        if not long:
            return {
            "team": self.team.serialize()["name"],
            "points": self.points,
            "order" : self.order
            }
        else:
            return {
                "team": self.team.serialize(),
                "points": self.points,
                "order" : self.order
            }
            
    def deserialize(self, doc):
        self.points = doc["points"]
        self.order = doc["order"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["points"]
        }
        props = schema["properties"] = {}
        props["points"] = {
            "description": "Player points",
            "type": "number"
        }
        props["order"] = {
            "description": "Order of team",
            "type": "number"
        }
        
        return schema



# commands for cli
# placed here to ensure that the models are loaded.
# call them from __init__.py


# from sensorhub example 
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    
    
@click.command("testgen")
@with_appcontext
def generate_test_data():
    ### Populate database

    # add a player
    p = Player(name='Nick')
    db.session.add(p)
    db.session.commit()

    print(f"Added player {p.name} as {p}")

    # add a team
    t = Team(name='Foxes')
    db.session.add(t)
    db.session.commit()

    print(f"Added team {t.name} as {t}")

    #add a game
    g = Game(name='CS:GO')
    db.session.add(g)
    db.session.commit()

    print(f"Added game {g.name} as {g}")

    # add map for the game
    m = Map(
        name='dust',
        game_id=g.id
        )
    db.session.add(m)
    db.session.commit()

    print(f"Added map {m.name} as {m} for game {g.name} {g}")

    # add ruleset for the game
    r = Ruleset(
        name='competitive',
        game_id=g.id
        )
    db.session.add(r)
    db.session.commit()

    print(f"Added ruleset {r.name} as {r} for game {g.name} {g}")

    ### Match
    # match info, use game, map, ruleset
    m1 = Match(
        date=datetime.date(2022, 12, 25),
        turns=30,
        game_id=g.id,
        map_id=m.id,
        ruleset_id=r.id
        )
    db.session.add(m1)
    db.session.commit()

    print(f"Added match on date {m1.date} as {m1}, with {g}, {m}, {r}")

    # team results, use match, team
    tr = Team_result(
        points=56,
        order=2,
        match_id=m1.id,
        team_id=t.id
        )
    db.session.add(tr)
    db.session.commit()

    print(f"Added team score {tr.points} as {tr} for match {m1}")

    # player results, use match, player, team
    pr = Player_result(
        points=23,
        match_id=m1.id,
        team_id=t.id,
        player_id=p.id
        )
    db.session.add(pr)
    db.session.commit()

    print(f"Added player score {pr.points} as {pr}")

    db.session.commit()
