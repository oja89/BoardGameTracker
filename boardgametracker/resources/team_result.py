# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Player, Team_result 
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class TeamResultCollection(Resource):
    def get(self, match=None, team=None):
        '''
        Get all results
        If match is given, all for that match
        If team given, all for that team
        If both, that should be an item, so abort?
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        # do the query for all
        if team is None and match is None:
            t_results = Team_result.query.all()
            
        # do the query for given team
        elif match is None:
            thisteam = team.serialize()
            t_results = Team_result.query.filter_by(team_id=thisteam["id"])
            
        elif team is None:
            thismatch = match.serialize()
            t_results = Team_result.query.filter_by(match_id=thismatch["id"])
        
        else:
        # should not come here
        # both match and team given, that should find an item
        # throw an error
        # Todo: what error?
            abort(400)
            

        for result in t_results:
            data_object.append({
                'points': result.points,
                'order': result.order,
                'match_id': result.match_id,
                'team_id': result.team_id
            })
            
        response = data_object
        
        return response, 200
