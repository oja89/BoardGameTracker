# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/location.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from boardgametracker import db

class PlayerCollection(Resource):
    def get(self):
        pass
    
class PlayerItem(Resource):
    def get(self, player):
        db_player = Players.query.filter_by(name=player).first()
        if db_player is None:
            return create_error_response(
                404, "Not found",
                f"No player was found with the name {player}."
            )
    
