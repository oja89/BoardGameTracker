"""
Functions for player class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import *
from boardgametracker.models import Player
from boardgametracker.utils import BGTBuilder


class PlayerCollection(Resource):
    """
    Collection of players
    """
    @cache.cached(timeout=5)
    def get(self):
        """
        Get all players
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        modified to use MasonBuilder after ex3, and added YAML
        ---
        tags:
            - player
        description: Get all players
        responses:
            200:
                description: List of players
                content:
                    application/json:
                        example:
                            - name: Bob
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playercollection"))
        body.add_control_add_player()
        body["items"] = []

        for player in Player.query.all():
            item = BGTBuilder(player.serialize(long=True))
            # create controls
            item.add_control("self", url_for("api.playeritem", player=player))
            item.add_control("profile", PLAYER_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self):
        """
        Add a new player
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        added mason and openapi
        ---
        tags:
            - player
        description: Add a new player
        requestBody:
            description: JSON containing data for the player
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Player'
                    example:
                        name: Tim
        responses:
            201:
                description: Player added
                headers:
                    Location:
                        description: URI of the player
                        schema:
                            type: string
            409:
                description: Name already exists
        """

        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, Player.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            player = Player(
                name=request.json["name"]
            )
            db.session.add(player)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            name = request.json["name"]
            raise Conflict(description=f"Player with name '{name}' already exists.")
        return Response(
                status=201,
                headers={"Location": url_for("api.playeritem", player=player)
                 }
        )

class PlayerItem(Resource):
    """
    One item of player
    """
    def get(self, player):
        """
        Get information about a player
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        return player.serialize(long=True)

    def put(self, player):
        """
        Change information of a player
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Player.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        player.name = request.json["name"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description=f"Player with name '{player.name}' already exists.")

        return Response(status=204)

    def delete(self, player):
        """
        Delete a player
        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        """
        db.session.delete(player)
        db.session.commit()

        return Response(status=204)
