'''
Functions for match class objects

from sensorhub example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
'''
from datetime import datetime
from jsonschema import validate, ValidationError
from flask import Response, request, abort, url_for
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from boardgametracker.models import Match
from boardgametracker.utils import BGTBuilder
from boardgametracker import db, cache, api
from boardgametracker.constants import *

class MatchCollection(Resource):
    '''
    Collection of matches
    '''
    @cache.cached(timeout=5)
    def get(self):
        '''
        Get all matches
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        
        modified to use MasonBuilder after ex3
        
        '''

        body = BGTBuilder()
        body.add_namespace("BGT", LINK_RELATIONS_URL)
        # cannot use, api is defined inside function...?
        body.add_control("self", url_for("api.matchcollection"))
        body.add_control_add_match()
        body["items"] = []
        
        for match in Match.query.all():
            # use serializer
            #body["items"].append(match.serialize(long=True))
            pass

        response = body

        return response, 200

    def post(self):
        '''
        Add a new match
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Match.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))
        try:
            match = Match(
                date=datetime.fromisoformat(request.json["date"]),
                turns=request.json["turns"]
            )
            db.session.add(match)
            db.session.commit()

        #If a field is missing raise except
        except KeyError:
            db.session.rollback()
            abort(400)

        return Response(status=201)

class MatchItem(Resource):
    '''
    One item of match
    '''
    def get(self, match):
        '''
        Get information about a match
        From exercise 2 material,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        return match.serialize(long=True)

    def put(self, match):
        '''
        Change information of a match
        From exercise 2,
        https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/
        '''
        if not request.mimetype == "application/json":
            raise UnsupportedMediaType
        try:
            validate(request.json, Match.get_schema())
        except ValidationError as err:
            raise BadRequest(description=str(err))

        try:
            match = Match(
                date=datetime.fromisoformat(request.json["date"]),
                turns=request.json["turns"]
            )
            db.session.add(match)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(409)

        return Response(status=204)

    def delete(self, match):
        '''
        Delete a match
        From 
        https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/resources/sensor.py
        '''
        db.session.delete(match)
        db.session.commit()

        return Response(status=204)
