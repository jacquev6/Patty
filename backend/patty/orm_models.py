from __future__ import annotations

import datetime
import inspect
import typing

from sqlalchemy import orm
import sqlalchemy as sql
import pydantic

from .extraction import assistant_responses as extraction_responses
from .adaptation import adaptation as adaptation_responses
from .adaptation import llm as adaptation_llm
from .adaptation.strategy import ConcreteLlmResponseSpecification
from .adapted import Exercise as AdaptedExercise
from .any_json import JsonDict, JsonList
from .database_utils import OrmBase as OrmBaseBase
from .extraction import llm as extraction_llm


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
                    if caller_frame.filename.startswith("/app") and caller_frame.function != "make":
                        break
                print(
                    f"WARNING: on {caller_frame.filename}:{caller_frame.lineno}, field '{column.name}' of {cls.__name__} is not set",
                    flush=True,
                )
        super().__init__(**kwargs)


class Textbook(OrmBase):
    __tablename__ = "textbooks"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'Textbook's are created manually

    title: orm.Mapped[str]
    editor: orm.Mapped[str | None]  # @todo Rename to 'publisher'. Everywhere. Sic.
    year: orm.Mapped[int | None]
    isbn: orm.Mapped[str | None]

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
    created_by_username: orm.Mapped[str | None]  # Some 'AdaptableExercise's are created by a 'PageExtraction'

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


class PdfFile(OrmBase):
    __tablename__ = "pdf_files"

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'PdfFile's are created manually

    sha256: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    bytes_count: orm.Mapped[int]
    pages_count: orm.Mapped[int]
    known_file_names: orm.Mapped[list[str]] = orm.mapped_column(sql.JSON)


class PdfFileRange(OrmBase):
    __tablename__ = "pdf_file_ranges"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'PdfFileRange's are created manually

    pdf_file_sha256: orm.Mapped[str] = orm.mapped_column(sql.ForeignKey(PdfFile.sha256))
    pdf_file: orm.Mapped[PdfFile] = orm.relationship(foreign_keys=[pdf_file_sha256], remote_side=[PdfFile.sha256])
    pdf_file_first_page_number: orm.Mapped[int]
    pages_count: orm.Mapped[int]


class ExtractionStrategy(OrmBase):
    __tablename__ = "extraction_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'ExtractionStrategy's are created manually

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> extraction_llm.ConcreteModel:
        return pydantic.RootModel[extraction_llm.ConcreteModel](self._model).root  # type: ignore[arg-type]

    @model.setter
    def model(self, value: extraction_llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    prompt: orm.Mapped[str]


class ExtractionBatch(OrmBase):
    __tablename__ = "extraction_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'ExtractionBatch's are created manually

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionStrategy.id))
    strategy: orm.Mapped[ExtractionStrategy] = orm.relationship(
        foreign_keys=[strategy_id], remote_side=[ExtractionStrategy.id]
    )

    range_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(PdfFileRange.id))
    range: orm.Mapped[PdfFileRange] = orm.relationship(foreign_keys=[range_id], remote_side=[PdfFileRange.id])

    page_extractions: orm.Mapped[list[PageExtraction]] = orm.relationship(
        back_populates="extraction_batch", order_by=lambda: [PageExtraction.page_number]
    )

    run_classification: orm.Mapped[bool]

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
        if value is None:
            self._model_for_adaptation = sql.null()
        else:
            self._model_for_adaptation = value.model_dump()


class PageExtraction(OrmBase):
    __tablename__ = "page_extractions"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'PageExtraction's are created manually

    extraction_batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(ExtractionBatch.id))
    extraction_batch: orm.Mapped[ExtractionBatch] = orm.relationship(
        foreign_keys=[extraction_batch_id], remote_side=[ExtractionBatch.id], back_populates="page_extractions"
    )

    page_number: orm.Mapped[int]

    _assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("assistant_response", sql.JSON)

    @property
    def assistant_response(self) -> extraction_responses.AssistantResponse | None:
        if self._assistant_response is None:
            return None
        else:
            return pydantic.RootModel[extraction_responses.AssistantResponse](self._assistant_response).root  # type: ignore[arg-type]

    @assistant_response.setter
    def assistant_response(self, value: extraction_responses.AssistantResponse | None) -> None:
        if value is None:
            self._assistant_response = sql.null()
        else:
            self._assistant_response = value.model_dump()

    exercises: orm.Mapped[list[AdaptableExercise]] = orm.relationship(
        back_populates="created_by_page_extraction", order_by=[BaseExercise.page_number, BaseExercise.exercise_number]
    )


class ClassificationBatch(OrmBase):
    __tablename__ = "classification_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]  # Some 'ClassificationBatch's are created by a 'PageExtraction'
    created_by_page_extraction_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    created_by_page_extraction: orm.Mapped[PageExtraction | None] = orm.relationship(
        foreign_keys=[created_by_page_extraction_id], remote_side=[PageExtraction.id]
    )

    exercises: orm.Mapped[list[AdaptableExercise]] = orm.relationship(
        back_populates="classified_by_classification_batch", order_by=lambda: [AdaptableExercise.id]
    )

    _model_for_adaptation: orm.Mapped[JsonDict | None] = orm.mapped_column("model_for_adaptation", sql.JSON)

    @property
    def model_for_adaptation(self) -> adaptation_llm.ConcreteModel | None:
        if self._model_for_adaptation is None:
            return None
        else:
            return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model_for_adaptation).root  # type: ignore[arg-type]

    @model_for_adaptation.setter
    def model_for_adaptation(self, value: adaptation_llm.ConcreteModel | None) -> None:
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
    created_by_username: orm.Mapped[str | None]  # Some 'ExerciseClass's are created by a 'ClassificationBatch'
    created_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    created_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[created_by_classification_batch_id], remote_side=[ClassificationBatch.id]
    )

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

    created_by_page_extraction_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(PageExtraction.id))
    created_by_page_extraction: orm.Mapped[PageExtraction | None] = orm.relationship(
        foreign_keys=[created_by_page_extraction_id], remote_side=[PageExtraction.id], back_populates="exercises"
    )

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
    created_by_username: orm.Mapped[str]  # All 'AdaptationStrategySettings's are created manually

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
    created_by_username: orm.Mapped[str | None]  # Some 'AdaptationStrategy's are created by a 'ClassificationBatch'
    created_by_classification_batch_id: orm.Mapped[int | None] = orm.mapped_column(
        sql.ForeignKey(ClassificationBatch.id)
    )
    created_by_classification_batch: orm.Mapped[ClassificationBatch | None] = orm.relationship(
        foreign_keys=[created_by_classification_batch_id], remote_side=[ClassificationBatch.id]
    )

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(AdaptationStrategySettings.id))
    settings: orm.Mapped[AdaptationStrategySettings] = orm.relationship(
        foreign_keys=[settings_id], remote_side=[AdaptationStrategySettings.id]
    )

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    @property
    def model(self) -> adaptation_llm.ConcreteModel:
        return pydantic.RootModel[adaptation_llm.ConcreteModel](self._model).root  # type: ignore[arg-type]

    @model.setter
    def model(self, value: adaptation_llm.ConcreteModel) -> None:
        self._model = value.model_dump()


class AdaptationBatch(OrmBase):
    __tablename__ = "adaptation_batches"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str]  # All 'AdaptationBatch's are created manually

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
    created_by_username: orm.Mapped[str | None]  # Some 'Adaptation's are created by a 'ClassificationBatch'

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
    def initial_assistant_response(self) -> adaptation_responses.AssistantResponse | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return pydantic.RootModel[adaptation_responses.AssistantResponse](self._initial_assistant_response).root  # type: ignore[arg-type]

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: adaptation_responses.AssistantResponse | None) -> None:
        if value is None:
            self._initial_assistant_response = sql.null()
        else:
            self._initial_assistant_response = value.model_dump()

    _adjustments: orm.Mapped[JsonList] = orm.mapped_column("adjustments", sql.JSON)

    @property
    def adjustments(self) -> list[adaptation_responses.Adjustment]:
        return [adaptation_responses.Adjustment(**adjustment) for adjustment in self._adjustments]

    @adjustments.setter
    def adjustments(self, value: list[adaptation_responses.Adjustment]) -> None:
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


class ErrorCaughtByFrontend(OrmBase):
    __tablename__ = "errors_caught_by_frontend"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sql.DateTime(timezone=True))
    created_by_username: orm.Mapped[str | None]

    patty_version: orm.Mapped[str]
    user_agent: orm.Mapped[str]
    window_size: orm.Mapped[str]
    url: orm.Mapped[str]

    caught_by: orm.Mapped[str]
    message: orm.Mapped[str]
    code_location: orm.Mapped[str | None]


all_models: list[type[OrmBase]] = [
    AdaptableExercise,
    Adaptation,
    AdaptationBatch,
    AdaptationStrategy,
    AdaptationStrategySettings,
    BaseExercise,
    ClassificationBatch,
    ErrorCaughtByFrontend,
    ExerciseClass,
    ExternalExercise,
    ExtractionBatch,
    ExtractionStrategy,
    PageExtraction,
    PdfFile,
    PdfFileRange,
    Textbook,
]
