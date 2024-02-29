from marshmallow import EXCLUDE
from flasgger import Schema, fields


from src.schemas.class_schema import PreferencesSchema

class EventSchema(Schema):
  class_code = fields.Str()
  subject_code = fields.Str()
  subject_name = fields.Str()
  professor = fields.Str()
  start_period = fields.Str()
  end_period = fields.Str()
  start_time = fields.Str()
  end_time = fields.Str()
  week_day = fields.Str()
  class_type = fields.Str()
  vacancies = fields.Int()
  subscribers = fields.Int()
  pendings = fields.Int()
  preferences = fields.Nested(PreferencesSchema(unknown=EXCLUDE))
  has_to_be_allocated = fields.Bool()
  classroom = fields.Str()
  building = fields.Str()
  updated_at = fields.Str()
  created_by = fields.Str()
