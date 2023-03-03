# from example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/utils.py

import json
import secrets
from flask import Response, request, url_for
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.routing import BaseConverter

from boardgametracker.constants import *
from boardgametracker.models import *

class PlayerConverter(BaseConverter):
    
    def to_python(self, player):
        db_player = Player.query.filter_by(name=player).first()
        if db_player is None:
            raise NotFound
        return db_player
        
    def to_url(self, db_player):
        return db_player.name
        
        
class MatchConverter(BaseConverter):
    def to_python(self, match):
        db_match = Match.query.filter_by(id=match).first()
        if db_match is None:
            raise NotFound
        return db_match
        
    def to_url(self, db_match):
        return db_match.id

class GameConverter(BaseConverter):
    
    def to_python(self, game):
        db_game = Game.query.filter_by(name=game).first()
        if db_game is None:
            raise NotFound
        return db_game
        
    def to_url(self, db_game):
        return db_game.name       

       
class TeamConverter(BaseConverter):
    
    def to_python(self, team):
        db_team = Team.query.filter_by(name=team).first()
        if db_team is None:
            raise NotFound
        return db_team
        
    def to_url(self, db_team):
        return db_team.name
        
class RulesetConverter(BaseConverter):
    def to_python(self, ruleset):
        db_ruleset = Ruleset.query.filter_by(id=ruleset).first()
        if db_ruleset is None:
            raise NotFound
        return db_ruleset
        
    def to_url(self, db_ruleset):
        return db_ruleset.id
 
class MapConverter(BaseConverter):
    def to_python(self, map):
        db_map = Map.query.filter_by(id=map).first()
        if db_map is None:
            raise NotFound
        return db_map
        
    def to_url(self, db_map):
        return db_map.id