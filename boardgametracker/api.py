# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/api.py

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# after api creation to avoid circular imports
from boardgametracker.resources.players import PlayerCollection, PlayerItem

api.add_resource(PlayerCollection, "/players/")
api.add_resource(PlayerItem, "players/<player>/")

@api_bp.route("/"):
def index():
    return ""