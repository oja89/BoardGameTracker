# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Player, PlayerResult 
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType
from boardgametracker import cache

class PlayerResultCollection(Resource):
    @cache.cached(timeout=5)
    def get(self, match=None, player=None):
        '''
        Get all results
        If match is given, all for that match
        If player given, all for that player
        If both, that should be an item, so abort?
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        # do the query for all
        if player is None and match is None:
            p_results = Player_result.query.all()
            
        # do the query for given player
        elif match is None:
            player_id = player.serialize(long=True)["id"]
            p_results = Player_result.query.filter_by(player_id=player_id)
            
        elif player is None:
            match_id = match.serialize(long=True)["id"]
            p_results = Player_result.query.filter_by(match_id=match_id)
        
        else:
        # should not come here
        # both match and player given, that should find an item
        # throw an error
        # Todo: what error?
            abort(400)
            

        for result in p_results:
            data_object.append(result.serialize(long=True))
            
        response = data_object
        
        return response, 200
