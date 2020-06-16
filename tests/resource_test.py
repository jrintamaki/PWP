# The structure of this test file is borrowed from PWP course materials:
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/flask-api-project-layout/

import json
import os
import pytest
import tempfile
import time
from datetime import date
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from frolftracker import create_app, db
from frolftracker.models import Player, Score, Course


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()
        _populate_db()
        
    yield app.test_client()
    
    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    for i in range(4):
        p = Player(
            name="test-player-{}".format(i)
        )
        db.session.add(p)
        c = Course(
            name="test-course-{}".format(i)
        )
        db.session.add(c)
    db.session.commit()

    for i in range(8):
        p = Player.query.filter_by(name="test-player-{}".format(i%4))
        c = Course.query.filter_by(name="test-course-{}".format(i%4))
        s = Score(
            throws=54+i,
            date=date.today(),
            player=p,
            course=c,
            player_id=p.id,
            course_id=c.id
        )
        db.session.add(s)
    db.session.commit()

def _get_player_json(number=1):
    """
    Creates a valid player JSON object to be used for PUT and POST tests.
    """
    
    return {"name": "extra-player-{}".format(number)}

def _check_namespace(client, response):
    """
    Checks that the "frolf" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["frolf"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

## TODO