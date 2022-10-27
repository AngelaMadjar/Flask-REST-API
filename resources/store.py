from email import message
import uuid
from flask import Flask, request
from flask.views import MethodView # used for creating a class whose megthods rout to specific endpoints
from flask_smorest import Blueprint, abort # used to divide an api into multiple segments
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from schemas import StoreSchema
from models import StoreModel


# the name of the blueprint is reffered when we want to create a link between two blueprints
blp = Blueprint("Stores", "stores", __name__, description="Operations on stores") # each blueprint needs a unique name


@blp.route("/store/<int:store_id>")
class Store(MethodView): # inherits from methodviews

    # GET STORE
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        #try:
        #    return stores[store_id]
        #except KeyError:
        #    abort(404, message="Store not found")
        store = StoreModel.query.get_or_404(store_id)
        return store


    # DELETE STORE
    def delete(self, store_id):
        #try:
        #    del stores[store_id]
        #    return {"message": "Store deleted."}
        #except KeyError:
        #    abort(404, message="Store not found.")  
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted."}
        #raise NotImplementedError("Deleting a store is not implemented.")




@blp.route("/store")
class StoreList(MethodView): # inherits from methodviews

    # GET ALL STORES
    @blp.response(200, StoreSchema(many=True)) 
    def get(self):
        #return {"stores": list(stores.values())}
        return StoreModel.query.all()


    # CREATE STORE
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema) # this doesn't change even if we decide to use SQLAlchemy
    def post(self, store_data):
        #store_data = request.get_json()
        #if "name" not in store_data:
        #    abort(400, message="Bad request. Ensure 'name' are in the request.")

        # Ensuring that there won't be a store with the same name
        #for store in stores.values():
        #    if store_data["name"] == store["name"]:
        #        abort(400, message="Store already exists.")

        #store_id = uuid.uuid4().hex
        #new_store = {**store_data, "id": store_id} # collects the attribute from the dictionary and adds a new id attribute
        #stores[store_id] = new_store

        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError: # when a violation of the db constraints happens
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the store.")

        return store



