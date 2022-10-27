from db import db

# the db instance can be used to tell which tables we will be using in our app
# and what columns will those tables have

# any class created that maps to a table with columns will be automatically handled by sqlalchemy
# by turning those table rows into python objects

class ItemModel(db.Model):
    __tablename__ = "items" # we will create an use a table names items for rthis class and the objects of this class

    # defining columns that should be in this table
    id = db.Column(db.Integer, primary_key = True) # autoincrementing
    name = db.Column(db.String(80), unique=True, nullable=False) # max 80 chars, cannot be null
    description = db.Column(db.String) # change for illustrating db migrations
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False) # FOREIGN KEY (one-to-many relationship because each item has one store associated with it, but a store can have many items associate with it)
    store = db.relationship("StoreModel", back_populates="items") # grab a storemodel object that has this store_id
                                                                # populates the store var with a StoreModel object whose id matches that of the foreign key
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")

                        

