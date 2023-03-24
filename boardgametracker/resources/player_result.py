"""
Functions for team_result class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""

from flask_restful import Resource

from boardgametracker import cache
from boardgametracker.models import PlayerResult


class PlayerResultCollection(Resource):
    """
    Collection of player_results
    """
    @cache.cached(timeout=5)
    def get(self, match=None, player=None):
        """
        Get all results
        If match is given, all for that match
        If player given, all for that player
        If both, that should be an item, so abort?

        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        data_object = []

        # do the query for all
        if player is None and match is None:
            p_results = PlayerResult.query.all()

        # do the query for given player
        elif match is None:
            player_id = player.serialize(long=True)["id"]
            p_results = PlayerResult.query.filter_by(player_id=player_id)
        elif player is None:
            match_id = match.serialize(long=True)["id"]
            p_results = PlayerResult.query.filter_by(match_id=match_id)

        for result in p_results:
            data_object.append(result.serialize(long=True))

        response = data_object

        return response, 200
