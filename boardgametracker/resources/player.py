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
from boardgametracker import cache
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

class PlayerCollection(Resource):
    @cache.cached(timeout=5)
    def get(self):
        '''
        Get all players
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        data_object= []
        
        for player in Player.query.all():
            data_object.append({
                'name': player.name
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
                409
            )

        return Response(status=201)
    
class PlayerItem(Resource):
    def get(self, player):
        '''
        Get information about a player
        
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return player.serialize(long=True)
        
    def put(self, player):
        '''
        Change information of a player
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Player.get_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        player.deserialize(request.json)
        try:
            db.session.add(player)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                409
            )
        
        return Response(status=204)
            
    def delete(self, player):
        '''
        Delete a player
        
        From https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        ''' 
        db.session.delete(player)
        db.session.commit()
        

        return Response(status=204)

