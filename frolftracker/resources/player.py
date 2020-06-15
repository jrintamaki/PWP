import json
from jsonschema import validate, ValidationError
from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from frolftracker import db
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response, FrolftrackerBuilder

class PlayerCollection(Resource):
    
    def get(self, player_name):
        pass

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Player.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        player = Player(
            name=request.json["name"]
        )

        try:
            db.session.add(player)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Player with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.playeritem", sensor=request.json["name"])
        })


class PlayerItem(Resource):

    def get(self, player_id):
        db_player = Player.query.filter_by(id=player_id).first()
        if db_player is None:
            return create_error_response(
                404, "Not found",
                "No player found with the id {}".format(player_id)
            )

        body = FrolftrackerBuilder(player_id=db_player.id, name=db_player.name, scores=db_player.scores)
        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playeritem", player_id=player_id))
        body.add_control("profile", PLAYER_PROFILE)
        body.add_control("collection", url_for("api.playercollection"))
        body.add_control_delete_player(player_id)
        body.add_control_modify_player(player_id)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, player_id):
        pass

    def delete(self, player_id):
        pass
