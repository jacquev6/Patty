import pydantic.alias_generators


class ApiModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True, extra="forbid"
    )
