# from marshmallow import Schema, fields
from flasgger import Schema, fields


class ClassroomSchema(Schema):
    classroom_name = fields.Str()
    building = fields.Str()
    floor = fields.Int()
    capacity = fields.Int()
    air_conditioning = fields.Bool()
    ignore_to_allocate = fields.Bool()
    projector = fields.Bool()
    accessibility = fields.Bool()
    updated_at = fields.Str()
    created_by = fields.Str()


class AvailableClassroomsQuerySchema(Schema):
    week_day = fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)


class GetAvailableClassroomsSchema(Schema):
    events_ids = fields.List(fields.Str(), required=True)
    building_id = fields.Str(required=True)
