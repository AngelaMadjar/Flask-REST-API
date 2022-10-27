from flask.views import MethodView # used for creating a class whose megthods rout to specific endpoints
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.item import ItemModel # used to divide an api into multiple segments
from schemas import ItemSchema, ItemUpdateSchema

# the name of the blueprint is reffered when we want to create a link between two blueprints
blp = Blueprint("Items", "items", __name__, description="Operations on stores") # each blueprint needs a unique name


@blp.route("/item/<int:item_id>")
class Item(MethodView): # inherits from methodviews

    # GET ITEM
    #@jwt_required()
    @blp.response(200, ItemSchema) # dump_only args are also included in the response
    def get(self, item_id):
        #try:
        #    return items[item_id]
        #except KeyError:
        #    abort(404, message="Item not found")
        item  = ItemModel.query.get_or_404(item_id) # retrieves an item by its primary key. No need from error handling
        return item


    # DELETE ITEM
    @jwt_required()
    def delete(self, item_id):
        #try:
        #    del items[item_id]
        #    return {"message": "Item Deleted."}
        #except KeyError:
        #    abort(404, message="Item not found.")
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilige required")
        
        item  = ItemModel.query.get_or_404(item_id) # retrieves an item by its primary key. No need from error handling
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted."}


    # UPDATE ITEM
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema) # response should be deeper than the arguments
    def put(self, item_data, item_id): # it is important that item_data goes IN FRONT OF every other root arg
        #item_data = request.get_json()
        #if "price" not in item_data or "name" not in item_data:
        #    abort(400, "Bad request. Ensure that 'name' and 'price' are in the request.")
        
        #try:
        #    item = items[item_id]
        #    item.update(item_data) # changes the contents of item_data

        #    return item
        #except KeyError:
        #    abort(404, message="Item not found.")

        item = ItemModel.query.get(item_id) # we want to acheive idempotent request - running 1 or 100 reqs needs to result in the same state
        # if the requested item doesn't exist => create it. If it does => update it
        # the result in both cases is an item
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data) # if store_id is not passed, we'll get an error here

        db.session.add(item)
        db.session.commit()

        return item



@blp.route("/item")
class ItemList(MethodView): # inherits from methodviews

    # GET ALL ITEMS
    #@jwt_required()
    @blp.response(200, ItemSchema(many=True)) # many=True turns the response into a List
    def get(self):
        #return {"items": list(items.values())}
        return ItemModel.query.all()


    # CREATE ITEM
    @jwt_required(fresh=True) # can't call this endpoint unless we sent a jwt
    @blp.arguments(ItemSchema) # the json that the client sends is passed through the ItemSchema to validate the arguments
    @blp.response(201, ItemSchema)
    def post(self, item_data): # then it gives the method an agrument which is a validated dictionary (item_data)
        # item_data = request.get_json()
        # ensuring that the request contains the requested arguments
        # despite this, we should also ensure of the passed arguments' type, but we'll do this later with marshmallow
        #if("price" not in item_data 
        #    or "store_id" not in item_data
        #    or "name" not in item_data):
        #    abort(400, message="Bad request. Ensure 'price', 'store_it', 'name' are in the request.")


        # we already do this in the models, when creating the columns of the db
        # Ensuring that there won't be an item with the same name
        #for item in items.values():
        #    if(item_data["name"] == item["name"]
        #        and item_data["store_id"] == item["store_id"]):
        #        abort(400, message="Item already exists.")

        #if item_data["store_id"] not in stores:
        #    abort(404, message="Store not found") # smorest for better documentation
        
        #item_id = uuid.uuid4().hex
        #item = {**item_data, "id": item_id}
        #items[item_id] = item

        item = ItemModel(**item_data) # we don't pass the id because the db does that for us
        # the validation checks are not performed and the id is not created until we assign the model to the db
        try:
            db.session.add(item) 
            db.session.commit() # saving changes to "disk"
        except SQLAlchemyError:
            abort(500, message="An error has occured while inserting the item.")

        return item



