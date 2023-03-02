# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Player
from boardgametracker import db
from boardgametracker.constants import *

class PlayerCollection(Resource):
    def get(self):

        # create list
        data_object = []
        
        # query players in Player
        player_list = Player.query.all()
        
        # append players to list with keys
        for player in player_list:
            data_object.append({
                'name': player.name
            })
            
        #no need to rebuild the response to json
        response = data_object
        
        return response, 200
    
class PlayerItem(Resource):
    def get(self, player):
        pass

