from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Player(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    #scores = db.relationship("Score", cascade="all,delete", back_populates="player")
    #tournaments = db.relationship("Tournament", back_populates="players")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)


class Score(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    throws = db.Column(db.Integer, nullable=False)
    par = db.Column(db.ForeignKey("course.par", ondelete="CASCADE"), nullable=False)
    player_id = db.Column(db.ForeignKey("player.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    round_id = db.Column(db.ForeignKey("round.id", ondelete="CASCADE"), nullable=True)

    #course = db.relationship("Course", back_populates="scores")
    #player = db.relationship("Player", back_populates="scores")
    #round = db.relationship("Round", back_populates="scores")


class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    num_holes = db.Column(db.Integer, nullable=False, default=18)
    par = db.Column(db.Integer, nullable=False, default=54)

    #scores = db.relationship("Score", cascade="all,delete", back_populates="course")
    #tournaments = db.relationship("Tournament", back_populates="course")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)


class Round(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.ForeignKey("course.id"))
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    round_number = db.Column(db.Integer, default=1)
    num_players = db.Column(db.Integer, nullable=False, default=4)

    #course = db.relationship("Course")
    #scores = db.relationship("Score", back_populates="round")
    #tournament = db.relationship("Tournament", back_populates="rounds")


class Tournament(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    num_rounds = db.Column(db.Integer, nullable=False, default=1)
    num_players = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    #players = db.relationship("Player", back_populates="tournaments")
    #rounds = db.relationship("Round", back_populates="tournament")
    #course = db.relationship("Course", back_populates="tournaments")
