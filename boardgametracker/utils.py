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