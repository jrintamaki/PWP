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
    
    def get(self):
        body = FrolftrackerBuilder()

        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.coursecollection"))
        body.add_control_add_course()
        body["items"] = []
        for db_course in Course.query.all():
            item = FrolftrackerBuilder(
                name=db_course.name,
                num_holes=db_course.num_holes,
                par=db_course.par
            )
            item.add_control("self", url_for("api.courseitem", course_id=db_course.id))
            item.add_control("profile", COURSE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

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

        return Response(status=201, headers={
            "Location": url_for("api.courseitem", course_id=course.id)
        })


class CourseItem(Resource):

    def get(self, course_id):
        db_course = Course.query.filter_by(id=course_id).first()
        if db_course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(course_id)
            )

        body = FrolftrackerBuilder(course_id=db_course.id, name=db_course.name)
        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.courseitem", course_id=course_id))
        body.add_control("profile", COURSE_PROFILE)
        body.add_control("collection", url_for("api.coursecollection"))
        body.add_control_delete_course(course_id)
        body.add_control_modify_course(course_id)
        body.add_control_get_scores_by_course(course_id)

        return Response(json.dumps(body), 200, mimetype=MASON)


    def put(self, course_id):
        db_course = Course.query.filter_by(id=course_id).first()
        if db_course is None:
            return create_error_response(
                404, "Not found",
                "No course was found with the ID {}".format(course_id)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Course.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_course.name = request.json["name"]
        db_course.num_holes = request.json["num_holes"]
        db_course.par = request.json["par"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                500, "TODO",
                "TODO '{}'.".format(request.json["id"])
            )

        return Response(status=204)


    def delete(self, course_id):
        db_course = Course.query.filter_by(id=course_id).first()
        if db_course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(course_id)
            )

        db.session.delete(db_course)
        return Response(status=204)


