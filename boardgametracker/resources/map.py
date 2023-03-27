"""
Functions for map class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker.models import Map, Game
from boardgametracker.utils import BGTBuilder
from flask import Response, request, abort, url_for
from flask import Response, request, abort
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.models import Map


class MapCollection(Resource):
    """
    Collection of maps
    """

    @cache.cached(timeout=5)
    def get(self, game):
        """
        Get all maps for the game given
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        
        ---
        tags:
            - map
        description: Get all maps for one game
        parameters:
            - $ref: '#/components/parameters/game_name'
        responses:
            200:
                description: List of maps
                content:
                    application/json:
                        example:
                            - name: Dust
                            - name: Verdun
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.mapcollection", game=game))
        body.add_control_add_map(game)  #NOT SURE IF THIS IS CORRECT!
        body["items"] = []

        #for map_ in Map.query.filter_by(game_id=db_game.id):
        for map_ in game.map:
            # use serializer and BGTBuilder
            item = BGTBuilder(map_.serialize(long=True))
            # create controls for all items
            item.add_control("self", url_for("api.mapitem", game=game.name, map_=map_.id))
            item.add_control("profile", MAP_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self, game):
        """
        Add a new map
        Cannot add a map without a game

        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        
        ---
        tags:
            - map
        description: Add a new map
        parameters:
            - $ref: '#/components/parameters/game_name'
        requestBody:
            description: JSON containing data for the map
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Map'
                    example:
                        name: Sauna
                        game_id: 1
        responses:
            201:
                description: Map added
                headers:
                    Location:
                        description: URI of the match
                        schema:
                            type: string
                        example: "asdfadf"
            400:
                description: Key error
        """
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType

        if game is None:
            # check the correct error message
            # game needs to exist
            abort(400)
        else:
            game_id = game.serialize(long=True)["id"]

        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            map_ = Map(
                name=request.json["name"],
                game_id=game_id
            )
            db.session.add(map_)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(status=201)


class MapItem(Resource):
    """
    One item of team
    """

    def get(self, map_, game=None):
        """
        Get information about a map
        (Game can be in the path, but doesn't make difference)
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """

        return map_.serialize(long=True)

    def put(self, map_):
        """
        Change information of a map
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

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
        return Response(status=204)

    def delete(self, map_):
        """
        Delete a map

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        """
        db.session.delete(map_)
        db.session.commit()

        return Response(status=204)
