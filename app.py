import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
import models # need to be imported before initializing swlalchemy so that it knows how to create the tables

from resources.items import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint



def create_app(db_url=None): # factory pattern
    # creates an app for us
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True # a flask config that makes exceptions that occured inside the classes visible in the main class
    app.config["API_TITLE"] = "Stores REST API" # name of the api
    app.config["API_VERSION"] = "v1" # version of the api that we're currently working on
    app.config["OPENAPI_VERSION"] = "3.0.3" # standard for api documentation
    app.config["OPENAPI_URL_PREFIX"] = "/" # tells flask smorest where the root of the api is
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" # it tells smorest to use swagger for documentation of the api
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # usually, connection strings are stored and used from env variables, so that when we share our coce, other users don't have access to it
    # will use db_url if not None, else it'll use the environment variable. If it also doensn't exist, it'll use sqlite
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db") # an easy way of creating a connection string (before we migrate to postgres)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app) # initializing the flask sqlalchemy extension, giving it our flask app so that it connects it to the sqlalchemy

    migrate = Migrate(app, db) # a connection between flask and alemic

    api = Api(app)

    # should be stored in an environment var
    app.config["JWT_SECRET_KEY"] =  "300236127466337743041278049002610707889" # used for signing the access to"ken. It is later checked to see if the JWT token of a user is valid
    jwt = JWTManager(app) # making sure that the user is not pretending 

    # checks if the token is in the blosklist 
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.additional_claims_loader # allows adding extra info to a jwt token
    def add_claims_to_jwt(identity): # when creating an access token, it has an identity -- which is passed to this function
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # since we will be using flask-migrate to create db tables, we no longer need SQLAlchemy to do it
    # thus, we'll comment out the function bellow
    #@app.before_first_request
    #def create_tables():
    #    db.create_all() # create all the tables in the db before the first ever request

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app