"""
Database models
Schema validations
Serializers

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py
"""

import datetime
import click
import hashlib


from flask.cli import with_appcontext

from boardgametracker import db

class ApiKey(db.Model):
    """
    Authorization, from
    https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/#key-registry
    """
    name = db.Column(db.String(16), primary_key=True)
    key = db.Column(db.String(32), nullable=False, unique=True)
    admin = db.Column(db.Boolean, default=False)

    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=True)

    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()
class Player(db.Model):
    """
    Player class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    # results by player
    player_result = db.relationship("PlayerResult", back_populates="player")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """

        # get all results of the player listed too

        if not long:
            return {"name": self.name}

        return {
            "name": self.name,
            "id": self.id,
            "matches": len(self.player_result)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
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
    """
    Team class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    # result - team relation
    team_result = db.relationship("TeamResult", back_populates="team")
    # team - player_result relation
    match_player = db.relationship("PlayerResult", back_populates="team")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {"name": self.name}

        return {
            "name": self.name,
            "id": self.id,
            "matches": len(self.team_result)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Team's  name",
            "type": "string"
        }
        return schema


class Game(db.Model):
    """
    Game class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    # map - game relationship
    map = db.relationship("Map", back_populates="game")
    # ruleset - game relationship
    ruleset = db.relationship("Ruleset", back_populates="game")
    # match - game relationship
    match = db.relationship("Match", back_populates="game")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {"name": self.name}

        return {
            "name": self.name,
            "id": self.id,
            "matches": len(self.match)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
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


class Map(db.Model):
    """
    map class
    """
    id = db.Column(db.Integer, primary_key=True)
    # different games might have same names for maps
    # removed uniqueness
    name = db.Column(db.String(16), nullable=False)

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id", ondelete="SET NULL")
    )

    # map - game relationship
    game = db.relationship("Game", back_populates="map")

    # match - map relationship
    match = db.relationship("Match", back_populates="map")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {
                "name": self.name,
                "id": self.id
            }

        return {
            "name": self.name,
            "id": self.id,
            "game": self.game.serialize()["name"],
            "matches": len(self.match)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
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
    """
    Ruleset class
    """
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
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {"name": self.name}

        return {
            "name": self.name,
            "id": self.id,
            "game": self.game.serialize()["name"],
            "matches": len(self.match)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
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


class Match(db.Model):
    """
    Match class
    """
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
    team_result = db.relationship("TeamResult", back_populates="match")
    player_result = db.relationship("PlayerResult", back_populates="match")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {"date": self.date.isoformat()}

        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "turns": self.turns,

            # serializers to get more details
            # use "and" to make it work even if there are nulls
            "game_name": self.game and self.game.serialize()["name"],
            "map_name": self.map and self.map.serialize()["name"],
            "ruleset_name": self.ruleset and self.ruleset.serialize()["name"]
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
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
        props["game_id"] = {
            "description":"Game's id",
            "type":"number"
        }
        props["map_id"] = {
            "description":"Map's id",
            "type":"number"
        }
        props["ruleset_id"] = {
            "description":"Ruleset's id",
            "type":"number"
        }
        return schema


class PlayerResult(db.Model):
    """
    PlayerResult class
    """
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
    # team relation
    team = db.relationship("Team", back_populates="match_player")

    def serialize(self, long=False):
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {
                "player": self.player.serialize()["name"],
                # use "and" to deal with None
                "team": self.team_id and self.team.serialize()["name"],
                "points": self.points
            }

        return {
            "id": self.id,
            "points": self.points,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "player": self.player.serialize()["name"],
            "team_id": self.team_id,
            "team": self.team_id and self.team.serialize()["name"]
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
        schema = {
            "type": "object",
            "required": ["points", "player_id", "team_id"]
        }
        props = schema["properties"] = {}
        props["points"] = {
            "description": "Player's points",
            "type": "number"
        }
        props["player_id"] = {
            "description": "ID of player",
            "type": "number"
        }
        # props["match_id"] = {
        #    "description": "ID of match",
        #    "type": "number"
        # }
        props["team_id"] = {
            "description": "ID of team",
            "type": "number"
        }
        return schema


class TeamResult(db.Model):
    """
    TeamResult class
    """
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
        """
        Convert data to dictionary format
        long=True gives more info
        """
        if not long:
            return {
                "team": self.team_id and self.team.name,
                "points": self.points,
                "order": self.order
            }

        return {
            "team": self.team_id and self.team.name,
            "team_id": self.team_id,
            "points": self.points,
            "order": self.order,
            #"match_info": self.match.serialize(long=True)
        }

    @staticmethod
    def get_schema():
        """
        json verification
        """
        schema = {
            "type": "object",
            "required": ["points"]
        }
        props = schema["properties"] = {}
        props["points"] = {
            "description": "Team's points",
            "type": "number"
        }
        props["order"] = {
            "description": "Finishing order of the team",
            "type": "number"
        }
        props["match_id"] = {
            "description": "ID of match",
            "type": "number"
        }
        props["team_id"] = {
            "description": "ID of team",
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
    """
    Create the database
    """
    db.create_all()


@click.command("testgen")
@with_appcontext
def generate_test_data():
    """
    Populate the database with some example data
    """
    # Populate database

    # add a player
    player = Player(name='Nick')
    db.session.add(player)
    db.session.commit()

    print(f"Added player {player.name} as {player}")

    # add a team
    team = Team(name='Foxes')
    db.session.add(team)
    db.session.commit()

    print(f"Added team {team.name} as {team}")

    # add a game
    game = Game(name='CS:GO')
    db.session.add(game)
    db.session.commit()

    print(f"Added game {game.name} as {game}")

    # add map for the game
    map_ = Map(
        name='dust',
        game_id=game.id
    )
    db.session.add(map_)
    db.session.commit()

    print(f"Added map {map_.name} as {map_} for game {game.name} {game}")

    # add ruleset for the game
    rset = Ruleset(
        name='competitive',
        game_id=game.id
    )
    db.session.add(rset)
    db.session.commit()

    print(f"Added ruleset {rset.name} as {rset} for game {game.name} {game}")

    ### Match
    # match info, use game, map, ruleset
    match = Match(
        date=datetime.date(2022, 12, 25),
        turns=30,
        game_id=game.id,
        map_id=map_.id,
        ruleset_id=rset.id
    )
    db.session.add(match)
    db.session.commit()

    print(f"Added match on date {match.date} as {match}, with {game}, {map_}, {rset}")

    # team results, use match, team
    tres = TeamResult(
        points=56,
        order=2,
        match_id=match.id,
        team_id=team.id
    )
    db.session.add(tres)
    db.session.commit()

    print(f"Added team score {tres.points} as {tres} for match {match}")

    # player results, use match, player, team
    pres = PlayerResult(
        points=23,
        match_id=match.id,
        team_id=team.id,
        player_id=player.id
    )
    db.session.add(pres)
    db.session.commit()

    print(f"Added player score {pres.points} as {pres}")

    db.session.commit()


@click.command("adminkey")
@with_appcontext
def generate_admin_key():
    """
    Generate API key for admin
    from:
    https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py
    """
    import secrets
    token = secrets.token_urlsafe()
    db_key = ApiKey(
        name="admin",
        key=ApiKey.key_hash(token),
        admin=True
    )
    db.session.add(db_key)
    db.session.commit()
    print(token)

@click.command("userkey")
@with_appcontext
def generate_user_key():
    """
    Generate API key for user
    from:
    https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py
    """
    import secrets
    token = secrets.token_urlsafe()
    db_key = ApiKey(
        #push hash to name now
        # TODO: do not do that.
        name=token,
        #hardcoded player id
        player_id=1,
        key=ApiKey.key_hash(token)
    )
    db.session.add(db_key)
    db.session.commit()
    print(token)