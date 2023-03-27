"""
Functions for ruleset class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, abort, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import JSON, MASON, RULESET_PROFILE, LINK_RELATIONS_URL
from boardgametracker.models import Ruleset
from boardgametracker.utils import BGTBuilder


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
            - ruleset
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
        body.add_control_get_game(game)
        body.add_control_add_ruleset(game)

        body["items"] = []

        # append objects to list
        for ruleset in game.ruleset:
            # use serializer and BGTBuilder
            item = BGTBuilder(ruleset.serialize(long=True))
            # create controls for all items
            item.add_control("self", url_for("api.rulesetitem", game=game, ruleset=ruleset))
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

        ---
        tags:
            - ruleset
        description: Add a new ruleset
        parameters:
            - $ref: '#/components/parameters/game_name'
        requestBody:
            description: JSON containing data for the map
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Ruleset'
                    example:
                        name: Gungame
                        game_id: 1
        responses:
            201:
                description: Ruleset added
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

        return Response(
            status=201,
            headers={"Location": url_for("api.rulesetitem", game=game, ruleset=ruleset)
                     }
        )


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

        ---
        tags:
            - ruleset
        description: Get one ruleset
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/ruleset_id'
        responses:
            200:
                description: Map's information
                content:
                    application/json:
                        example:
                            - name: competitive
                            - game_id: 1
        """

        body = BGTBuilder()
        body["item"] = BGTBuilder(ruleset.serialize(long=True))
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.rulesetitem", game=game, ruleset=ruleset))
        body.add_control("profile", RULESET_PROFILE)
        body.add_control("collection", url_for("api.rulesetcollection", game=game))
        body.add_control_put("edit", "Edit this ruleset", url_for("api.rulesetitem", \
                                                                  game=game, ruleset=ruleset),
                             schema=Ruleset.get_schema())
        body.add_control_delete("Delete this ruleset", \
                                url_for("api.rulesetitem", game=game, ruleset=ruleset))

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def put(self, game, ruleset):
        """
        Change information of a ruleset
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - ruleset
        description: Modify map information
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/ruleset_id'
        requestBody:
            description: JSON containing new data for the game
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Ruleset'
                    example:
                        name: Competitive
        responses:
            204:
                description: Map information changed
        """
        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            ruleset.name = request.json["name"]
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)

        return Response(status=204)

    def delete(self, game, ruleset):
        """
        Delete a ruleset
        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

        ---
        tags:
            - ruleset
        description: Delete a ruleset
        parameters:
            - $ref: '#/components/parameters/game_name'
            - $ref: '#/components/parameters/ruleset_id'
        responses:
            204:
                description: Ruleset deleted, nothing to return
        """
        db.session.delete(ruleset)
        db.session.commit()

        return Response(status=204)
