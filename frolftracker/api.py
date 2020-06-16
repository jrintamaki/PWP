from flask import Blueprint
from flask_restful import Api, Resource

from frolftracker.resources.entry import EntryPoint
from frolftracker.resources.player import PlayerItem, PlayerCollection
from frolftracker.resources.course import CourseItem, CourseCollection
from frolftracker.resources.score import ScoreItem, ScoreCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(EntryPoint, "/")

api.add_resource(PlayerCollection, "/players/")
api.add_resource(PlayerItem, "/players/<player_id>/")

api.add_resource(CourseCollection, "/courses/")
api.add_resource(CourseItem, "/courses/<course_id>/")

api.add_resource(ScoreCollection, "/scores/")
api.add_resource(ScoreItem, "/scores/<score_id>/")
