# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Match
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType
from boardgametracker import cache

class MatchCollection(Resource):
    @cache.cached(timeout=5)
    def get(self):
        '''
        Get all matches
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        
        data_object = []

        for match in Match.query.all():
            # use serializer
            data_object.append(match.serialize(long=True))
            
        response = data_object
        
        return response, 200
    
    def post(self):
        '''
        Add a new match
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Match.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            match = Match(
                date=datetime.fromisoformat(request.json["date"]),
                turns=request.json["turns"]
            )
            db.session.add(match)
            db.session.commit()
        except KeyError:
            abort(400)

        return Response(status=201)
    
class MatchItem(Resource):
    def get(self, match):
        '''
        Get information about a match
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return match.serialize(long=True)
        
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

