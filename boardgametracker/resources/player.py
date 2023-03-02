# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from boardgametracker.models import Player
from boardgametracker import db
from boardgametracker.utils import BGTBuilder, create_error_response, require_admin
from boardgametracker.constants import *

class PlayerCollection(Resource):
    def get(self):
        body = BGTBuilder()

        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playercollection"))
        body.add_control_add_player()
        body["items"] = []
        for player in Player.query.all():
            item = BGTBuilder(
                id=player.id,
                name=player.name,
                result=player.result and player.result.id
            )
            item.add_control("self", url_for("api.playeritem", player=player))
            item.add_control("profile", PLAYER_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)
    
class PlayerItem(Resource):
    def get(self, player):
        body = BGTBuilder(
            id=player.id,
            name=player.name
            )
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        return Response(json.dumps(body), 200, mimetype=MASON)
