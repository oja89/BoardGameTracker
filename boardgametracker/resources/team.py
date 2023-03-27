"""
Functions for team class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, url_for
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from flask_restful import Resource

from boardgametracker import cache
from boardgametracker import db
from boardgametracker.constants import JSON, MASON, TEAM_PROFILE, LINK_RELATIONS_URL
from boardgametracker.models import Team
from boardgametracker.utils import BGTBuilder


class TeamCollection(Resource):
    """
    Collection of teams
    """
    @cache.cached(timeout=5)
    def get(self):
        """
        Get all teams
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        ---
        tags:
            - team
        description: Get all teams
        responses:
            200:
                description: List of teams
                content:
                    application/json:
                        example:
                            - name: Foxes
                            - name: Wolves
        """
        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.teamcollection"))
        body.add_control_all_teams()
        body.add_control_add_team()
        body["items"] = []

        for team in Team.query.all():
            item = BGTBuilder(team.serialize(long=True))
            # create controls
            item.add_control("self", url_for("api.teamitem", team=team))
            item.add_control("profile", TEAM_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response


    def post(self):
        """
        Add a new team
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - team
        description: Add a new team
        requestBody:
            description: JSON containing data for the team
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Team'
                    example:
                        name: Squirrels
        responses:
            201:
                description: Team added
                headers:
                    Location:
                        description: URI of the team
                        schema:
                            type: string
            409:
                description: Name already exists
        """

        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, Team.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            team = Team(
                name=request.json["name"]
            )
            db.session.add(team)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            name = request.json["name"]
            raise Conflict(description=f"Team with name '{name}' already exists.")
        return Response(status=201)

class TeamItem(Resource):
    """
    One item of team
    """
    def get(self, team):
        """
        Get information about a team
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - team
        description: Get one team
        parameters:
            - $ref: '#/components/parameters/team_name'
        responses:
            200:
                description: Team's information
                content:
                    application/json:
                        example:
                            - name: Wolves

        """

        body = BGTBuilder()
        body["item"] = BGTBuilder(team.serialize(long=True))
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.teamitem", team=team))
        body.add_control("profile", TEAM_PROFILE)
        body.add_control("collection", url_for("api.teamcollection"))
        body.add_control_put("edit", "Edit this team", \
        url_for("api.teamitem", team=team), schema=Team.get_schema())
        body.add_control_delete("Delete this team", url_for("api.teamitem", team=team))

        response = Response(json.dumps(body), 200, mimetype=MASON)

        return response

    def put(self, team):
        """
        Change information of a team
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - team
        description: Modify map information
        parameters:
            - $ref: '#/components/parameters/team_name'
        requestBody:
            description: JSON containing new data for the game
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/Team'
                    example:
                        name: Wolves
        responses:
            204:
                description: Team information changed
            409:
                description: Integrity error
        """
        if not request.mimetype == JSON:
            raise UnsupportedMediaType
        try:
            validate(request.json, Team.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        team.name = request.json["name"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(description=f"Team with name '{team.name}' already exists.")

        return Response(status=204)

    def delete(self, team):
        """
        Delete a team

        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

        ---
        tags:
            - team
        description: Delete a team
        parameters:
            - $ref: '#/components/parameters/team_name'
        responses:
            204:
                description: Team deleted, nothing to return
        """
        db.session.delete(team)
        db.session.commit()

        return Response(status=204)
