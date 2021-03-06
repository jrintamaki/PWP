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
    
    def get(self):
        # Get query parameters from request
        player_id = request.args.get("player_id")
        course_id = request.args.get("course_id")

        body = FrolftrackerBuilder()

        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.scorecollection"))
        body.add_control("frolf:players-all", url_for("api.playercollection"))
        body.add_control("frolf:courses-all", url_for("api.coursecollection"))
        body.add_control_add_score()
        body["items"] = []

        # All scores
        if course_id is None and player_id is None:
            query = Score.query.all()
        # Scores filtered by course AND player
        elif course_id is not None and player_id is not None:
            player = Player.query.filter_by(id=player_id).first()
            query = player.scores.filter_by(course_id=course_id).all()
        # Scores filtered by course
        elif course_id is not None:
            course = Course.query.filter_by(id=course_id).first()
            query = course.scores
        # Scores filtered by player
        elif player_id is not None:
            player = Player.query.filter_by(id=player_id).first()
            query = player.scores

        for db_score in query:
            item = FrolftrackerBuilder(
                score_id=db_score.id,
                throws=db_score.throws,
                date=db_score.date,
                player_id=db_score.player_id,
                course_id=db_score.course_id,
            )
            item.add_control("self", url_for("api.scoreitem", score_id=db_score.id))
            item.add_control("profile", SCORE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Score.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        player = Player.query.filter_by(id=request.json["player_id"]).first()
        if player is None:
            return create_error_response(
                404, "Not found",
                "No player found with the id {}".format(request.json["player_id"])
            )

        course = Course.query.filter_by(id=request.json["course_id"]).first()
        if course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(request.json["course_id"])
            )

        score = Score(
            throws=request.json["throws"],
            date=request.json["date"],
            player_id=request.json["player_id"],
            course_id=request.json["course_id"],
            course=course,
            player=player
        )

        db.session.add(score)
        db.session.commit()


        return Response(status=201, headers={
            "Location": url_for("api.scoreitem", score_id=score.id)
        })

class ScoreItem(Resource):

    def get(self, score_id):
        db_score = Score.query.filter_by(id=score_id).first()
        if db_score is None:
            return create_error_response(
                404, "Not found",
                "No score found with the id {}".format(score_id)
            )

        body = FrolftrackerBuilder(score_id=db_score.id, throws=db_score.throws, date=db_score.date, player_id=db_score.player_id, course_id=db_score.course_id)
        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.scoreitem", score_id=score_id))
        body.add_control("profile", SCORE_PROFILE)
        body.add_control("collection", url_for("api.scorecollection"))
        body.add_control("frolf:player", url_for("api.playeritem", player_id=db_score.player_id), method="GET", title="Player of this score")
        body.add_control("frolf:course", url_for("api.courseitem", course_id=db_score.course_id), method="GET", title="Course of this score")
        body.add_control_delete_score(score_id)
        body.add_control_modify_score(score_id)

        return Response(json.dumps(body), 200, mimetype=MASON)


    def put(self, score_id):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        db_score = Score.query.filter_by(id=score_id).first()
        if db_score is None:
            return create_error_response(
                404, "Not found",
                "No score found with the id {}".format(score_id)
            )

        try:
            validate(request.json, Score.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        player = Player.query.filter_by(id=request.json["player_id"]).first()
        if player is None:
            return create_error_response(
                404, "Not found",
                "No player found with the id {}".format(request.json["player_id"])
            )

        course = Course.query.filter_by(id=request.json["course_id"]).first()
        if course is None:
            return create_error_response(
                404, "Not found",
                "No course found with the id {}".format(request.json["course_id"])
            )

        db_score.throws = request.json["throws"]
        db_score.date = request.json["date"]
        db_score.player_id = request.json["player_id"]
        db_score.course_id = request.json["course_id"]
        db_score.course = course
        db_score.player = player

        db.session.commit()

        return Response(status=204)

    def delete(self, score_id):
        db_score = Score.query.filter_by(id=score_id).first()
        if db_score is None:
            return create_error_response(
                404, "Not found",
                "No score found with the id {}".format(score_id)
            )

        db.session.delete(db_score)
        db.session.commit()

        return Response(status=204)
