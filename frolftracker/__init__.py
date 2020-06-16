import os
from flask import Flask, Response, url_for
from flask_sqlalchemy import SQLAlchemy
import json

from frolftracker.constants import *

db = SQLAlchemy()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy by Mika Oja (https://github.com/enkwolf/pwp-course-sensorhub-api-example/)
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)

    from . import api
    app.register_blueprint(api.api_bp)
    
    @app.route("/api/")
    def entry():
        return "tomi pls fix"

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return "tomi pls fix"
    
    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "tomi pls fix"



    return app
