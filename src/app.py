import json

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flasgger import APISpec, Swagger
from flask import Flask
from flask_cors import CORS

from src.blueprints.building_blueprint import building_blueprint
from src.blueprints.class_blueprint import class_blueprint
from src.blueprints.classroom_blueprint import classroom_blueprint
from src.blueprints.conflict_blueprint import conflict_blueprint
from src.blueprints.event_blueprint import event_blueprint
from src.blueprints.institutional_event_blueprint import institutional_event_blueprint
from src.blueprints.mobile_blueprint import mobile_blueprint
from src.blueprints.self_blueprint import self_blueprint
from src.blueprints.subject_blueprint import subject_blueprint
from src.blueprints.test_blueprint import test_blueprint
from src.blueprints.user_blueprint import user_blueprint
from src.common.cache import cache
from src.schemas.allocation_schema import AllocatorInputSchema, AllocatorOutputSchema
from src.schemas.class_schema import ClassSchema, HasToBeAllocatedClassesSchema
from src.schemas.classroom_schema import AvailableClassroomsQuerySchema, ClassroomSchema
from src.schemas.subject_schema import SubjectSchema


class JSONEncoder(json.JSONEncoder):
    """
    JSON Encoder to transform all ObjectIds into strings
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super(JSONEncoder, self).default(o)


load_dotenv()
app = Flask(__name__)
app.json_encoder = JSONEncoder
CORS(app)
cache.init_app(app)

app.register_blueprint(test_blueprint)
app.register_blueprint(classroom_blueprint)
app.register_blueprint(class_blueprint)
app.register_blueprint(subject_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(mobile_blueprint)
app.register_blueprint(institutional_event_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(building_blueprint)
app.register_blueprint(self_blueprint)
app.register_blueprint(conflict_blueprint)


# Swagger
plugins = [FlaskPlugin(), MarshmallowPlugin()]
spec = APISpec("USPolis", version="1.0", openapi_version="2.0", plugins=plugins)
definitions = [
    ClassroomSchema,
    AvailableClassroomsQuerySchema,
    AllocatorOutputSchema,
    AllocatorInputSchema,
    SubjectSchema,
    ClassSchema,
    HasToBeAllocatedClassesSchema,
]
template = spec.to_flasgger(app, definitions=definitions)
config = {"url_prefix": "/api"}

swagger = Swagger(app, template=template, config=config, merge=True)
