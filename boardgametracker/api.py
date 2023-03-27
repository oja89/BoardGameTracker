"""
Creating of the api

 from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/api.py''"""

from flask import Blueprint
from flask_restful import Api

from boardgametracker.resources.game import GameCollection, GameItem
from boardgametracker.resources.map import MapCollection, MapItem
from boardgametracker.resources.match import MatchCollection, MatchItem
from boardgametracker.resources.player import PlayerCollection, PlayerItem
from boardgametracker.resources.player_result import PlayerResultCollection, PlayerResultItem
from boardgametracker.resources.ruleset import RulesetCollection, RulesetItem
from boardgametracker.resources.team import TeamCollection, TeamItem
from boardgametracker.resources.team_result import TeamResultCollection, TeamResultItem

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(PlayerCollection, "/players/")
api.add_resource(PlayerItem, "/player/<player:player>/")
api.add_resource(TeamCollection, "/teams/")
api.add_resource(TeamItem, "/team/<team:team>/")
api.add_resource(GameCollection, "/games/")
api.add_resource(GameItem, "/game/<game:game>/")
api.add_resource(MapCollection, "/game/<game:game>/maps/")
api.add_resource(MapItem, "/game/<game:game>/map/<map_:map_>/")
api.add_resource(RulesetCollection, "/game/<game:game>/rulesets/")
api.add_resource(RulesetItem, "/game/<game:game>/ruleset/<ruleset:ruleset>/")
api.add_resource(MatchCollection, "/matches/")
api.add_resource(MatchItem, "/match/<match:match>/")
api.add_resource(PlayerResultCollection, "/match/<match:match>/playerresults/")
api.add_resource(PlayerResultItem,"/match/<match:match>/playerresult/<player_result:player_result>/")
api.add_resource(TeamResultCollection, "/match/<match:match>/teamresults/")
api.add_resource(TeamResultItem, "/match/<match:match>/teamresult/<team_result:team_result>/")
