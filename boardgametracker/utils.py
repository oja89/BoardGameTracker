'''
Converters for URL calls

from example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/utils.py'''

from flask import Response
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from boardgametracker.models import (
    Player,
    Team,
    Game,
    Map,
    Ruleset,
    Match
    )

class PlayerConverter(BaseConverter):
    '''
    Converter for player URL
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_player = Player.query.filter_by(name=value).first()
        if db_player is None:
            raise NotFound
        return db_player

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.name

class MatchConverter(BaseConverter):
    '''
    Converter for match URL
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_match = Match.query.filter_by(id=value).first()
        if db_match is None:
            raise NotFound
        return db_match

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.id

class GameConverter(BaseConverter):
    '''
    Converter for game URL
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_game = Game.query.filter_by(name=value).first()
        if db_game is None:
            raise NotFound
        return db_game

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.name

class TeamConverter(BaseConverter):
    '''
    Converter for team URL
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_team = Team.query.filter_by(name=value).first()
        if db_team is None:
            raise NotFound
        return db_team

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.name

class RulesetConverter(BaseConverter):
    '''
    Converter for ruleset URL
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_ruleset = Ruleset.query.filter_by(id=value).first()
        if db_ruleset is None:
            raise NotFound
        return db_ruleset

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.id

class MapConverter(BaseConverter):
    '''
    Converter for map url
    '''
    def to_python(self, value):
        '''
        URL to python
        '''
        db_map = Map.query.filter_by(id=value).first()
        if db_map is None:
            raise NotFound
        return db_map

    def to_url(self, value):
        '''
        python to URL
        '''
        return value.id
