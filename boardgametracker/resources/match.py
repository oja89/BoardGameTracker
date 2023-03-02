# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Match
from boardgametracker import db
from boardgametracker.constants import *

class MatchCollection(Resource):
    def get(self):

        # create list
        data_object = []
        
        # query matches in match
        match_list = Match.query.all()
        
        # append matches to list with keys
        for match in match_list:
            data_object.append({
                'date': match.date.isoformat(),
                'turns': match.turns
            })
            
        #no need to rebuild the response to json
        response = data_object
        
        return response, 200
    
class MatchItem(Resource):
    def get(self, match):
        pass

