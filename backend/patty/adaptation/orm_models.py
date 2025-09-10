from __future__ import annotations

import typing
import datetime

from sqlalchemy import orm
import sqlalchemy as sql

from . import adapted
from . import assistant_responses
from . import llm
from . import strategy
from ..any_json import JsonDict, JsonList
from ..database_utils import CreatedByUserMixin, OrmBase, OrderBy, annotate_new_tables
from ..exercises import Exercise, ExerciseCreation, ExerciseLocation

if typing.TYPE_CHECKING:
    from ..classification import ExerciseClassCreation, Classification


class AdaptableExercise(Exercise):
    __tablename__ = "exercises__adaptable"
    __mapper_args__ = {"polymorphic_identity": "adaptable"}

    def __init__(
        self,
        *,
        created: ExerciseCreation,
        location: ExerciseLocation,
        full_text: str,
        instruction_hint_example_text: str | None,
        statement_text: str | None,
    ) -> None:
        super().__init__(created=created, location=location)
        self.full_text = full_text
        self.instruction_hint_example_text = instruction_hint_example_text
        self.statement_text = statement_text

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Exercise.id), primary_key=True)
    full_text: orm.Mapped[str]
    instruction_hint_example_text: orm.Mapped[str | None]
    statement_text: orm.Mapped[str | None]

    adaptations: orm.Mapped[list[Adaptation]] = orm.relationship(back_populates="exercise")

    def fetch_latest_adaptation(self, exercise_class: ExerciseClass) -> Adaptation | None:
        # @todo Do this in SQL?
        adaptations = list(
            filter(lambda adaptation: adaptation.settings.exercise_class == exercise_class, self.adaptations)
        )
        if len(adaptations) == 0:
            return None
        else:
            return max(adaptations, key=lambda adaptation: adaptation.created.at)

    @staticmethod
    def classifications_order_by() -> OrderBy:
        from ..classification import Classification

        return [Classification.at]

    classifications: orm.Mapped[list[Classification]] = orm.relationship(
        back_populates="exercise", order_by=classifications_order_by
    )


# @todo Move to 'classification' (requires reversing the foreign key ExerciseAdaptationSettings.exercise_class_id)
class ExerciseClass(OrmBase):
    __tablename__ = "exercise_classes"

    def __init__(
        self, *, created: ExerciseClassCreation, name: str, latest_strategy_settings: AdaptationSettings | None
    ) -> None:
        super().__init__()
        self.created = created
        self.name = name
        self.latest_strategy_settings = latest_strategy_settings

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[ExerciseClassCreation] = orm.relationship(back_populates="exercise_class")

    name: orm.Mapped[str]

    latest_strategy_settings_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey("adaptation_settings.id", use_alter=True)
    )
    latest_strategy_settings: orm.Mapped[AdaptationSettings | None] = orm.relationship(
        foreign_keys=[latest_strategy_settings_id], remote_side=lambda: [AdaptationSettings.id]
    )


class AdaptationSettings(OrmBase, CreatedByUserMixin):
    __tablename__ = "adaptation_settings"

    def __init__(
        self,
        *,
        created_by: str,
        created_at: datetime.datetime,
        exercise_class: ExerciseClass | None,
        parent: AdaptationSettings | None,
        system_prompt: str,
        response_specification: strategy.ConcreteLlmResponseSpecification,
    ) -> None:
        super().__init__(created_by=created_by, created_at=created_at)
        self.exercise_class = exercise_class
        self.parent = parent
        self.system_prompt = system_prompt
        self.response_specification = response_specification

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    exercise_class_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(ExerciseClass.id))
    exercise_class: orm.Mapped[ExerciseClass | None] = orm.relationship(
        foreign_keys=[exercise_class_id], remote_side=lambda: [ExerciseClass.id]
    )

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey("adaptation_settings.id"))
    parent: orm.Mapped[AdaptationSettings | None] = orm.relationship(
        foreign_keys=[parent_id], remote_side=lambda: [AdaptationSettings.id]
    )

    system_prompt: orm.Mapped[str]

    _response_specification: orm.Mapped[JsonDict] = orm.mapped_column("response_specification", sql.JSON)

    @property
    def response_specification(self) -> strategy.ConcreteLlmResponseSpecification:
        return strategy.validate(self._response_specification)

    @response_specification.setter
    def response_specification(self, value: strategy.ConcreteLlmResponseSpecification) -> None:
        self._response_specification = value.model_dump()


class Adaptation(OrmBase):
    __tablename__ = "adaptations"

    def __init__(
        self,
        *,
        created: AdaptationCreation,
        exercise: AdaptableExercise,
        model: llm.ConcreteModel,
        settings: AdaptationSettings,
        raw_llm_conversations: JsonList,
        initial_assistant_response: assistant_responses.Response | None,
        adjustments: list[assistant_responses.Adjustment],
        manual_edit: adapted.Exercise | None,
    ) -> None:
        super().__init__()
        self.created = created
        self.exercise = exercise
        self.model = model
        self.settings = settings
        self.raw_llm_conversations = raw_llm_conversations
        self.initial_assistant_response = initial_assistant_response
        self.adjustments = adjustments
        self.manual_edit = manual_edit

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created: orm.Mapped[AdaptationCreation] = orm.relationship(back_populates="exercise_adaptation")

    exercise_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptableExercise.id))
    exercise: orm.Mapped[AdaptableExercise] = orm.relationship(
        foreign_keys=[exercise_id], remote_side=lambda: [AdaptableExercise.id], back_populates="adaptations"
    )

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationSettings.id))
    settings: orm.Mapped[AdaptationSettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=lambda: [AdaptationSettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> llm.ConcreteModel:
        return llm.validate(self._model)

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)

    _initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("initial_assistant_response", sql.JSON)

    @property
    def initial_assistant_response(self) -> assistant_responses.Response | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return assistant_responses.validate(self._initial_assistant_response)

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: assistant_responses.Response | None) -> None:
        if value is None:
            self._initial_assistant_response = sql.null()
        else:
            self._initial_assistant_response = value.model_dump()

    _adjustments: orm.Mapped[JsonList] = orm.mapped_column("adjustments", sql.JSON)

    @property
    def adjustments(self) -> list[assistant_responses.Adjustment]:
        return [assistant_responses.Adjustment.model_validate(adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[assistant_responses.Adjustment]) -> None:
        self._adjustments = [adjustment.model_dump() for adjustment in value]

    _manual_edit: orm.Mapped[JsonDict | None] = orm.mapped_column("manual_edit", sql.JSON)

    @property
    def manual_edit(self) -> adapted.Exercise | None:
        if self._manual_edit is None:
            return None
        else:
            return adapted.Exercise.model_validate(self._manual_edit)

    @manual_edit.setter
    def manual_edit(self, value: adapted.Exercise | None) -> None:
        if value is None:
            self._manual_edit = sql.null()
        else:
            self._manual_edit = value.model_dump()


class AdaptationCreation(OrmBase):
    __tablename__ = "adaptation_creations"
    __mapper_args__ = {"polymorphic_on": "kind"}

    def __init__(self, *, at: datetime.datetime) -> None:
        super().__init__()
        self.at = at

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Adaptation.id), primary_key=True)
    kind: orm.Mapped[str]
    at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))

    exercise_adaptation: orm.Mapped[Adaptation] = orm.relationship(
        foreign_keys=[id], remote_side=[Adaptation.id], back_populates="created"
    )


# @todo Delete this class (after migration of data with Patty 2025-09-10)
class AdaptationCreationByUser_ToBeDeleted(AdaptationCreation):
    __tablename__ = "adaptation_creations__by_user"
    __mapper_args__ = {"polymorphic_identity": "by_user"}

    def __init__(self) -> None:
        assert False

    id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationCreation.id), primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column()


annotate_new_tables("adaptation")
