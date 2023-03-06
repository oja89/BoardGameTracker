'''
Functions for map class objects

from sensorhub example 
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
'''
from jsonschema import validate, ValidationError
from flask import Response, request, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Map
from boardgametracker import db
from boardgametracker import cache
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

class MapCollection(Resource):
    '''
    Collection of maps
    '''
    @cache.cached(timeout=5)
    def get(self, game=None):
        '''
        Get all maps
        If game given, all for that game

        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        # do the query for all
        if game is None:
            maps = Map.query.all()

        # do the query for given game
        else:
            game_id = game.serialize(long=True)["id"]
            maps = Map.query.filter_by(game_id=game_id)

        for map_ in maps:
            # use serializer
            data_object.append(map_.serialize(long=True))

        response = data_object

        return response, 200

    def post(self, game=None):
        '''
        Add a new map
        Cannot add a map without a game

        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        if game is None:
        # check the correct error message
        # game needs to exist
            abort(400)
        else:
            game_id = game.serialize(long=True)["id"]

        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            map_ = Map(
                name = request.json["name"],
                game_id = game_id
            )
            db.session.add(map_)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(status=201)

class MapItem(Resource):
    '''
    One item of team
    '''
    def get(self, map_, game=None):
        '''
        Get information about a map
        (Game can be in the path, but doesn't make difference)
        
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        return map_.serialize(long=True)

    def put(self, map_):
        '''
        Change information of a map
        
        
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        map_.deserialize(request.json)
        try:
            map_ = Map(
            name=request.json["name"],
            game_id=request.json["game_id"]
            )
            db.session.add(map_)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)
        return Response(status=201)

    def delete(self, map_):
        '''
        Delete a map
        
        From 
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        '''
        db.session.delete(map_)
        db.session.commit()

        return Response(status=204)
