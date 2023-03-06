'''
Functions for team class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
'''

from jsonschema import validate, ValidationError
from flask import Response, request, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Team
from boardgametracker import db
from boardgametracker import cache
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class TeamCollection(Resource):
    '''
    Collection of teams
    '''
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

        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Team.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            team = Team(
                name=request.json["name"]
            )
            db.session.add(team)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)
        except IntegrityError:
            db.session.rollback()
            name = request.json["name"]
            raise Conflict(description=f"Team with name '{name}' already exists.")
        return Response(status=201)

class TeamItem(Resource):
    '''
    One item of team
    '''
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
        except ValidationError as err:
            raise BadRequest(description=str(err))

        team.name = request.json["name"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description=f"Team with name '{team.name}' already exists.")

        return Response(status=204)

    def delete(self, team):
        '''
        Delete a team
        
        From 
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        '''
        db.session.delete(team)
        db.session.commit()

        return Response(status=204)
