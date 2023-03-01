# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/api.py

from flask import Blueprint
from flask_restful import Api

from boardgametracker.resources.players import *

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(PlayerCollection, "/players/")
