from flasgger import ValidationError

from src.common.general_error import GeneralError


def validate_body(body, schema):
    try:
        if not body:
            raise GeneralError("Body is required", 400)
        data = schema.load(body)
        if data is None:
            raise GeneralError("Invalid body", 400)
        return data
    except ValidationError as e:
        raise GeneralError(e.message, 400)
