"""
Creates the Flask app

from sensorhub example:
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/__init__.py
which is based on
http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
"""

import os
from flask import Response
import json

from flasgger import Swagger
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from boardgametracker.constants import *


db = SQLAlchemy()
cache = Cache()


def create_app(test_config=None):
    """
    Create Flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),
    )

    app.config["SWAGGER"] = {
        "title": "Sensorhub API",
        "openapi": "3.0.3",
        "uiversion": 3
    }
    swagger = Swagger(app, template_file="doc/openapi.yml")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)

    # imports need to be inside the function to prevent circular imports
    # pylint gives bad points but cannot find a better way
    from . import models
    from . import api

    from boardgametracker.utils import (
        PlayerConverter,
        TeamConverter,
        MatchConverter,
        RulesetConverter,
        MapConverter,
        GameConverter,
        PlayerResultConverter,
        TeamResultConverter,
        MasonBuilder,
        BGTBuilder
    )

    # cli commands placed in models
    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.generate_test_data)
    app.cli.add_command(models.generate_admin_key)
    # TODO: elsewhere...
    app.cli.add_command(models.generate_user_key)


    # print instance path
    print(app.instance_path)

    app.url_map.converters["player"] = PlayerConverter
    app.url_map.converters["team"] = TeamConverter
    app.url_map.converters["match"] = MatchConverter
    app.url_map.converters["ruleset"] = RulesetConverter
    app.url_map.converters["map_"] = MapConverter
    app.url_map.converters["game"] = GameConverter
    app.url_map.converters["player_result"] = PlayerResultConverter
    app.url_map.converters["team_result"] = TeamResultConverter

    # this has to be after converters
    app.register_blueprint(api.api_bp)

    @app.route(LINK_RELATIONS_URL)
    def get_relations():
        return "links"

    @app.route("/api/")
    def index():
        """
        Index page
        """
        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        body.add_control_match_collection()
        body.add_control_all_players()
        body.add_control_all_teams()
        body.add_control_all_games()

        response = Response(json.dumps(body), 200, mimetype=MASON)


        return response

    return app
