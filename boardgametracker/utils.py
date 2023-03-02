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

        
class TeamConverter(BaseConverter):
    
    def to_python(self, team):
        db_team = Team.query.filter_by(name=team).first()
        if db_team is None:
            raise NotFound
        return db_team
        
    def to_url(self, db_team):
        return db_team.name