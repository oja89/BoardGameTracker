"""
Functions for team_result class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, abort, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from boardgametracker import cache, db
from boardgametracker.constants import *
from boardgametracker.models import TeamResult
from boardgametracker.utils import BGTBuilder


class TeamResultCollection(Resource):
    """
    Collection of team_results
    """

    @cache.cached(timeout=5)
    def get(self, match):
        """
        Get all team_results for a match


        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        YAML and Mason added
        ---
        tags:
            - results
        description: Get team results for a match
        parameters:
            - $ref: '#/components/parameters/match_id'
        responses:
            200:
                description: One row of results
                content:
                    application/json:
                        example:
                            - points: 45
                              order: 1
                              match_id: 2
                              team_id: 2
        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.teamresultcollection", match=match))
        body["items"] = []

        # get results for match

        for result in match.team:
            item = BGTBuilder(result.serialize(long=True))
            item.add_control("self", url_for("api.teamresultitem", match=match, team_result=result))
            item.add_control("profile", TEAM_RESULT_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def post(self, match=None):
        """
        Add a new team_result
        Cannot add a result without a game

        ---
        tags:
            - results
        description: Add a new row of team_results
        parameters:
            - $ref: '#/components/parameters/match_id'
        requestBody:
            description: JSON containing data for the result
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/TeamResult'
                    example:
                        - points: 45
                          order: 1
                          team_id: 2
        responses:
            201:
                description: Row added
                headers:
                    Location:
                        description: URI of the result
                        schema:
                            type: string
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
            validate(request.json, TeamResult.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            team_result = TeamResult(
                points=request.json["points"],
                order=request.json["order"],
                match_id=match.id,
                team_id=request.json["team_id"]
            )
            print(team_result)
            db.session.add(team_result)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(
            status=201,
            headers={"Location": url_for("api.teamresultitem", match=match, team_result=team_result)}
        )


class TeamResultItem(Resource):
    """
    item of team_result
    """

    @cache.cached(timeout=5)
    def get(self, team_result, match):
        """
        Get one row of results

        ---
        tags:
            - results
        description: Get one row
        parameters:
            - $ref: '#/components/parameters/match_id'
            - $ref: '#/components/parameters/team_result_id'
        responses:
            200:
                description: One row of team results
                application/json:
                    schema:
                        $ref: '#/components/schemas/TeamResult'
                    example:
                        - points: 45
                          order: 1
                          team_id: 2
        """
        body = BGTBuilder(team_result.serialize(long=True))
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.teamresultitem", match=match, team_result=team_result))
        body.add_control("profile", TEAM_RESULT_PROFILE)
        body.add_control_put("edit", "Edit this row",
                             url_for("api.teamresultitem",
                                     match=match,
                                     team_result=team_result),
                             schema=TeamResult.get_schema()
                             )
        body.add_control_delete("Delete this row",
                                url_for("api.teamresultitem",
                                        match=match,
                                        team_result=team_result
                                        )
                                )
        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def put(self, team_result, match):
        """
        Edit a row of team results

        ---
        tags:
            - results
        description: Edit a row
        parameters:
            - $ref: '#/components/parameters/match_id'
            - $ref: '#/components/parameters/team_result_id'
        requestBody:
            description: JSON containing new data for the row
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/PlayerResult'
                    example:
                        - points: 45
                          order: 1
                          team_id: 2
        responses:
            204:
                description: Row modified, return new URI
                headers:
                    Location:
                        description: URI of the player_result
                        schema:
                            type: string
        """
        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, TeamResult.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        team_result.match_id = match.id
        team_result.points = request.json["points"]
        team_result.order = request.json["order"]
        team_result.team_id = request.json["team_id"]

        db.session.commit()

        # return the location?
        return Response(status=204, headers={
            "Location": url_for("api.teamresultitem",
                                match=match,
                                team_result=team_result
                                )
        }
                        )

    def delete(self, team_result, match):
        """
        Delete a row of team_results

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

        ---
        tags:
            - results
        description: Delete a row
        parameters:
            - $ref: '#/components/parameters/match_id'
            - $ref: '#/components/parameters/team_result_id'
        responses:
            204:
                description: Row deleted, nothing to return
        """
        db.session.delete(team_result)
        db.session.commit()

        return Response(status=204)
