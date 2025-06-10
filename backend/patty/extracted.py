import pydantic


# These are needed to make extraction more robust:
# @todo Make this model stricter (forbid extra fields, enforce some fields)
# @todo Switch to english names for fields
class Exercise(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")

    id: str | None = None
    numero: str | None = None
    consignes: list[str] = []
    conseil: str | None = None
    exemple: str | None = None
    enonce: str | None = None
    references: str | None = None
    autre: str | None = None
