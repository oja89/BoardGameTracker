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
import datetime

class MatchCollection(Resource):
    def get(self):
        '''
        Get all matches
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        
        data_object = []
        match_list = Match.query.all()
        for match in match_list:
            data_object.append({
                'date': match.date.isoformat(),
                'turns': match.turns
            })
            
        response = data_object
        
        return response, 200
    
    def post(self):
        '''
        Add a new player
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Player.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            player = Player(
                name=request.json["name"]
            )
            db.session.add(player)
            db.session.commit()
        except KeyError:
            abort(400)
        except IntegrityError:
            raise Conflict(
                409,
                description="Player with name '{name}' already exists.".format(
                    **request.json
                )
            )

        return Response(status=201)
    
class MatchItem(Resource):
    def get(self, match):
        '''
        Get information about a match
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return match.serialize()
        
    def put(self, match):
        '''
        Change information of a match
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Match.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        match.deserialize(request.json)
        try:
            db.session.add(match)
            db.session.commit()
        except IntegrityError:
            raise Conflict(409)
            
    def delete(self, match):
        '''
        Delete a match
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(match)
        db.session.commit()

        return Response(status=204)

