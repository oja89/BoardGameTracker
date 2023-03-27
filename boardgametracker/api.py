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
from boardgametracker.resources.player_result import PlayerResultCollection
from boardgametracker.resources.ruleset import RulesetCollection, RulesetItem
from boardgametracker.resources.team import TeamCollection, TeamItem
from boardgametracker.resources.team_result import TeamResultCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(PlayerCollection, "/players/")
api.add_resource(PlayerItem, "/player/<player:player>/")
api.add_resource(TeamCollection, "/teams/")
api.add_resource(TeamItem, "/team/<team:team>/")
api.add_resource(GameCollection, "/games/")
api.add_resource(GameItem, "/game/<game:game>/")

# 2 routes for map
api.add_resource(MapCollection,
                 #"/maps/",
                 "/game/<game:game>/maps/"
                 )
api.add_resource(MapItem,
                 #"/map/<map_:map_>/",
                 "/game/<string:game>/map/<int:map_>/"
                 )

# 2 routes for rulesets
api.add_resource(RulesetCollection,
                 #"/rulesets/",
                 "/game/<game:game>/rulesets/"
                 )
api.add_resource(RulesetItem,
                #"/ruleset/<ruleset:ruleset>/",
                 "/game/<game:game>/ruleset/<int:ruleset>/"
                 )

api.add_resource(MatchCollection, "/matches/")
api.add_resource(MatchItem, "/match/<int:match>/")

# results collections
api.add_resource(PlayerResultCollection,
                 "/player/<player:player>/results/",
                 "/match/<int:match>/playerresults/"
                 )
api.add_resource(TeamResultCollection,
                 "/team/<team:team>/results/",
                 "/match/<int:match>/teamresults/"
                 )
