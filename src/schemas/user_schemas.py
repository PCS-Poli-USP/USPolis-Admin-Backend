# from marshmallow import Schema, fields
from flasgger import Schema, fields

class UserInputSchema(Schema):
  name = fields.Str()
  username = fields.Str()
  email = fields.Str()
  isAdmin = fields.Bool()
  building_ids = fields.List(fields.Str(), required=False)

class UserOutputSchema(Schema):
  _id = fields.Str()
  name = fields.Str()
  username = fields.Str()
  created_by = fields.Str()
  updated_at = fields.Str()
  updated_by = fields.Str()