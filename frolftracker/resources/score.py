import json
from jsonschema import validate, ValidationError
from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from frolftracker import db
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response, FrolftrackerBuilder

class ScoreCollection(Resource):
    
    def get(self, score_id):
        pass

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Sensor.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        score = Score(
            throws=request.json["throws"],
            date=request.json["date"]
        )

        try:
            db.session.add(score)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                500, "Score",
                "Something went wrong :(")
            )

class ScoreItem(Resource):

    def put(self, score_id):
        db_score = Score.query.filter_by(id=score_id).first()
        if db_score is None:
            return create_error_response(
                404, "Not found",
                "No score found with the id {}".format(score_id)
            )

    def delete(self, score_id):
        pass
