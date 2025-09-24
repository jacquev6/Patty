import typing
import pydantic


# Legacy, before #92
class ExerciseWithoutImages(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")

    id: str | None = None
    numero: str | None = None
    consignes: list[str] = []
    conseil: str | None = None
    exemple: str | None = None
    enonce: str | None = None
    references: str | None = None
    autre: str | None = None


class Exercise(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")

    id: str | None = None
    type: typing.Literal["exercice"] = "exercice"
    images: bool = False
    type_images: typing.Literal["none", "unique", "ordered", "unordered", "composite"] = "none"

    class Properties(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="ignore")

        numero: str | None = None
        consignes: list[str] = []
        enonce: str | None = None
        conseil: str | None = None
        exemple: str | None = None
        references: str | None = None
        autre: str | None = None

    properties: Properties = Properties()


ExercisesList = pydantic.RootModel[list[Exercise]]
