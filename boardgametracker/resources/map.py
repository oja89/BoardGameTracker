# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Map
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class MapCollection(Resource):
    def get(self):
        '''
        Get all maps
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        for map in Map.query.all():
            data_object.append({
                'name': map.name
            })
            
        response = data_object
        
        return response, 200
    
    def post(self):
        '''
        Add a new map
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Map.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            map = Map(
                name=request.json["name"]
            )
            db.session.add(map)
            db.session.commit()
        except KeyError:
            abort(400)

        return Response(status=201)
    
class MapItem(Resource):
    def get(self, map):
        '''
        Get information about a map
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        return map.serialize()
        
    def put(self, map):
        '''
        Change information of a map
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Map.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        map.deserialize(request.json)
        try:
            db.session.add(map)
            db.session.commit()
        except IntegrityError:
            raise Conflict(409)
            
    def delete(self, map):
        '''
        Delete a map
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(map)
        db.session.commit()

        return Response(status=204)
        
class MapsFor(Resource):
    def get(self, game):
        '''
        Get all maps for a certain game
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        for map in Map.query.filter_by(game_id=game):
            data_object.append({
                'name': map.name
            })
            
        response = data_object
        
        return response, 200