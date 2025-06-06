from __future__ import annotations

import datetime
import inspect
import typing

from sqlalchemy import orm
import sqlalchemy as sql
import pydantic

from . import llm
from .adapted import Exercise as AdaptedExercise
from .any_json import JsonDict, JsonList
from .database_utils import OrmBase as OrmBaseBase
from .adaptation.adaptation import Adjustment, AssistantResponse
from .adaptation.strategy import ConcreteLlmResponseSpecification

# @todo: Remove ORM models in 'adaptation', move the models in this file into 'orm_models.py', remove this file.


class OrmBase(OrmBaseBase):
    __abstract__ = True

    def __init__(self, **kwargs: typing.Any) -> None:
        cls = type(self)
        for column in typing.cast(sql.Table, cls.__table__).columns:
            ok = column.name == "id" or column.name in kwargs
            if not ok and column.name.endswith("_id"):
                ok = column.name[:-3] in kwargs
            if not ok:
                for caller_frame in inspect.stack()[1:]:
                    if caller_frame.filename.startswith("/app"):
                        break
                print(
                    f"WARNING: on {caller_frame.filename}:{caller_frame.lineno}, field '{column.name}' of {cls.__name__} is not set"
                )
        super().__init__(**kwargs)


class Textbook(OrmBase):
    __tablename__ = "textbooks"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    title: orm.Mapped[str]

    exercises: orm.Mapped[list[BaseExercise]] = orm.relationship(
        back_populates="textbook", order_by=lambda: [BaseExercise.page_number, BaseExercise.exercise_number]
    )

    adaptation_batches: orm.Mapped[list[AdaptationBatch]] = orm.relationship(
        back_populates="textbook", order_by=lambda: [AdaptationBatch.id]
    )


class BaseExercise(OrmBase):
    __tablename__ = "exercises"
    # __abstract__ = True

    __mapper_args__ = {"polymorphic_on": "kind"}

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    kind: orm.Mapped[str]

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook | None] = orm.relationship(foreign_keys=[textbook_id], remote_side=[Textbook.id])
    removed_from_textbook: orm.Mapped[bool]
    page_number: orm.Mapped[int | None] = orm.mapped_column()
    # Custom collation: migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str | None] = orm.mapped_column(sql.String(collation="exercise_number"))


class ExternalExercise(BaseExercise):
    __tablename__ = "external_exercises"

    __mapper_args__ = {"polymorphic_identity": "external"}

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(BaseExercise.id), primary_key=True)

    original_file_name: orm.Mapped[str]


class ClassificationBatch(OrmBase):
    __tablename__ = "classification_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    exercises: orm.Mapped[list[AdaptableExercise]] = orm.relationship(
        back_populates="classified_by_classification_batch", order_by=lambda: [AdaptableExercise.id]
    )

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()

    adaptations: orm.Mapped[list[Adaptation]] = orm.relationship(
        back_populates="classification_batch", order_by="Adaptation.id"
    )


class ExerciseClass(OrmBase):
    __tablename__ = "exercise_classes"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    name: orm.Mapped[str]

    latest_strategy_settings_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey("adaptation_strategy_settings.id", use_alter=True)
    )
    latest_strategy_settings: orm.Mapped[AdaptationStrategySettings | None] = orm.relationship(
        foreign_keys=[latest_strategy_settings_id], remote_side=lambda: [AdaptationStrategySettings.id]
    )


class AdaptableExercise(BaseExercise):
    __tablename__ = "adaptable_exercises"

    __mapper_args__ = {"polymorphic_identity": "adaptable"}

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(BaseExercise.id), primary_key=True)

    full_text: orm.Mapped[str]
    instruction_hint_example_text: orm.Mapped[str | None]
    statement_text: orm.Mapped[str | None]

    classified_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(sql.DateTime(timezone=True))
    classified_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    classified_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[classified_by_classification_batch_id],
        remote_side=[ClassificationBatch.id],
        back_populates="exercises",
    )
    classified_by_username: orm.Mapped[str | None]
    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=[ExerciseClass.id]
    )

    adaptation: orm.Mapped[Adaptation | None] = orm.relationship(back_populates="exercise")


class AdaptationStrategySettings(OrmBase):
    __tablename__ = "adaptation_strategy_settings"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=[ExerciseClass.id]
    )

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("adaptation_strategy_settings.id"))
    parent: orm.Mapped[AdaptationStrategySettings | None] = orm.relationship(
        foreign_keys=[parent_id], remote_side=lambda: [AdaptationStrategySettings.id]
    )

    system_prompt: orm.Mapped[str]
    _response_specification: orm.Mapped[JsonDict] = orm.mapped_column("response_specification", sql.JSON)

    @property
    def response_specification(self) -> ConcreteLlmResponseSpecification:
        return pydantic.RootModel[ConcreteLlmResponseSpecification](self._response_specification).root  # type: ignore[arg-type]

    @response_specification.setter
    def response_specification(self, value: ConcreteLlmResponseSpecification) -> None:
        self._response_specification = value.model_dump()


class AdaptationStrategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategySettings.id))
    settings: orm.Mapped[AdaptationStrategySettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[AdaptationStrategySettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> llm.ConcreteModel:
        return pydantic.RootModel[llm.ConcreteModel](self._model).root  # type: ignore[arg-type]

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()


class AdaptationBatch(OrmBase):
    __tablename__ = "adaptation_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategy.id))
    strategy: orm.Mapped[AdaptationStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[AdaptationStrategy.id]
    )

    textbook_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(Textbook.id))
    textbook: orm.Mapped[Textbook | None] = orm.relationship(
        foreign_keys=[textbook_id], remote_side=[Textbook.id], back_populates="adaptation_batches"
    )
    removed_from_textbook: orm.Mapped[bool]

    adaptations: orm.Mapped[list[Adaptation]] = orm.relationship(
        back_populates="adaptation_batch", order_by="Adaptation.id"
    )


class Adaptation(OrmBase):
    __tablename__ = "adaptations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]

    exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptableExercise.id))
    exercise: orm.Mapped[AdaptableExercise] = orm.relationship(
        foreign_keys=[exercise_id], remote_side=[AdaptableExercise.id], back_populates="adaptation"
    )

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategy.id))
    strategy: orm.Mapped[AdaptationStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[AdaptationStrategy.id]
    )

    classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ClassificationBatch.id))
    classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[classification_batch_id], remote_side=[ClassificationBatch.id], back_populates="adaptations"
    )

    adaptation_batch_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(AdaptationBatch.id))
    adaptation_batch: orm.Mapped[AdaptationBatch | None] = orm.relationship(
        foreign_keys=[adaptation_batch_id], remote_side=[AdaptationBatch.id], back_populates="adaptations"
    )

    # Help investigation of future issues
    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)

    _initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("initial_assistant_response", sql.JSON)

    @property
    def initial_assistant_response(self) -> AssistantResponse | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return pydantic.RootModel[AssistantResponse](self._initial_assistant_response).root  # type: ignore[arg-type]

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: AssistantResponse | None) -> None:
        if value is None:
            self._initial_assistant_response = sql.null()
        else:
            self._initial_assistant_response = value.model_dump()

    _adjustments: orm.Mapped[JsonList] = orm.mapped_column("adjustments", sql.JSON)

    @property
    def adjustments(self) -> list[Adjustment]:
        return [Adjustment(**adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[Adjustment]) -> None:
        self._adjustments = [adjustment.model_dump() for adjustment in value]

    _manual_edit: orm.Mapped[JsonDict | None] = orm.mapped_column("manual_edit", sql.JSON)

    @property
    def manual_edit(self) -> AdaptedExercise | None:
        if self._manual_edit is None:
            return None
        else:
            return AdaptedExercise(**self._manual_edit)

    @manual_edit.setter
    def manual_edit(self, value: AdaptedExercise | None) -> None:
        if value is None:
            self._manual_edit = sql.null()
        else:
            self._manual_edit = value.model_dump()
