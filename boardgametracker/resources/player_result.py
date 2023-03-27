"""
Functions for player_result class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""
import json

from flask import Response, request, url_for
from flask_restful import Resource

from boardgametracker import cache
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
        Get all results
        If match is given, all for that match
        If player given, all for that player
        If both, that should be an item, so abort?

        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

        ---
        tags:
            - results
        description: Get results for a match

        """

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.gamecollection"))
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
        pass

class PlayerResultItem(Resource):
    """
    item of player_result
    """
    @cache.cached(timeout=5)
    def get(self, match=None, player=None):
        pass