# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Ruleset
from boardgametracker import db
from boardgametracker.constants import *
import datetime
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class RulesetCollection(Resource):
    def get(self):
        '''
        Get all rulesets
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        for ruleset in Ruleset.query.all():
            data_object.append({
                'name': ruleset.name,
                'game_id': ruleset.game_id
            })
            
        response = data_object
        
        return response, 200
    
    def post(self):
        '''
        Add a new ruleset
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            ruleset = Ruleset(
                name=request.json["name"]
            )
            db.session.add(ruleset)
            db.session.commit()
        except KeyError:
            abort(400)

        return Response(status=201)
    
class RulesetItem(Resource):
    def get(self, ruleset):
        '''
        Get information about a ruleset
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        return ruleset.serialize()
        
    def put(self, ruleset):
        '''
        Change information of a ruleset
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        ruleset.deserialize(request.json)
        try:
            db.session.add(ruleset)
            db.session.commit()
        except IntegrityError:
            raise Conflict(409)
            
    def delete(self, ruleset):
        '''
        Delete a ruleset
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(ruleset)
        db.session.commit()

        return Response(status=204)
        
class RulesetFor(Resource):
    def get(self, game):
        '''
        Get all rulesets for a certain game
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        for ruleset in Ruleset.query.filter_by(game_id=game):
            data_object.append({
                'name': ruleset.name,
                'game_id': ruleset.game_id
            })
            
        response = data_object
        
        return response, 200