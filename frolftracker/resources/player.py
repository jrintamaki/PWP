import json
from flask import request, Response, url_for
from flask_restful import Resource
from frolftracker.constants import *
from frolftracker.models import Course, Player, Score
from frolftracker.utils import create_error_response

class PlayerItem(Resource):

    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass

class PlayerCollection(Resource):
    
    def get(self, player_id):
        db_player = Player.query.filter_by(id=player_id).first()
        if db_player is None:
            return create_error_response(
                404, "Not found",
                "No player found with the id {}".format(player_id)
            )


    def post(self):
        pass
