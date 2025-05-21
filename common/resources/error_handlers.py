from flask_resources import HTTPJSONException
from jsonschema.exceptions import ValidationError
from oarepo_runtime.services.relations.errors import InvalidRelationError


def create_json_exception_handler():
    return lambda e: HTTPJSONException(
        code=400,
        description=str(e),
    )


ERROR_HANDLERS = {
    InvalidRelationError: create_json_exception_handler(),
    ValidationError: create_json_exception_handler(),
}
