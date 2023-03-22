"""
Functions for game class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker.models import Game
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
        """
        return game.serialize()

    def put(self, game):
        """
        Change information of a game


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
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
        """
        Delete a game

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        """
        db.session.delete(game)
        db.session.commit()

        return Response(status=204)
