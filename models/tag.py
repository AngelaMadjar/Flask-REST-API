from enum import unique
from tkinter.tix import Tree
from db import db

class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False) # unique is tablewise, not storewise
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)

    store = db.relationship("StoreModel", back_populates = "tags")
    items = db.relationship("ItemModel", back_populates="tags", secondary="items_tags") # goes to the specified secondary table to find the items that the tag is related to

