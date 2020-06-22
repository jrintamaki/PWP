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
def client():
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
            name="test-course-{}".format(i),
            num_holes = 23,
            par = 69
        )
        db.session.add(c)
    db.session.commit()

    for i in range(8):
        p = Player.query.filter_by(name="test-player-{}".format(i%4)).first()
        c = Course.query.filter_by(name="test-course-{}".format(i%4)).first()
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

def _get_course_json(number=1):
    """
    Creates a valid course JSON object to be used for PUT and POST tests.
    """
    
    return {"name": "extra-course-{}".format(number),
            "num_holes": number * 10,
            "par": number * 30}

def _get_score_json(number=1):
    """
    Creates a valid score JSON object to be used for PUT and POST tests.
    """
    
    return {"score_id": number,
            "throws": number * 10,
            "date": "2020-06-22",
            "player_id": number, 
            "course_id": number}

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

def _check_control_put_method_player(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid player against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_player_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_control_post_method_player(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_player_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

def _check_control_put_method_course(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid player against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_course_json()
    body["name"] = obj["name"]
    body["num_holes"] = obj["num_holes"]
    body["par"] = obj["par"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_control_post_method_course(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_course_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

def _check_control_put_method_score(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid player against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_score_json()
    body["score_id"] = obj["score_id"]
    body["throws"] = obj["throws"]
    body["date"] = obj["date"]
    body["player_id"] = obj["player_id"]
    body["course_id"] = obj["course_id"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
def _check_control_post_method_score(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """
    
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_score_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestPlayerCollection(object):
    """
    This class implements tests for each HTTP method in player collection
    resource. 
    """
    
    RESOURCE_URL = "/api/players/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_post_method_player("frolf:add-player", client, body)
        assert len(body["items"]) == 4
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_player_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        print(resp.headers["Location"])
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "5" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "extra-player-1"
        
        # send same data again for 409
        # resp = client.post(self.RESOURCE_URL, json=valid)
        # assert resp.status_code == 409
        
        # create invalid request body for 400
        invalid = {"namme": "extra-player-1"}
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400

class TestPlayerItem(object):
    
    RESOURCE_URL = "/api/players/1/"
    INVALID_URL = "/api/players/999/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "test-player-0"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_get_method("frolf:scores-by", client, body)
        _check_control_put_method_player("edit", client, body)
        _check_control_delete_method("frolf:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_player_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another sensor's name
        #valid["name"] = "test-sensor-2"
        #resp = client.put(self.RESOURCE_URL, json=valid)
        #assert resp.status_code == 409
        
        # test with valid (only change model)
        valid["name"] = "test-player-x"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # create invalid request body for 400
        invalid = {"namme": "extra-player-1"}
        resp = client.put(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        
        valid = _get_player_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
                
class TestCourseCollection(object):
    """
    This class implements tests for each HTTP method in course collection
    resource. 
    """
    
    RESOURCE_URL = "/api/courses/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_post_method_course("frolf:add-course", client, body)
        assert len(body["items"]) == 4
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item
            assert "num_holes" in item
            assert "par" in item


    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_course_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        print(resp.headers["Location"])
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "5" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "extra-course-1"
        
        # send same data again for 409
        # resp = client.post(self.RESOURCE_URL, json=valid)
        # assert resp.status_code == 409
        
        # create invalid request body for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestCourseItem(object):
    
    RESOURCE_URL = "/api/courses/1/"
    INVALID_URL = "/api/courses/999/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "test-course-0"
        assert body["num_holes"] == 23
        assert body["par"] == 69
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_get_method("frolf:scores-by", client, body)
        _check_control_put_method_course("edit", client, body)
        _check_control_delete_method("frolf:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_course_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another sensor's name
        #valid["name"] = "test-sensor-2"
        #resp = client.put(self.RESOURCE_URL, json=valid)
        #assert resp.status_code == 409
        
        # test with valid (only change model)
        valid["name"] = "test-course-x"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # create invalid request body for 400
        valid.pop("name")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_course_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        
        
class TestScoreCollection(object):
    """
    This class implements tests for each HTTP method in score collection
    resource. 
    """
    
    RESOURCE_URL = "/api/scores/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("frolf:players-all", client, body)
        _check_control_get_method("frolf:courses-all", client, body)
        _check_control_post_method_score("frolf:add-score", client, body)
        assert len(body["items"]) == 8
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "score_id" in item
            assert "throws" in item
            assert "date" in item
            assert "player_id" in item
            assert "course_id" in item

    def test_get_by_player(self, client):
        """
        Tests the GET method filtered by player id. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL, query_string={"player_id": 1})
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("frolf:players-all", client, body)
        _check_control_get_method("frolf:courses-all", client, body)
        _check_control_post_method_score("frolf:add-score", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "score_id" in item
            assert "throws" in item
            assert "date" in item
            assert "player_id" in item
            assert item["player_id"] == 1
            assert "course_id" in item

    def test_get_by_course(self, client):
        """
        Tests the GET method filtered by course id. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL, query_string={"course_id": 1})
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("frolf:players-all", client, body)
        _check_control_get_method("frolf:courses-all", client, body)
        _check_control_post_method_score("frolf:add-score", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "score_id" in item
            assert "throws" in item
            assert "date" in item
            assert "player_id" in item
            assert item["course_id"] == 1
            assert "course_id" in item

    def test_get_by_player_and_course(self, client):
        """
        Tests the GET method filtered by player id and course id. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL, query_string={"player_id": 1, "course_id": 1})
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("frolf:players-all", client, body)
        _check_control_get_method("frolf:courses-all", client, body)
        _check_control_post_method_score("frolf:add-score", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "score_id" in item
            assert "throws" in item
            assert "date" in item
            assert "player_id" in item
            assert item["player_id"] == 1
            assert item["course_id"] == 1
            assert "course_id" in item


    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_score_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        print(resp.headers["Location"])
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "9" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["score_id"] == 9
        assert body["throws"] == 10
        assert body["date"] == "2020-06-22"
        assert body["player_id"] == 1
        assert body["course_id"] == 1
        
        # send same data again for 409
        # resp = client.post(self.RESOURCE_URL, json=valid)
        # assert resp.status_code == 409
        
        # create invalid request body for 400
        valid.pop("player_id")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestScoreItem(object):
    
    RESOURCE_URL = "/api/scores/1/"
    INVALID_URL = "/api/scores/999/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["score_id"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method_score("edit", client, body)
        _check_control_delete_method("frolf:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_score_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another sensor's name
        #valid["name"] = "test-sensor-2"
        #resp = client.put(self.RESOURCE_URL, json=valid)
        #assert resp.status_code == 409
        
        # test with valid (only change throws)
        valid["throws"] = 123
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # create invalid request body for 400
        valid.pop("player_id")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_score_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["score_id"] == valid["score_id"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


## TODO