from flasgger import Schema, fields
from marshmallow import post_load

from src.schemas.class_schema import PreferencesSchema


class AllocatorInputSchema(Schema):
    class_code = fields.Str()
    subject_code = fields.Str()
    week_day = fields.Str()
    start_time = fields.Time("%H:%M")
    end_time = fields.Time("%H:%M")
    subscribers = fields.Int()
    preferences = fields.Nested(PreferencesSchema)
    has_to_be_allocated = fields.Bool()

    @post_load
    def create_ids(self, data, **_):
        data["event_id"] = (
            data["subject_code"] + "_" + data["class_code"] + "_" + data["week_day"]
        )
        data["class_id"] = data["subject_code"] + "_" + data["class_code"]
        return data


class AllocatorOutputSchema(Schema):
    class_code = fields.Str()
    subject_code = fields.Str()
    week_day = fields.Str()
    start_time = fields.Str()
    end_time = fields.Str()
    classroom = fields.Str()
    building = fields.Str()


class UpdateManyAllocationsSchema(Schema):
    events_ids = fields.List(fields.String(), required=True)
    building_id = fields.String(required=True)
    classroom = fields.String(required=True)

class UpdateManyAllocationsInManyBuildingsSchema(Schema):
    events_ids = fields.List(fields.String(), required=True)
    buildings_ids = fields.List(fields.String(), required=True)
    classrooms = fields.List(fields.String(), required=True)
