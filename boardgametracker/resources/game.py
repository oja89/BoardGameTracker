# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Game
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker import cache
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class GameCollection(Resource):
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
        name=""
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Game.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        try:
            game = Game(
                name=request.json["name"]
            )
            db.session.add(game)
            db.session.commit()
        except KeyError:
            abort(400)
        except IntegrityError:
            raise Conflict(description="Game with name '{name}' already exists.".format(name=name))

        return Response(status=201)
    
class GameItem(Resource):
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
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Game.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        
        game.name = request.json["name"]
        
        try:
            db.session.commit()
        except IntegrityError:
            raise Conflict(description="Game with this name already exists")
            
    def delete(self, game):
        '''
        Delete a game
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(game)
        db.session.commit()

        return Response(status=204)

