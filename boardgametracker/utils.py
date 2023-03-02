# from example
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/utils.py

import json
import secrets
from flask import Response, request, url_for
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.routing import BaseConverter

from boardgametracker.constants import *
from boardgametracker.models import *

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class BGTBuilder(MasonBuilder):

    def add_control_delete_player(self, player):
        self.add_control(
            "bgt:delete",
            url_for("api.playeritem", sensor=sensor),
            method="DELETE",
            title="Delete this player"
        )

    def add_control_add_ruleset(self, game):
        self.add_control(
            "bgt:add-ruleset",
            url_for("api.rulesetcollection", game=game),
            method="POST",
            encoding="json",
            title="Add a new ruleset for this game",
            schema=Ruleset.get_schema()
        )

    def add_control_add_player(self):
        self.add_control(
            "bgt:add-player",
            url_for("api.playercollection"),
            method="POST",
            encoding="json",
            title="Add a new player",
            schema=Player.get_schema()
        )

    def add_control_modify_player(self, player):
        self.add_control(
            "edit",
            url_for("api.playeritem", player=player),
            method="PUT",
            encoding="json",
            title="Edit this player",
            schema=Player.get_schema()
        )

    def add_control_get_ruleset(self, game):
        base_uri = url_for("api.rulesetcollection", game=game)
        uri = base_uri + "?start={index}"
        self.add_control(
            "bgt:ruleset",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    @staticmethod
    def _paginator_schema():
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        props = schema["properties"]
        props["index"] = {
            "description": "Starting index for pagination",
            "type": "integer",
            "default": "0"
        }
        return schema
        
def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)

def page_key(*args, **kwargs):
    start = request.args.get("start", 0)
    return request.path + f"[start_{start}]"
    
def require_admin(func):
    def wrapper(*args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("BGT-Api-Key", "").strip())
        db_key = ApiKey.query.filter_by(admin=True).first()
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper

def require_player_key(func):
    def wrapper(self, player, *args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("BGT-Api-Key").strip())
        db_key = ApiKey.query.filter_by(player=player).first()
        if db_key is not None and secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper


class PlayerConverter(BaseConverter):
    
    def to_python(self, value):
        db_player = Player.query.filter_by(name=value).first()
        if db_player is None:
            raise NotFound
        return db_player
        
    def to_url(self, db_player):
        return db_player.name