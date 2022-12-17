# from marshmallow import Schema, fields
from flasgger import Schema, fields

class SubjectSchema(Schema):
  subject_name = fields.Str()
  subject_code = fields.Str()