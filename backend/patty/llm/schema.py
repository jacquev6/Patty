from typing import Any, Type, TypeVar

from pydantic import BaseModel
import mistralai.extra
import openai.lib._parsing._completions


CustomPydanticModel = TypeVar("CustomPydanticModel", bound=BaseModel)


def make_schema(model: Type[CustomPydanticModel]) -> dict[str, Any]:
    mistralai_response_format = mistralai.extra.response_format_from_pydantic_model(model)
    assert isinstance(mistralai_response_format.json_schema, mistralai.models.JSONSchema)
    schema = mistralai_response_format.json_schema.schema_definition
    openai_response_format = openai.lib._parsing._completions.type_to_response_format_param(model)
    assert isinstance(openai_response_format, dict)
    assert openai_response_format["type"] == "json_schema"
    assert schema == openai_response_format["json_schema"]["schema"]
    return schema
