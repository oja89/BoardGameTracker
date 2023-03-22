"""
Functions for game class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker.models import Game, Map, Ruleset
from boardgametracker.utils import BGTBuilder
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType


class GameCollection(Resource):
    """
    Collection of games
    """

    @cache.cached(timeout=5)
    def get(self):
        """
        Get all games


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - game
        description: Get all games
        responses:
            200:
                description: List of games
                content:
                    application/json:
                        example:
                            - name: CS:GO
                            - name: Terraforming Mars
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.gamecollection"))
        body.add_control_add_game()
        body["items"] = []

        for game in Game.query.all():
            item = BGTBuilder(game.serialize(long=True))
            # create controls
            item.add_control("self", url_for("api.gameitem", game=game))
            item.add_control("profile", GAME_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self):
        """
        Add a new game


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

                ---
        tags:
            - game
        description: Add a new game
        requestBody:
            description: JSON containing data for the game
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Game'
                    example:
                        name: Chess
        responses:
            201:
                description: Game added
                headers:
                    Location:
                        description: URI of the game
                        schema:
                            type: string
            409:
                description: Name already exists
        """
        if not request.mimetype == JSON:
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
            name = request.json["name"]
            raise Conflict(description=f"Game with name '{name}' already exists.")
        return Response(
            status=201,
            headers={"Location": url_for("api.gameitem", game=game)
                     }
        )


class GameItem(Resource):
    """
    One item of game
    """

    def get(self, game):
        """
        Get information about a game


        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        modified to use MasonBuilder after ex3, and added YAML
        ---
        tags:
            - game
        description: Get one game
        responses:
            200:
                description: Game and stuff
                content:
                    application/json:
                        example:
                            - name: CS:GO
                              maps:
                                - Dust
                                - inferno
                              rulesets:
                                - competitive
                                - arcade
        """

        body = BGTBuilder(game.serialize(long=True))
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.gameitem", game=game))
        body.add_control("profile", PLAYER_PROFILE)
        body.add_control("collection", url_for("api.gamecollection"))
        body.add_control_put("edit", "Edit this game", url_for("api.gameitem", game=game), schema=Game.get_schema())
        body.add_control_delete("Delete this game", url_for("api.gameitem", game=game))


        # TODO: IS THIS THE RIGHT WAY?
        # game and rulesets and controls


        # needs to pass the game
        body.add_control_add_map(game)
        body.add_control_add_ruleset(game)


        # if map(s) exists, add route to edit and delete it
        if game.map is not None:
            body["maps"] = []
            # for each "row" in this games results:
            for map_ in game.map:
                item = BGTBuilder(map_.serialize(long=False))
                item.add_control_put("edit",
                                 "Edit this map",
                                 url_for("api.mapitem", game=game, map_=map_.id),
                                Map.get_schema()
                                )
                item.add_control_delete("Delete this map", url_for("api.mapitem", game=game, map_=map_.id))
                body["maps"].append(item)


        # if ruleset(s) exists, add route to edit and delete it
        if game.ruleset is not None:
            body["rulesets"] = []
            # for each "row" in this games results:
            for ruleset in game.ruleset:
                item = BGTBuilder(ruleset.serialize(long=False))
                item.add_control_put("edit",
                                 "Edit this ruleset",
                        url_for("api.rulesetitem", game=game, ruleset=ruleset.id),
                                Ruleset.get_schema()
                                )
                item.add_control_delete("Delete this ruleset",
                        url_for("api.rulesetitem", game=game, ruleset=ruleset.id)
                                )
                body["rulesets"].append(item)


        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def put(self, game):
        """
        Change information of a game


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        added YAML
                ---
        tags:
            - game
        description: Modify a game
        parameters:
            - $ref: '#/components/parameters/game_name'
        requestBody:
            description: JSON containing new data for the game
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Game'
                    example:
                        name: Chess
        responses:
            204:
                description: Game modified, return new URI
                headers:
                    Location:
                        description: URI of the match
                        schema:
                            type: string
                        example: "/api/Game/Chess"
            409:
                description: Name exists already
        """
        if not request.mimetype == JSON:
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

        # return the location?
        return Response(status=204, headers={
            "Location": url_for("api.gameitem", game=game)
                }
                        )

    def delete(self, game):
        """
        Delete a game

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

        YAML added
        ---
        tags:
            - game
        description: Delete a game
        parameters:
            - $ref: '#/components/parameters/game_name'
        responses:
            204:
                description: Game deleted, nothing to return
        """

        db.session.delete(game)
        db.session.commit()

        return Response(status=204)
