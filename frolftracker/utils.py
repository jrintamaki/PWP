import json
from flask import Response, request, url_for
from frolftracker.constants import *
from frolftracker.models import *

# NOTE: MasonBuilder, FrolftrackerBuilder classes and error response function borrowed from PWP exercises
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href



class FrolftrackerBuilder(MasonBuilder):

    def add_control_add_player(self, player):
        self.add_control(
            "frolftracker:add-player",
            url_for("api.playercollection", player=player),
            method="POST",
            encoding="json",
            title="Add a new player",
            schema=Player.get_schema()
        )

    def add_control_delete_player(self, player):
        self.add_control(
            "frolftracker:delete-player",
            url_for("api.playeritem", player=player),
            method="DELETE",
            title="Delete this player"
        )

    def add_control_modify_player(self, player):
        self.add_control(
            "frolftracker:modify-player",
            url_for("api.playeritem", player=player),
            method="PUT",
            encoding="json",
            title="Edit this player",
            schema=Player.get_schema()
        )

    def add_control_add_course(self, course):
        self.add_control(
            "frolftracker:add-course",
            url_for("api.coursecollection", course=course),
            method="POST",
            encoding="json",
            title="Add a new course",
            schema=Course.get_schema()
        )

    def add_control_delete_course(self, course):
        self.add_control(
            "frolftracker:delete-course",
            url_for("api.courseitem", course=course),
            method="DELETE",
            title="Delete this course"
        )

    def add_control_modify_course(self, course):
        self.add_control(
            "frolftracker:modify-course",
            url_for("api.courseitem", course=course),
            method="PUT",
            encoding="json",
            title="Edit this course",
            schema=Course.get_schema()
        )

    def add_control_add_score(self, score):
        self.add_control(
            "frolftracker:add-score",
            url_for("api.scorecollection", score=score),
            method="POST",
            encoding="json",
            title="Add a new score",
            schema=Score.get_schema()
        )

    def add_control_delete_score(self, score):
        self.add_control(
            "frolftracker:delete-score",
            url_for("api.scoreitem", score=score),
            method="DELETE",
            title="Delete this score"
        )

    def add_control_modify_score(self, score):
        self.add_control(
            "frolftracker:modify-score",
            url_for("api.scoreitem", score=score),
            method="PUT",
            encoding="json",
            title="Edit this score",
            schema=Score.get_schema()
        )

    def add_control_get_scores_by_player(self, player):
        base_uri = url_for("api.scorecollection", player=player),
        uri = base_uri + "?start={index}"
        self.add_control(
            "frolftracker:scores",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    def add_control_get_scores_by_course(self, course):
        base_uri = url_for("api.scorecollection", course=course),
        uri = base_uri + "?start={index}"
        self.add_control(
            "frolftracker:scores",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )


    @staticmethod
    def _paginator_schema():
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        props = schema["properties"]
        props["index"] = {
            "description": "Starting index for pagination",
            "type": "integer",
            "default": "0"
        }
        return schema


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)