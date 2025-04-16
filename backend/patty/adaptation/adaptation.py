from sqlalchemy import orm
from typing import Any, Literal
import psycopg2.errors
import pydantic
import sqlalchemy as sql
import sqlalchemy.exc

from .. import llm
from ..adapted import Exercise
from ..any_json import JsonDict, JsonList
from ..api_utils import ApiModel
from ..database_utils import OrmBase, TestCaseWithDatabase
from .batch import Batch
from .input import Input
from .strategy import Strategy, JsonFromTextLlmResponseSpecification


class AssistantSuccess(ApiModel):
    kind: Literal["success"]
    exercise: Exercise


class AssistantInvalidJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["invalid-json"]
    parsed: Any


class AssistantNotJsonError(ApiModel):
    kind: Literal["error"]
    error: Literal["not-json"]
    text: str


AssistantResponse = AssistantSuccess | AssistantInvalidJsonError | AssistantNotJsonError


class Adjustment(ApiModel):
    user_prompt: str
    assistant_response: AssistantResponse


class Adaptation(OrmBase):
    __tablename__ = "adaptation_adaptations"

    __table_args__ = (
        sql.ForeignKeyConstraint(
            ["batch_id", "strategy_id"], ["adaptation_batches.id", "adaptation_batches.strategy_id"]
        ),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    created_by: orm.Mapped[str]

    batch_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Batch.id))
    batch: orm.Mapped[Batch] = orm.relationship(Batch, foreign_keys=[batch_id], back_populates="adaptations")

    strategy_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Strategy.id))
    strategy: orm.Mapped[Strategy] = orm.relationship(Strategy)

    input_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Input.id))
    input: orm.Mapped[Input] = orm.relationship(Input)

    # Kept only to help investigating future issues
    raw_llm_conversations: orm.Mapped[JsonList] = orm.mapped_column(sql.JSON)

    _initial_assistant_response: orm.Mapped[JsonDict | None] = orm.mapped_column("initial_assistant_response", sql.JSON)

    class _AssistantResponseContainer(pydantic.BaseModel):
        response: AssistantResponse

    @property
    def initial_assistant_response(self) -> AssistantResponse | None:
        if self._initial_assistant_response is None:
            return None
        else:
            return self._AssistantResponseContainer(response=self._initial_assistant_response).response  # type: ignore[arg-type]

    @initial_assistant_response.setter
    def initial_assistant_response(self, value: AssistantResponse | None) -> None:
        if value is None:
            self._initial_assistant_response = None
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
    def manual_edit(self) -> Exercise | None:
        if self._manual_edit is None:
            return None
        else:
            return Exercise(**self._manual_edit)

    @manual_edit.setter
    def manual_edit(self, value: Exercise | None) -> None:
        if value is None:
            self._manual_edit = None
        else:
            self._manual_edit = value.model_dump()


class AdaptationTestCase(TestCaseWithDatabase):
    def test_create(self) -> None:
        input = self.create_model(Input, created_by="UnitTests", text="Input text")

        strategy = self.create_model(
            Strategy,
            created_by="UnitTests",
            model=llm.DummyModel(name="dummy-1"),
            system_prompt="System prompt",
            response_specification=JsonFromTextLlmResponseSpecification(format="json", formalism="text"),
        )

        batch = self.create_model(Batch, created_by="UnitTests", strategy=strategy)

        self.create_model(
            Adaptation,
            created_by="UnitTests",
            batch=batch,
            strategy=strategy,
            input=input,
            raw_llm_conversations=[],
            initial_assistant_response=None,
            adjustments=[],
            manual_edit=None,
        )

    def test_create_with_inconsistent_strategy__with_orm(self) -> None:
        input = self.create_model(Input, created_by="UnitTests", text="Input text")

        strategy_1 = self.create_model(
            Strategy,
            created_by="UnitTests",
            model=llm.DummyModel(name="dummy-1"),
            system_prompt="System prompt 1",
            response_specification=JsonFromTextLlmResponseSpecification(format="json", formalism="text"),
        )

        strategy_2 = self.create_model(
            Strategy,
            created_by="UnitTests",
            model=llm.DummyModel(name="dummy-1"),
            system_prompt="System prompt 2",
            response_specification=JsonFromTextLlmResponseSpecification(format="json", formalism="text"),
        )

        batch = self.create_model(Batch, created_by="UnitTests", strategy=strategy_1)

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.create_model(
                Adaptation,
                created_by="UnitTests",
                batch=batch,
                strategy=strategy_2,  # Inconsistent strategy
                input=input,
                raw_llm_conversations=[],
                initial_assistant_response=None,
                adjustments=[],
                manual_edit=None,
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_adaptations_batch_id_strategy_id_adaptati_52e6"
        )

    def test_create_with_inconsistent_strategy__without_orm(self) -> None:
        input = self.create_model(Input, created_by="UnitTests", text="Input text")

        strategy_1 = self.create_model(
            Strategy,
            created_by="UnitTests",
            model=llm.DummyModel(name="dummy-1"),
            system_prompt="System prompt 1",
            response_specification=JsonFromTextLlmResponseSpecification(format="json", formalism="text"),
        )

        strategy_2 = self.create_model(
            Strategy,
            created_by="UnitTests",
            model=llm.DummyModel(name="dummy-1"),
            system_prompt="System prompt 2",
            response_specification=JsonFromTextLlmResponseSpecification(format="json", formalism="text"),
        )

        batch = self.create_model(Batch, created_by="UnitTests", strategy=strategy_1)

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.session.execute(
                sql.insert(Adaptation).values(
                    created_by="UnitTests",
                    batch_id=batch.id,
                    strategy_id=strategy_2.id,  # Inconsistent strategy
                    input_id=input.id,
                    raw_llm_conversations=[],
                    _initial_assistant_response=None,
                    _adjustments=[],
                    _manual_edit=None,
                )
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_adaptations_batch_id_strategy_id_adaptati_52e6"
        )
