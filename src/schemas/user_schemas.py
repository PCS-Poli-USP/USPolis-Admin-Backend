# from marshmallow import Schema, fields
from flasgger import Schema, fields

class UserSchema(Schema):
  username = fields.Str()

class UserInputSchema(Schema):
  username = fields.Str()

class UserOutputSchema(Schema):
  _id = fields.Str()
  username = fields.Str()
  created_by = fields.Str()
  updated_at = fields.Str()
  updated_by = fields.Str()