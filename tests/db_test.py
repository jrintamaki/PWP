import os
import pytest
import tempfile

from datetime import datetime

import models
from models import Player, Course, Score, Round, Tournament

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
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    models.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    models.app.config["TESTING"] = True

    with models.app.app_context():
        models.db.create_all()

    yield models.db

    models.db.session.remove()
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
        par=course.par,
        course_id=course.id,
        player_id=player.id
    )

def _get_round():
    #score = _get_score()
    #course = Course.query.filter_by(id=score.course_id).first()

    return Round(
        date=datetime.now(),
        num_players=1,
        #course=course,
        #scores=[score]
    )

def _get_tournament():
    return Tournament(
        name="Maailmam mestaruus turnaus:D",
    )


def test_create_player(db_handle):
    player = _get_player()

    db_handle.session.add(player)
    db_handle.session.commit()
    assert Player.query.count() == 1

def test_create_score(db_handle):
    score = _get_score()

    db_handle.session.add(score)
    db_handle.session.commit()
    assert Score.query.count() == 1

def test_create_course(db_handle):
    course = _get_course()

    db_handle.session.add(course)
    db_handle.session.commit()
    assert Course.query.count() == 1

def test_create_round(db_handle):
    round = _get_round()

    db_handle.session.add(round)
    db_handle.session.commit()
    assert Round.query.count() == 1

def test_create_tournament(db_handle):
    tournament = _get_tournament()

    db_handle.session.add(tournament)
    db_handle.session.commit()
    assert Tournament.query.count() == 1
