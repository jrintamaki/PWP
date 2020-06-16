from flask_restful import Resource
from flask import Response, url_for
import json
from frolftracker.utils import MasonBuilder
from frolftracker.constants import *

class EntryPoint(Resource):

    def get(self):
        body = MasonBuilder()
        body.add_namespace("frolf", LINK_RELATIONS_URL)
        body.add_control("players-all", url_for("api.playercollection"))
        body.add_control("courses-all", url_for("api.coursecollection"))
        body.add_control("scores-all", url_for("api.scorecollection"))
        
        return Response(json.dumps(body), status=200, mimetype=MASON)
