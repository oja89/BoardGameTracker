"""
Functions for map class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, abort, url_for
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import JSON, MASON, MAP_PROFILE, LINK_RELATIONS_URL
from boardgametracker.models import Map
from boardgametracker.utils import BGTBuilder

from flask_restful import Resource



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
        body.add_control_all_maps(game)  #NOT SURE IF THIS IS CORRECT!
        body["items"] = []

        #for map_ in Map.query.filter_by(game_id=db_game.id):
        for map_ in game.map:
            # use serializer and BGTBuilder
            item = BGTBuilder(map_.serialize(long=True))
            # create controls for all items
            print(game)
            print(map_)
            item.add_control("self", url_for("api.mapitem", game=game, map_=map_))
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
        if not request.mimetype == JSON:
            raise UnsupportedMediaType

        if game is None:
            # check the correct error message
            # game needs to exist
            abort(400)

        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            map_ = Map(
                name=request.json["name"],
                game_id=game.id
            )
            db.session.add(map_)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(
            status=201,
            headers={"Location": url_for("api.mapitem", game=game, map_=map_)}
        )


class MapItem(Resource):
    """
    One item of map
    """

    def get(self, map_, game=None):
        """
        Get information about a map
        (Game can be in the path, but doesn't make difference)
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - map
        description: Get one map
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/map_id'
        responses:
            200:
                description: Map's information
                content:
                    application/json:
                        example:
                            - name: dust
                            - game_id: 1

        """
        body = BGTBuilder()
        body["item"] = BGTBuilder(map_.serialize(long=True))
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.mapitem", game=game, map_=map_))
        body.add_control("profile", MAP_PROFILE)
        body.add_control("collection", url_for("api.mapcollection", game=game))
        body.add_control_put("edit", "Edit this map", url_for("api.mapitem", game=game, map_=map_),\
        schema=Map.get_schema())
        body.add_control_delete("Delete this map", url_for("api.mapitem", game=game, map_=map_))

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def put(self, game, map_):
        """
        Change information of a map
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - map
        description: Modify map information
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/map_id'
        requestBody:
            description: JSON containing new data for the game
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Map'
                    example:
                        name: Dust
        responses:
            204:
                description: Map information changed
            409:
                description: Integrity error
        """
        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, Map.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            map_.name = request.json["name"]
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)
        return Response(status=204)

    def delete(self, game, map_):
        """
        Delete a map

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

        ---
        tags:
            - map
        description: Delete a map
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/map_id'
        responses:
            204:
                description: Map deleted, nothing to return
        """
        print(map_)
        db.session.delete(map_)
        db.session.commit()

        return Response(status=204)
