"""
Converters for URL calls

from example
https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/utils.py"""

import secrets

from flask import url_for, request
from werkzeug.exceptions import NotFound, Forbidden
from werkzeug.routing import BaseConverter

from functools import wraps

from boardgametracker.models import (
    Player,
    Team,
    Game,
    Map,
    Ruleset,
    Match,
    PlayerResult,
    TeamResult,
    ApiKey
)


class MasonBuilder(dict):
    """
    Copied from exercise 3 materials, small modifications
    https://lovelace.oulu.fi/file-download/embedded/ohjelmoitava-web/ohjelmoitava-web/pwp-masonbuilder-py/
    
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    
    Note that child classes should set the *DELETE_RELATION* to the application
    specific relation name from the application namespace. The IANA standard
    does not define a link relation for deleting something.
    """

    DELETE_RELATION = ""

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

    def add_control_get(self, ctrl_name, title, href):
        """
        Not in the original example, added for uniformity
        Utility method for adding GET type controls.
        Method and encoding are
        fixed to "GET" and "json" respectively.

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema

        """
        self.add_control(
            ctrl_name,
            href,
            method="GET",
            encoding="json",
            title=title
        )

    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Utility method for adding POST type controls. The control is
        constructed from the method's parameters. Method and encoding are
        fixed to "POST" and "json" respectively.
        
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, ctrl_name, title, href, schema):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control name, method and
        encoding are fixed to "edit", "PUT" and "json" respectively.
        
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema

        TODO: add notion about ctrl_name
        """

        self.add_control(
            ctrl_name,
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_delete(self, title, href):
        """
        Utility method for adding DELETE type controls. The control is
        constructed from the method's parameters. Control method is fixed to
        "DELETE", and control's name is read from the class attribute
        *DELETE_RELATION* which needs to be overridden by the child class.

        : param str href: target URI for the control
        : param str title: human-readable title for the control
        """

        self.add_control(
            "BGT:delete",
            href,
            method="DELETE",
            title=title,
        )


class BGTBuilder(MasonBuilder):
    """
    Class for building the hypermedia
    from exercise 3 material
    https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/exercise-3-api-documentation-and-hypermedia/
    """

    def add_control_all_matches(self):
        """
        Match collection
        leads to GET /api/matches/
        """
        self.add_control_get(
            ctrl_name="BGT:all-matches",
            href=url_for("api.matchcollection"),
            title="All matches"
        )

    def add_control_add_match(self):
        """
        Add a new match
        leads to Post /api/matches/
        """
        self.add_control_post(
            ctrl_name="BGT:add-match",
            href=url_for("api.matchcollection"),
            schema=Match.get_schema(),
            title="Add match"
        )

    def add_control_all_players(self):
        """
        Get all game's players
        leads to GET /api/players/
        """
        self.add_control_get(
            ctrl_name="BGT:all-players",
            href=url_for("api.playercollection"),
            title="All players"
        )

    def add_control_add_player(self):
        """
        Add a new player
        leads to Post /api/players/
        """
        self.add_control_post(
            ctrl_name="BGT:add-player",
            href=url_for("api.playercollection"),
            schema=Player.get_schema(),
            title="Add player"
        )

    def add_control_all_teams(self):
        """
        Get all teams
        leads to GET /api/teams/
        """
        self.add_control_get(
            ctrl_name="BGT:all-teams",
            href=url_for("api.teamcollection"),
            title="All teams"
        )

    def add_control_add_team(self):
        """
        Add a new team
        leads to POST /api/teams/
        """
        self.add_control_post(
            ctrl_name="BGT:add-team",
            href=url_for("api.teamcollection"),
            schema=Team.get_schema(),
            title="Add team"
        )

    def add_control_all_games(self):
        """
        Get all games
        leads to GET /api/games/
        """
        self.add_control_get(
            ctrl_name="BGT:all-games",
            href=url_for("api.gamecollection"),
            title="All games"
        )

    def add_control_add_game(self):
        """
        Add a new game
        leads to Post /api/games/
        """
        self.add_control_post(
            ctrl_name="BGT:add-game",
            href=url_for("api.gamecollection"),
            schema=Game.get_schema(),
            title="Add game"
        )

    def add_control_all_maps(self, game):
        """
        Get all game's maps
        leads to GET /api/<game:game>/maps/
        """
        self.add_control_get(
            ctrl_name="BGT:all-maps",
            href=url_for("api.mapcollection", game=game),
            title="All maps"
        )

    def add_control_add_map(self, game):
        """
        Add a new map to a game
        leads to POST /api/<game:game>/maps/
        """
        self.add_control_post(
            ctrl_name="BGT:add-map",
            href=url_for("api.mapcollection", game=game),
            schema=Map.get_schema(),
            title="Add map"
        )

    def add_control_all_rulesets(self, game):
        """
        Get all game's rulesets
        leads to GET /api/<game:game>/rulesets/
        """
        self.add_control_get(
            ctrl_name="BGT:all-rulesets",
            href=url_for("api.rulesetcollection", game=game),
            title="All rulesets"
        )

    def add_control_add_ruleset(self, game):
        """
        Add a new ruleset to a game
        leads to Post /api/<game:game>/rulesets/
        """
        self.add_control_post(
            ctrl_name="BGT:add-ruleset",
            href=url_for("api.rulesetcollection", game=game),
            schema=Ruleset.get_schema(),
            title="Add ruleset"
        )


    def add_control_get_match(self, match):
        """
        Go to the match (from results)
        leads to GET /api/match/<match>
        """
        self.add_control_get(
            ctrl_name="BGT:get-match",
            href=url_for("api.matchitem", match=match),
            title="Go to match"
        )

    def add_control_get_game(self, game):
        """
        Go to the game (from maps/rulesets)
        leads to GET /api/game/<game>
        """
        self.add_control_get(
            ctrl_name="BGT:get-game",
            href=url_for("api.gameitem", game=game),
            title="Go to game"
        )

    def add_control_get_player(self, player):
        """
        Go to player (of a result)
        leads to GET /api/player/<player>
        """
        self.add_control_get(
            ctrl_name="BGT:get-player",
            href=url_for("api.playeritem", player=player),
            title="Go to player"
        )

    def add_control_get_team(self, team):
        """
        Go to team (of a result)
        leads to GET /api/team/<team>
        """
        self.add_control_get(
            ctrl_name="BGT:get-team",
            href=url_for("api.teamitem", team=team),
            title="Go to team"
        )

class PlayerConverter(BaseConverter):
    """
    Converter for player URL
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_player = Player.query.filter_by(name=value).first()
        if db_player is None:
            raise NotFound
        return db_player

    def to_url(self, value):
        """
        python to URL
        """
        return value.name


class MatchConverter(BaseConverter):
    """
    Converter for match URL
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_match = Match.query.filter_by(id=value).first()
        if db_match is None:
            raise NotFound
        return db_match

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.id)


class GameConverter(BaseConverter):
    """
    Converter for game URL
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_game = Game.query.filter_by(name=value).first()
        if db_game is None:
            raise NotFound
        return db_game

    def to_url(self, value):
        """
        python to URL
        """
        return value.name


class TeamConverter(BaseConverter):
    """
    Converter for team URL
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_team = Team.query.filter_by(name=value).first()
        if db_team is None:
            raise NotFound
        return db_team

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.name)


class RulesetConverter(BaseConverter):
    """
    Converter for ruleset URL
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_ruleset = Ruleset.query.filter_by(id=value).first()
        if db_ruleset is None:
            raise NotFound
        return db_ruleset

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.id)


class MapConverter(BaseConverter):
    """
    Converter for map url
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_map = Map.query.filter_by(id=value).first()
        if db_map is None:
            raise NotFound
        return db_map

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.id)


class PlayerResultConverter(BaseConverter):
    """
    Converter for player results url
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_player_result = PlayerResult.query.filter_by(id=value).first()
        if db_player_result is None:
            raise NotFound
        return db_player_result

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.id)


class TeamResultConverter(BaseConverter):
    """
    Converter for team results url
    """

    def to_python(self, value):
        """
        URL to python
        """
        db_team_result = TeamResult.query.filter_by(id=value).first()
        if db_team_result is None:
            raise NotFound
        return db_team_result

    def to_url(self, value):
        """
        python to URL
        """
        return str(value.id)


def require_admin(func):
    """
    Decorator for admin requirement
    from
    https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/#key-registry

    Added same forbidden -error for not having a apikey
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            key_hash = ApiKey.key_hash(request.headers.get("BGT-Api-Key").strip())
            db_key = ApiKey.query.filter_by(admin=True).first()
            if secrets.compare_digest(key_hash, db_key.key):
                return func(*args, **kwargs)
            raise Forbidden
        except: AttributeError
        raise Forbidden
    return wrapper

def require_this_user(func):
    """
    Decorator for user
    Should give access if:
    ApiKey matches player that is to be modified
    or if ApiKey matches admin

    from
    https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/#key-registry

    """
    @wraps(func)
    # needs self, otherwise doesn't understand player
    # return also self and player in func
    def wrapper(self, player, *args, **kwargs):
        try:
            admin_hash = ApiKey.key_hash(request.headers.get("BGT-Api-Key").strip())
            # check if admin
            db_key = ApiKey.query.filter_by(admin=True).first()
            if secrets.compare_digest(key_hash, db_key.key):
                return func(self, player, *args, **kwargs)
            # check if this user
            db_key = ApiKey.query.filter_by(player_id=player.id).first()
            if db_key is not None and (
                    secrets.compare_digest(key_hash, db_key.key)
                ):
                return func(self, player, *args, **kwargs)
            raise Forbidden
        except: AttributeError
        raise Forbidden
    return wrapper

