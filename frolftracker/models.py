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

    scores = db.relationship("Score", cascade="all,delete", back_populates="player")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)


class Score(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    throws = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.ForeignKey("player.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)

    course = db.relationship("Course", back_populates="scores")
    player = db.relationship("Player", back_populates="scores")


class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    num_holes = db.Column(db.Integer, nullable=False, default=18)
    par = db.Column(db.Integer, nullable=False, default=54)

    scores = db.relationship("Score", cascade="all,delete", back_populates="course")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)

