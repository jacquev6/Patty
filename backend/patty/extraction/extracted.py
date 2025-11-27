import typing
import pydantic


class Base(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")


# Legacy
class ExerciseV1(Base):
    id: str | None = None
    numero: str | None = None
    consignes: list[str] = []
    conseil: str | None = None
    exemple: str | None = None
    enonce: str | None = None
    references: str | None = None
    autre: str | None = None


# Starting with #92
class ExerciseV2(Base):
    id: str | None = None
    type: typing.Literal["exercice"] = "exercice"
    images: bool = False
    type_images: typing.Literal["none", "unique", "ordered", "unordered", "composite"] = "none"

    class Properties(Base):
        numero: str | None = None
        consignes: list[str] = []
        enonce: str | None = None
        conseil: str | None = None
        exemple: str | None = None
        references: str | None = None
        autre: str | None = None

    properties: Properties = Properties()


ExercisesV2List = pydantic.RootModel[list[ExerciseV2]]
