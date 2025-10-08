import typing

import openai.lib._parsing._completions
import pydantic

from ...any_json import JsonDict


CustomPydanticModel = typing.TypeVar("CustomPydanticModel", bound=pydantic.BaseModel)


def make_schema(model: type[CustomPydanticModel]) -> JsonDict:
    response_format_param = openai.lib._parsing._completions.type_to_response_format_param(model)
    assert isinstance(response_format_param, dict)
    assert response_format_param["type"] == "json_schema"
    return response_format_param["json_schema"]["schema"]
