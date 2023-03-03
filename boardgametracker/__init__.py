# from sensorhub example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/__init__.py
# which is based on 
# http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from boardgametracker.constants import *

db = SQLAlchemy()
cache = Cache()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),
    )
    
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

    from . import models
    from . import api
    
    from boardgametracker.utils import PlayerConverter, TeamConverter, MatchConverter, RulesetConverter, MapConverter, GameConverter
    
    
    # cli commands placed in models
    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.generate_test_data)
    
    # print instance path
    print(app.instance_path)
    
    app.url_map.converters["player"] = PlayerConverter
    app.url_map.converters["team"] = TeamConverter
    app.url_map.converters["match"] = MatchConverter
    app.url_map.converters["ruleset"] = RulesetConverter
    app.url_map.converters["map"] = MapConverter
    app.url_map.converters["game"] = GameConverter
    
    #this has to be after converters
    app.register_blueprint(api.api_bp)
    
    @app.route("/api/")
    def index():
        return "This is index"
    
    
    return app
