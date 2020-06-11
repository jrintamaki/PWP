import json
from flask import request, Response, url_for
from flask_restful import Resource
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response

class CourseItem(Resource):

    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass

class CourseCollection(Resource):
    
    def get(self, course_id):
        db_course = Course.query.filter_by(id=course_id).first()
        if db_course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(course_id)
            )
            
    def post(self):
        pass
