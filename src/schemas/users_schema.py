# from marshmallow import Schema, fields
from flasgger import Schema, fields

class UserSchema(Schema):
  username = fields.Str()
  building = fields.Str()