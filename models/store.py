from db import db

# each store can have many items associated with it
class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False) # maps to the store_id in items table
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic") # by defining the relationships, sqlalchemy knows the two ends of the relationship and thus, we don't explicitly need the itmes ids. It will collect all items whose store_id is equal to the store's id
                                                                                # lazy="dynamic" means that the items won't be fatched from the db until we tell to. This is beause when we fetch a StoreModel from the db, it creates a query and it takes some time. Populating the items in this realtionship creates another query which takes even more time
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic") # the name of back_propagates must match the name of the model in TagModel
