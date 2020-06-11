import os
import pytest
import tempfile

from datetime import date

from frolftracker import create_app, db
from frolftracker.models import Player, Course, Score


# Foreign keys ON
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


''' Tests for SQLAlchemy database. Tests are implemented with the assumption that
    SQLAlchemy uses SQL queries correctly, so only database models and their relations are tested.'''

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
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_fname)

def _get_player():
    return Player(name="Player 1")

def _get_course():
    return Course(
        name="Meri-Toppila",
        num_holes=18,
        par=54
    )

def _get_score():
    course = _get_course()
    player = _get_player()

    return Score(
        throws=54,
        course=course,
        player=player,
        date=date.today()
    )

def test_create_player(app):
    with app.app_context():
        player = _get_player()

        db.session.add(player)
        db.session.commit()
        assert Player.query.count() == 1

def test_create_score(app):
    with app.app_context():
        score = _get_score()

        db.session.add(score)
        db.session.commit()
        assert Score.query.count() == 1

def test_create_course(app):
    with app.app_context():
        course = _get_course()

        db.session.add(course)
        db.session.commit()
        assert Course.query.count() == 1
