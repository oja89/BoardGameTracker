# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Player, Player_result 
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class PlayerResultCollection(Resource):
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
            thisplayer = player.serialize()
            p_results = Player_result.query.filter_by(player_id=thisplayer["id"])
            
        elif player is None:
            thismatch = match.serialize()
            p_results = Player_result.query.filter_by(match_id=thismatch["id"])
        
        else:
        # should not come here
        # both match and player given, that should find an item
        # throw an error
        # Todo: what error?
            abort(400)
            

        for result in p_results:
            data_object.append({
                'match_id': result.match_id,
                'player_id': result.player_id,
                'team_id': result.team_id
            })
            
        response = data_object
        
        return response, 200
