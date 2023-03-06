'''
Functions for game class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
'''

from jsonschema import validate, ValidationError
from flask import Response, request, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Game
from boardgametracker import db
from boardgametracker import cache
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class GameCollection(Resource):
    '''
    Collection of games
    '''
    @cache.cached(timeout=5)
    def get(self):
        '''
        Get all games
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        data_object= []

        for game in Game.query.all():
            data_object.append(game.serialize(long=True))

        response = data_object

        return response, 200

    def post(self):
        '''
        Add a new game
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Game.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            game = Game(
                name=request.json["name"]
            )
            db.session.add(game)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            name=request.json["name"]
            raise Conflict(description=f"Game with name '{name}' already exists.")
        return Response(status=201)

class GameItem(Resource):
    '''
    One item of game
    '''
    def get(self, game):
        '''
        Get information about a game
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return game.serialize()

    def put(self, game):
        '''
        Change information of a game
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Game.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        game.name = request.json["name"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description=f"Game with name '{game.name}' already exists.")

        return Response(status=204)

    def delete(self, game):
        '''
        Delete a game
        
        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        '''
        db.session.delete(game)
        db.session.commit()

        return Response(status=204)
