"""
Functions for player class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.models import Player
from flask import Response, request
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType


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
        """

        data_object = []

        for player in Player.query.all():
            data_object.append({
                'name': player.name
            })

        response = data_object

        return response, 200

    def post(self):
        """
        Add a new player
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """

        if not request.mimetype == "application/json":
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
        return Response(status=201)

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
