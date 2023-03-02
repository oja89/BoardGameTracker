# from https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/

# which is based onhttp://flask.pocoo.org/docs/1.0/testing/

import datetime
import os
import pytest
import tempfile
import json

from werkzeug.datastructures import Headers
from flask.testing import FlaskClient
from sqlalchemy import event
from sqlalchemy.engine import Engine

from boardgametracker import create_app, db
from boardgametracker.models import Player

# from https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/tests/resource_test.py
# which from # https://stackoverflow.com/questions/16416001/set-http-headers-for-all-requests-in-a-flask-test

TEST_KEY = "thisisatestkey"


class AuthHeaderClient(FlaskClient):

    def open(self, *args, **kwargs):
        api_key_headers = Headers({
            'BGT-api-key': TEST_KEY
        })
        headers = kwargs.pop('headers', Headers())
        headers.extend(api_key_headers)
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@pytest.fixture
def client():
    '''
    
    from https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/tests/resource_test.py
    '''
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
    for i in range(1, 4):
        p = Player(
            name=f"test-sensor-{i}"
        )
        db.session.add(p)
    db.session.commit()

class TestPlayerCollection(object):

    RESOURCE_URL = "/api/player/"
    
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        
        #assert len(body["items"]) == 4
        #for item in body["items"]:
        #    assert "name" in item
            
 