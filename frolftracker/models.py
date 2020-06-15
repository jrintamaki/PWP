from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, OperationalError

from frolftracker import db

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Player(db.Model):
    '''
    Database model of a frolf player.
    Attributes:
    id : database id, primary key
    name : name of the player
    scores : all scores by this player
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    scores = db.relationship("Score", cascade="all,delete", back_populates="player")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        properties = schema["properties"] = {}
        properties["id"] = {
            "description": "Database ID of this player",
            "type": "integer"
        }
        properties["name"] = {
            "description": "Player's name",
            "type": "string"
        }
        # TODO: scores

        return schema

class Score(db.Model):
    '''
    Database model of a round score.
    Attributes:
    id : database id, primary key
    throws : number of strokes on this score
    date : date this score was played on
    player_id : ID of the player, foreign key
    course_id : ID of the course, foreign key
    course : course this score was played on
    player : player who played this score 
    '''

    id = db.Column(db.Integer, primary_key=True)
    throws = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    player_id = db.Column(db.ForeignKey("player.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)

    course = db.relationship("Course", back_populates="scores", uselist=False)
    player = db.relationship("Player", back_populates="scores", uselist=False)

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["throws", "date", "player_id", "course_id"]
        }
        properties = schema["properties"] = {}
        properties["id"] = {
            "description": "ID of this score",
            "type": "integer"
        }
        properties["throws"] = {
            "description": "Total strokes on this round",
            "type": "integer"
        }
        properties["date"] = {
            "description": "Date this round was played",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]" #TODO: check that this works
        }
        properties["player_id"] = {
            "description": "ID of the player",
            "type": "integer"
        }
        properties["course_id"] = {
            "description": "ID of the course",
            "type": "integer"
        }

        # TODO: player, course
 
        return schema

class Course(db.Model):
    ''' 
    Database model of a frolf course.
    Attributes:
    id : database id, primary key
    name : name of the course
    num_holes : the number of holes on the course
    par : par score of the course 
    scores : all scores played on this course
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    num_holes = db.Column(db.Integer, nullable=False, default=18)
    par = db.Column(db.Integer, nullable=False, default=54)

    scores = db.relationship("Score", cascade="all,delete", back_populates="course")

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        properties = schema["properties"] = {}
        properties["id"] = {
            "description": "Database ID of this course",
            "type": "integer"
        }
        properties["name"] = {
            "description": "Name of this course",
            "type": "string"
        }
        properties["num_holes"] = {
            "description": "Number of holes on this course",
            "type": "integer"
        }
        properties["par"] = {
            "description": "Par score of this course",
            "type": "integer"
        }

        #TODO: scores

        return schema

def init_db_command():
    db.create_all()
