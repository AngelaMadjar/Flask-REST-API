from marshmallow import Schema, fields

# using marshmallow to check the type of data and whether it is required or optional
# used for validating the input data upon requests and ensuring that the output is in the correct form

# whenever we create an item, it'll have a nested store object 
# the store object will have a nested list of item objects
# we need to reflect this but in certain cases
# PlainItemSchema doesn't know anything about stores and doesn't deal with stores at all
# used when we want to include a nested item within a store but we don't want to add info about the store to the item
class PlainItemSchema(Schema):
    # item: id, name, price, store_id
    # defining these fields and how they behave on input and output
    id = fields.Int(dump_only=True) # is this coming from loading data from our request? or from returning data from our api?
                                    # we generate this in the function => dump_only = used for returning data from the API
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    #store_id = fields.Str(required=True) # this way, the fields without the id will be validated upon request
    

# Similarely, we also have PlainStoreSchema
class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ItemSchema(PlainItemSchema): # it'll have all of the fields of the PlainItemSchema
    store_id = fields.Int(required=True, load_only=True) # passing the store id when recieving data from the client
    store = fields.Nested(PlainStoreSchema(), dump_only=True) # passing the nested dobject as well
    tags = fields.Nested(PlainTagSchema(), dump_only=True)

class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int() # optional - when making the update function idempotent


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
# We use Plain Schemas so that when we use Nesting we can only include a part of the fields, so we don't end up in recursion

# we can use lambda when we want to create an object of a class that is yet to be defined


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True) # we never want to return the password when we receive a request for user info and load_only does this
    