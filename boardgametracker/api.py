# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/api.py

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# after api creation to avoid circular imports
from boardgametracker.resources.player import PlayerCollection, PlayerItem

api.add_resource(PlayerCollection, "/player/")
api.add_resource(PlayerItem, "/player/<player:player>/")

