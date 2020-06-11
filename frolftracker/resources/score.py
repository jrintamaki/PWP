import json
from flask import request, Response, url_for
from flask_restful import Resource
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response

class ScoreItem(Resource):

    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass

class ScoreCollection(Resource):
    
    def get(self, score_id):
        db_score = Score.query.filter_by(id=score_id).first()
        if db_score is None:
            return create_error_response(
                404, "Not found",
                "No score found with the id {}".format(score_id)
            )

    def post(self):
        pass
