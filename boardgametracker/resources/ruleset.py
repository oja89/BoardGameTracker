'''
Functions for ruleset class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
'''
from jsonschema import validate, ValidationError
from flask import Response, request, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from flask_restful import Resource
from boardgametracker.models import Ruleset
from boardgametracker import db
from boardgametracker import cache

class RulesetCollection(Resource):
    '''
    Collection of rulesets
    '''
    @cache.cached(timeout=5)
    def get(self, game=None):
        '''
        Get all rulesets
        If game given, all for that game
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        data_object = []

        # do the query for all
        if game is None:
            rulesets = Ruleset.query.all()

        # do the query for given game
        else:
            game_id = game.serialize(long=True)["id"]
            rulesets = Ruleset.query.filter_by(game_id=game_id)

        # append objects to list
        for ruleset in rulesets:
            # use serializer
            data_object.append(ruleset.serialize(long=True))

        response = data_object

        return response, 200

    def post(self, game=None):
        '''
        Add a new ruleset
        Cannot add a ruleset without a game
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType

        if game is None:
        # check the correct error message
        # game needs to exist
            abort(400)
        else:
            game_id = game.serialize(long=True)["id"]

        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            ruleset = Ruleset(
                name=request.json["name"],
                game_id=game_id
            )
            db.session.add(ruleset)
            db.session.commit()
        except KeyError:
            db.session.rollback()
            abort(400)
        # ruleset names are not unique, no need to test that

        return Response(status=201)

class RulesetItem(Resource):
    '''
    One item of ruleset
    '''
    def get(self, ruleset, game=None):
        '''
        Get information about a ruleset
        (Game can be in the path, but doesn't make difference)
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''

        return ruleset.serialize(long=True)

    def put(self, ruleset):
        '''
        Change information of a ruleset
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Ruleset.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            ruleset.name = request.json["name"]
            db.session.add(ruleset)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)

        return Response(status=204)

    def delete(self, ruleset):
        '''
        Delete a ruleset
        From
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        '''
        db.session.delete(ruleset)
        db.session.commit()

        return Response(status=204)
