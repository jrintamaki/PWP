import json
from jsonschema import validate, ValidationError
from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from frolftracker import db
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response, FrolftrackerBuilder

class CourseCollection(Resource):
    
    def get(self, course_id):
        pass

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Course.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        
        course = Course(
            name=request.json["name"],
        )

        if request.json["num_holes"]:
            course.num_holes = request.json["num_holes"]
        if request.json["par"]:
            course.par = request.json["par"]

        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Course with name '{}' already exists.".format(request.json["name"])
            )

class CourseItem(Resource):

    def get(self, id):
        db_course = Course.query.filter_by(id=course_id).first()
        if db_course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(course_id)
            )

    def put(self, id):
        pass

    def delete(self, id):
        pass
