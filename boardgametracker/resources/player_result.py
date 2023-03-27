"""
Functions for player_result class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, abort, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType

from boardgametracker import cache, db
from boardgametracker.models import PlayerResult
from boardgametracker.utils import BGTBuilder
from boardgametracker.constants import *


class PlayerResultCollection(Resource):
    """
    Collection of player_results
    """
    @cache.cached(timeout=5)
    def get(self, match):
        """
        Get all results for a match


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        YAML and Mason added
        ---
        tags:
            - results
        description: Get results for a match
        parameters:
            - $ref: '#/components/parameters/match_id'
        responses:
            200:
                description: One row of results
                content:
                    application/json:
                        example:
                            - points: 45
                              match_id: 1
                              player_id: 2
                              team_id: 2
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playerresultcollection", match=match))
        body["items"] = []


        # get results for match


        for result in match.player_result:
            item = BGTBuilder(result.serialize(long=True))
            item.add_control("self", url_for("api.playerresultitem", match=match, p_res=result))
            item.add_control("profile", PLAYER_RESULT_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self, match=None):
        """
        Add a new player_result
        Cannot add a result without a game

        ---
        tags:
            - results
        description: Add a new row of playerresults
        parameters:
            - $ref: '#/components/parameters/match_id'
        requestBody:
            description: JSON containing data for the result
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/PlayerResult'
                    example:
                        points: 23
                        player_id: 1
                        team_id: 2
        responses:
            201:
                description: Row added
                headers:
                    Location:
                        description: URI of the result
                        schema:
                            type: string
                        example: "asdfadf"
            400:
                description: Key error
        """
        if not request.mimetype == JSON:
            raise UnsupportedMediaType

        if match is None:
            # check the correct error message
            # game needs to exist
            abort(400)

        try:
            validate(request.json, PlayerResult.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            p_res = PlayerResult(
                points=request.json["points"],
                match_id=match.id,
                player_id=request.json["player_id"],
                team_id=request.json["team_id"]
            )
            print(p_res)
            db.session.add(p_res)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(
            status=201,
            headers={"Location": url_for("api.playerresultitem", match=match, p_res=p_res)}
        )


class PlayerResultItem(Resource):
    """
    item of player_result
    """
    @cache.cached(timeout=5)
    def get(self, match=None):
        pass