"""
Functions for ruleset class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, abort, url_for
from flask_restful import Resource
from boardgametracker.constants import *
from boardgametracker.utils import BGTBuilder
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.models import Ruleset


class RulesetCollection(Resource):
    """
    Collection of rulesets
    """
    @cache.cached(timeout=5)
    def get(self, game):
        """
        Get all rulesets
        If game given, all for that game
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        
        ---
        tags:
            - rulesets
        description: Get all rulesets for one game
        parameters:
            - $ref: '#/components/parameters/game_name'
        responses:
            200:
                description: List of rulesets
                content:
                    application/json:
                        example:
                            - name: Competitive
                            - name: Wingman
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.rulesetcollection", game=game))
        body.add_control_add_ruleset(game) 
        body["items"] = []

        # append objects to list
        for ruleset in game.ruleset:
            # use serializer and BGTBuilder
            item = BGTBuilder(ruleset.serialize(long=True))
            # create controls for all items
            item.add_control("self", url_for("api.rulesetitem", game=game.name, ruleset=ruleset.id))
            item.add_control("profile", RULESET_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self, game=None):
        """
        Add a new ruleset
        Cannot add a ruleset without a game
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
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
            validate(request.json, Ruleset.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            ruleset = Ruleset(
                name=request.json["name"],
                game_id=game_id
            )
            db.session.add(ruleset)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)
        # ruleset names are not unique, no need to test that

        return Response(status=201)

class RulesetItem(Resource):
    """
    One item of ruleset
    """
    def get(self, ruleset, game=None):
        """
        Get information about a ruleset
        (Game can be in the path, but doesn't make difference)
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """

        return ruleset.serialize(long=True)

    def put(self, ruleset):
        """
        Change information of a ruleset
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            ruleset.name = request.json["name"]
            db.session.add(ruleset)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)

        return Response(status=204)

    def delete(self, ruleset):
        """
        Delete a ruleset
        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        """
        db.session.delete(ruleset)
        db.session.commit()

        return Response(status=204)
