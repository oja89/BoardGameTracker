# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Team
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker import cache
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class TeamCollection(Resource):
    @cache.cached(timeout=5)
    def get(self):
        '''
        Get all teams
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []
        
        for team in Team.query.all():
            data_object.append({
                'name': team.name
            })
            
        response = data_object
        
        return response, 200
        
    def post(self):
        '''
        Add a new team
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        name = ""

        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Team.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            team = Team(
                name=request.json["name"]
            )
            db.session.add(team)
            db.session.commit()
        except KeyError:
            abort(400)
        except IntegrityError:
            raise Conflict(description="Team with name '{name}' already exists.".format(name=name))
        return Response(status=201)

class TeamItem(Resource):
    def get(self, team):
        '''
        Get information about a team
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return team.serialize(long=True)
        
    def put(self, team):
        '''
        Change information of a team
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Team.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        team.deserialize(request.json)
        try:
            db.session.add(team)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                409,
                description="Team with name '{team}' already exists.".format(
                    **request.json
                )
            )
            
    def delete(self, team):
        '''
        Delete a team
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(team)
        db.session.commit()

        return Response(status=204)

