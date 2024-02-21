from flasgger import Schema, fields

class BuildingInputSchema(Schema):
  name = fields.Str()