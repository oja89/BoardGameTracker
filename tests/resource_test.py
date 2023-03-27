"""
Pytest
from https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/
which is based onhttp://flask.pocoo.org/docs/1.0/testing/
"""


import datetime
import os
import tempfile
from datetime import datetime
import json
from werkzeug.datastructures import Headers
from flask.testing import FlaskClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
import pytest


from boardgametracker import create_app, db
from boardgametracker.models import Player, Match, Game \
, Map, Ruleset, Team, PlayerResult, TeamResult

# from
#https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/tests/resource_test.py
# which from
# https://stackoverflow.com/questions/16416001/set-http-headers-for-all-requests-in-a-flask-test

TEST_KEY = "thisisatestkey"


class AuthHeaderClient(FlaskClient):
    """
    Class for flask
    """
    def open(self, *args, **kwargs):
        """
        Open
        """
        api_key_headers = Headers({
            'BGT-api-key': TEST_KEY
        })
        headers = kwargs.pop('headers', Headers())
        headers.extend(api_key_headers)
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Listener
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@pytest.fixture
def client():
    """
    from
    https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/tests/resource_test.py
    """
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    app.test_client_class = AuthHeaderClient
    yield app.test_client()

    os.close(db_fd)
    #os.unlink(db_fname)
    # ^this gives error about permissions in win32

def _populate_db():
    """
    Populate database with dummy data
    """
    game = Game(name="CS:GO")
    db.session.add(game)
    game = Game(name="Battlefield")
    db.session.add(game)

    ruleset = Ruleset(name="competitive", game_id=1)
    db.session.add(ruleset)
    ruleset = Ruleset(name="domination", game_id=2)
    db.session.add(ruleset)

    map = Map(name="dust", game_id=1)
    db.session.add(map)
    map = Map(name="verdun", game_id=2)
    db.session.add(map)
    map = Map(name="amiens", game_id=2)
    db.session.add(map)
    map = Map(name="sauna", game_id=1)
    db.session.add(map)

    match = Match(date=datetime.now(), turns=30, game_id=1, ruleset_id=1, map_id=1)
    db.session.add(match)
    match = Match(date=datetime.now(), turns=2, game_id=2, ruleset_id=1, map_id=2)
    db.session.add(match)

    team = Team(name="alpha")
    db.session.add(team)
    team = Team(name="beta")
    db.session.add(team)
    team = Team(name="gamma")
    db.session.add(team)

    for i in range(1, 4):
        player = Player(
            name=f"John-{i}"

        )
        db.session.add(player)


    player_result = PlayerResult(points=100, match_id=1, player_id=1, team_id=1)
    db.session.add(player_result)

    team_result = TeamResult(points=1000, order=3, match_id=1, team_id=1)
    db.session.add(team_result)

    db.session.commit()

def _get_player_json():
    """
    Creates a valid player JSON object to be used for PUT and POST tests.
    """

    return {"name": "John"}

def _get_uplayer_json():
    """
    Creates a unvalid player JSON object to be used for PUT and POST tests.
    """

    return {"name": 123}

def _get_match_json():
    """
    Creates a valid match JSON object to be used for PUT and POST tests.
    """

    return{"date":"2022-12-25", "turns":500, "game_id":1, "ruleset_id":1, ":map_id":1}

def _get_game_json():
    """
    Creates a valid game JSON object to be used for PUT and POST tests.
    """

    return{"name": "newgame"}

def _get_map_json():
    """
    Creates a valid map JSON object to be used for PUT and POST tests.
    """

    return{"name":"newmap", "game_id":1}

def _get_ruleset_json():
    """
    Creates a valid ruleset JSON object to be used for PUT and POST tests.
    """

    return{"name":"newruleset", "game_id":1}

def _get_team_json():
    """
    Creates a valid team JSON object to be used for PUT and POST tests.
    """

    return {"name": "newteam"}

class TestPlayerCollection():
    """
    Test for PlayerCollection
    """
    RESOURCE_URL = "/api/player/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 3
        for item in body:
            assert "name" in item

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_player_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        # Name is unique. Check that can't add with same name
        valid["name"] = "John-1"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test wrong mediatype
        resp = client.post(self.RESOURCE_URL, data="notjson"\
        , headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in(400, 415)

        # test key error
        key_err = {"player":"asd"}
        resp = client.post(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestPlayerItem():
    """
    Test for PlayerItem
    """

    RESOURCE_URL = "/api/player/John-1/"
    INVALID_URL = "/api/player/John-100/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete function
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test delete missing object
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_player_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        valid["name"] = "John-1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test put with unique name
        valid["name"] = "John-2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test validation error
        key_err = {"game":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestMatchCollection():
    """
    Test for MatchCollection
    """

    RESOURCE_URL = "/api/match/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 2
        for item in body:
            assert "date" in item
            assert "turns" in item
            assert "results" in item
            assert "game_name" in item
            assert "game_name" in item
            assert "map_name" in item
            assert "ruleset_name" in item

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_match_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

    def test_post_missing_field(self, client):
        """
        Test post with a missing field
        """
        valid = _get_match_json()
        valid.pop("date")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _get_match_json()
        valid.pop("turns")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        # test wrong mediatype
        resp = client.post(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"match":"asd"}
        resp = client.post(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestMatchItem():
    """
    Test for MatchItem
    """

    RESOURCE_URL = "/api/match/1/"
    INVALID_URL = "/api/match/x/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete function
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test delete missing object
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_match_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson", \
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test validation error
        key_err = {"game":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestGameCollection():
    """
    Test for GameCollection
    """

    RESOURCE_URL = "/api/game/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 2
        for item in body:
            assert "name" in item

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_game_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        # Game name is unique. Check that can't add with same name
        valid["name"] = "CS:GO"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test  wrongmediatype
        resp = client.post(self.RESOURCE_URL, data="notjson", \
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"game":"asd"}
        resp = client.post(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestGameItem():
    """
    Test for GameItem
    """

    RESOURCE_URL = "/api/game/CS:GO/"
    INVALID_URL = "/api/game/invalid/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete function
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test delete missing object
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_game_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        valid["name"] = "CS:GO"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test put with unique name
        valid["name"] = "Battlefield"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test validation error
        key_err = {"game":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestMapCollection():
    """
    Test for MapCollection
    """

    RESOURCE_URL = "/api/map/"
    RESOURCE_URL_FOR_POST = "/api/game/CS:GO/map/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 4
        for item in body:
            assert "name" in item
            assert "id" in item
            assert "game" in item
            assert "matches" in item
        # show one games' maps
        resp = client.get(self.RESOURCE_URL_FOR_POST)
        body = json.loads(resp.data)
        assert len(body) == 2

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_map_json()
        resp = client.post(self.RESOURCE_URL_FOR_POST, json=valid)
        assert resp.status_code == 201

        # test wrong mediatype
        resp = client.post(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"matchaa":"asd"}
        resp = client.post(self.RESOURCE_URL_FOR_POST, json=key_err)
        assert resp.status_code == 400

    def test_post_missing_field(self, client):
        """
        Test post with missing field
        """
        valid = _get_map_json()
        valid.pop("game_id")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _get_map_json()
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestMapItem():
    """
    Test for MapItem
    """

    RESOURCE_URL = "/api/map/1/"
    INVALID_URL = "/api/map/invalid/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete function
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test to delete missing information
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_map_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"matchaa":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestRulesetCollection():
    """
    Test for RulesetCollection
    """

    RESOURCE_URL = "/api/ruleset/"
    RESOURCE_URL_FOR_POST = "api/game/CS:GO/ruleset/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 2
        for item in body:
            assert "name" in item
            assert "id" in item
            assert "game" in item
            assert "matches" in item
        # show one games' rulesets
        resp = client.get(self.RESOURCE_URL_FOR_POST)
        body = json.loads(resp.data)
        assert len(body) == 1

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_ruleset_json()
        resp = client.post(self.RESOURCE_URL_FOR_POST, json=valid)
        assert resp.status_code == 201

        # test wrong mediatype
        resp = client.post(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"mapp":"asd"}
        resp = client.post(self.RESOURCE_URL_FOR_POST, json=key_err)
        assert resp.status_code == 400

    def test_post_missing_field(self, client):
        """
        Test posting missing field
        """
        valid = _get_ruleset_json()
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        valid = _get_ruleset_json()
        valid.pop("game_id")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestRulesetItem():
    """
    Test for RulesetItem
    """

    RESOURCE_URL = "/api/ruleset/1/"
    INVALID_URL = "/api/ruleset/invalid/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test delete a missing object
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_ruleset_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"matchaa":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestTeamCollection():
    """
    Test for TeamCollection
    """

    RESOURCE_URL = "/api/team/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 3
        for item in body:
            assert "name" in item

    def test_post_valid_request(self, client):
        """
        Test post function
        """
        valid = _get_team_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        # Team name is unique. Check that can't add with same name
        valid["name"] = "gamma"
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test wrong mediatype
        resp = client.post(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in(400, 415)

        # test key error
        key_err = {"team":"asd"}
        resp = client.post(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestTeamItem():
    """
    Test for TeamItem
    """

    RESOURCE_URL = "/api/team/gamma/"
    INVALID_URL = "/api/team/invalid/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert len(body) > 0

    def test_delete_valid(self, client):
        """
        Test delete function
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

    def test_delete_missing(self, client):
        """
        Test delete missing object
        """
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Test put function
        """
        valid = _get_team_json()

        # test invalid url
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test valid
        valid["name"] = "gamma"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test put with unique name
        valid["name"] = "alpha"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test wrong mediatype
        resp = client.put(self.RESOURCE_URL, data="notjson",\
        headers=Headers({"Content-Type": "text"}))
        assert resp.status_code in (400, 415)

        # test key error
        key_err = {"matchaa":"asd"}
        resp = client.put(self.RESOURCE_URL, json=key_err)
        assert resp.status_code == 400

class TestPlayerResultCollection():
    """
    Test for PlayerResultcollection
    """

    RESOURCE_URL = "api/player/John-1/result/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        for item in body:
            assert "points" in item
            assert "match_id" in item
            assert "player_id" in item
            assert "match_info" in item

class TestTeamResultCollection():
    """
    Test for TeamResultCollection
    """

    RESOURCE_URL = "api/match/1/teamresult/"

    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 1
        for item in body:
            assert "team" in item
            assert "points" in item
            assert "order" in item
            assert "match_info" in item

class TestIndex():
    """
    Test for Index
    """

    RESOURCE_URL = "api/"
    def test_get(self, client):
        """
        Test get function
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
