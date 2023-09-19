from flask import Flask
from flask_cors import CORS
from flasgger import APISpec, Swagger
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from src.common.cache import cache

from src.blueprints.classroom_blueprint import classroom_blueprint
from src.blueprints.class_blueprint import class_blueprint
from src.blueprints.subject_blueprint import subject_blueprint
from src.blueprints.event_blueprint import event_blueprint
from src.blueprints.mobile_blueprint import mobile_blueprint
from src.blueprints.test_blueprint import test_blueprint

from src.schemas.classroom_schema import ClassroomSchema, AvailableClassroomsQuerySchema
from src.schemas.allocation_schema import AllocatorInputSchema, AllocatorOutputSchema
from src.schemas.subject_schema import SubjectSchema
from src.schemas.class_schema import ClassSchema, HasToBeAllocatedClassesSchema

from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)
cache.init_app(app)

app.register_blueprint(test_blueprint)
app.register_blueprint(classroom_blueprint)
app.register_blueprint(class_blueprint)
app.register_blueprint(subject_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(mobile_blueprint)


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
  HasToBeAllocatedClassesSchema
  ]
template = spec.to_flasgger(app, definitions=definitions)
config = {
  "url_prefix" : "/api"
}

swagger =  Swagger(app, template=template, config=config, merge=True)
