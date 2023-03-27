"""
Functions for team_result class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
"""

from flask_restful import Resource

from boardgametracker import cache
from boardgametracker.models import TeamResult


class TeamResultCollection(Resource):
    """
    Collection of team_results
    """
    @cache.cached(timeout=5)
    def get(self, match=None, team=None):
        """
        Get all results
        If match is given, all for that match
        If team given, all for that team
        If both, that should be an item, so abort?
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        """
        data_object = []

        # do the query for all
        if team is None and match is None:
            t_results = TeamResult.query.all()

        # do the query for given team
        elif match is None:
            team_id = team.serialize(long=True)["id"]
            t_results = TeamResult.query.filter_by(team_id=team_id)

        elif team is None:
            match_id = match.serialize(long=True)["id"]
            t_results = TeamResult.query.filter_by(match_id=match_id)

        for result in t_results:
            data_object.append(result.serialize(long=True))

        response = data_object

        return response, 200

class TeamResultItem(Resource):
    """
    item of team_result
    """
    @cache.cached(timeout=5)
    def get(self, match=None, player=None):
        pass