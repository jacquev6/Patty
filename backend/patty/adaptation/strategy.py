from __future__ import annotations
from typing import Literal

from sqlalchemy import orm
import psycopg2.errors
import pydantic
import sqlalchemy as sql
import sqlalchemy.exc

from .. import adapted
from .. import llm
from ..any_json import JsonDict
from ..api_utils import ApiModel
from ..database_utils import OrmBase, TestCaseWithDatabase


class JsonLlmResponseSpecification(ApiModel):
    format: Literal["json"]


class JsonFromTextLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["text"]

    def make_response_format(self) -> llm.JsonFromTextResponseFormat[adapted.Exercise]:
        return llm.JsonFromTextResponseFormat(response_type=adapted.Exercise)


class JsonObjectLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["json-object"]

    def make_response_format(self) -> llm.JsonObjectResponseFormat[adapted.Exercise]:
        return llm.JsonObjectResponseFormat(response_type=adapted.Exercise)


class JsonSchemaLlmResponseSpecification(JsonLlmResponseSpecification):
    formalism: Literal["json-schema"]
    instruction_components: adapted.InstructionComponents
    example_components: adapted.ExampleComponents
    hint_components: adapted.HintComponents
    statement_components: adapted.StatementComponents
    reference_components: adapted.ReferenceComponents

    def make_response_format(self) -> llm.JsonSchemaResponseFormat[adapted.Exercise]:
        return llm.JsonSchemaResponseFormat(response_type=self.make_response_type())

    def make_response_type(self) -> type[adapted.Exercise]:
        return adapted.make_exercise_type(
            self.instruction_components,
            self.example_components,
            self.hint_components,
            self.statement_components,
            self.reference_components,
        )

    def make_response_schema(self) -> JsonDict:
        return llm.make_schema(self.make_response_type())


ConcreteLlmResponseSpecification = (
    JsonFromTextLlmResponseSpecification | JsonObjectLlmResponseSpecification | JsonSchemaLlmResponseSpecification
)


class StrategySettingsBranch(OrmBase):
    __tablename__ = "adaptation_strategy_settings_branches"

    __table_args__ = (
        sql.CheckConstraint("name != ''", name="name_not_empty"),
        # Ensure self.head.branch == self
        sql.ForeignKeyConstraint(
            ["head_id", "id"],
            ["adaptation_strategy_settings.id", "adaptation_strategy_settings.branch_id"],
            use_alter=True,
        ),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    # Head is temporarily None on creation, before the first settings are created.
    head_id: orm.Mapped[int | None] = orm.mapped_column()
    head: orm.Mapped[StrategySettings | None] = orm.relationship(
        "StrategySettings",
        foreign_keys=[head_id, id],
        remote_side=lambda: [StrategySettings.id, StrategySettings.branch_id],
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True)


class StrategySettings(OrmBase):
    __tablename__ = "adaptation_strategy_settings"

    __table_args__ = (
        # Redondant ('id' is unique by itself), but required for the foreign key in 'StrategySettingsBranch'
        sql.UniqueConstraint("id", "branch_id"),
        # Ensure self.parent.branch == self.branch
        sql.ForeignKeyConstraint(
            ["parent_id", "branch_id"], ["adaptation_strategy_settings.id", "adaptation_strategy_settings.branch_id"]
        ),
        # Ensure having a parent requires having a branch
        sql.CheckConstraint("parent_id IS NULL OR branch_id IS NOT NULL", name="branch_required_if_parent"),
    )

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    branch_id: orm.Mapped[int | None] = orm.mapped_column(sql.ForeignKey(StrategySettingsBranch.id))
    branch: orm.Mapped[StrategySettingsBranch | None] = orm.relationship(
        StrategySettingsBranch, foreign_keys=[branch_id], remote_side=[StrategySettingsBranch.id]
    )

    parent_id: orm.Mapped[int | None] = orm.mapped_column()
    parent: orm.Mapped[StrategySettings | None] = orm.relationship(
        "StrategySettings", foreign_keys=[parent_id], remote_side=[id]
    )

    created_by: orm.Mapped[str]

    system_prompt: orm.Mapped[str]

    _response_specification: orm.Mapped[JsonDict] = orm.mapped_column("response_specification", sql.JSON)

    class _LlmResponseSpecificationContainer(pydantic.BaseModel):
        specification: ConcreteLlmResponseSpecification

    @property
    def response_specification(self) -> ConcreteLlmResponseSpecification:
        return self._LlmResponseSpecificationContainer(specification=self._response_specification).specification  # type: ignore[arg-type]

    @response_specification.setter
    def response_specification(self, value: ConcreteLlmResponseSpecification) -> None:
        self._response_specification = value.model_dump()


class Strategy(OrmBase):
    __tablename__ = "adaptation_strategies"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]

    _model: orm.Mapped[JsonDict] = orm.mapped_column("model", sql.JSON)

    class _ModelContainer(pydantic.BaseModel):
        model: llm.ConcreteModel

    @property
    def model(self) -> llm.ConcreteModel:
        return self._ModelContainer(model=self._model).model  # type: ignore[arg-type]

    @model.setter
    def model(self, value: llm.ConcreteModel) -> None:
        self._model = value.model_dump()

    settings_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(StrategySettings.id))
    settings: orm.Mapped[StrategySettings] = orm.relationship(
        StrategySettings, foreign_keys=[settings_id], remote_side=[StrategySettings.id]
    )


class StrategyTestCase(TestCaseWithDatabase):
    response_specification = JsonFromTextLlmResponseSpecification(format="json", formalism="text")

    def test_create_two_branches_with_same_name(self) -> None:
        self.flush_model(StrategySettingsBranch, name="branch")
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(StrategySettingsBranch, name="branch")

        assert isinstance(cm.exception.orig, psycopg2.errors.UniqueViolation)
        self.assertEqual(str(cm.exception.orig.diag.constraint_name), "uq_adaptation_strategy_settings_branches_name")

    def test_create_branch_with_bad_head(self) -> None:
        # This test is required because we're using a foreign key with use_alter=True (to break a cycle)
        # and 'alembic version --autogenerate' doesn't create the foreign key in that case.
        # (See https://github.com/sqlalchemy/alembic/issues/326)
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(StrategySettingsBranch, name="branch", head_id=42)

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_strategy_settings_branches_head_id_id_ada_7eb5"
        )

    def test_create_branch_with_empty_name(self) -> None:
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(StrategySettingsBranch, name="")

        assert isinstance(cm.exception.orig, psycopg2.errors.CheckViolation)
        self.assertEqual(
            str(cm.exception.orig.diag.constraint_name), "ck_adaptation_strategy_settings_branches_name_not_empty"
        )

    def test_create_branch_with_head_belonging_to_other_branch__with_orm(self) -> None:
        head = self.flush_model(
            StrategySettings,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(StrategySettingsBranch, name="branch", head=head)

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_strategy_settings_branches_head_id_id_ada_7eb5"
        )

    def test_create_branch_with_head_belonging_to_other_branch__without_orm(self) -> None:
        head = self.flush_model(
            StrategySettings,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.session.execute(sql.insert(StrategySettingsBranch).values(name="branch", head_id=head.id))

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_strategy_settings_branches_head_id_id_ada_7eb5"
        )

    def test_create_branch_history(self) -> None:
        branch = self.flush_model(StrategySettingsBranch, name="branch")
        settings_1 = self.flush_model(
            StrategySettings,
            branch=branch,
            created_by="test",
            system_prompt="prompt a",
            response_specification=self.response_specification,
        )
        settings_2 = self.flush_model(
            StrategySettings,
            branch=branch,
            parent=settings_1,
            created_by="test",
            system_prompt="prompt b",
            response_specification=self.response_specification,
        )
        settings_3 = self.flush_model(
            StrategySettings,
            branch=branch,
            parent=settings_2,
            created_by="test",
            system_prompt="prompt c",
            response_specification=self.response_specification,
        )
        branch.head = settings_3
        self.session.flush()
        assert branch.head is not None
        assert branch.head.parent is not None
        assert branch.head.parent.parent is not None
        self.assertEqual(branch.head.parent.parent.system_prompt, "prompt a")

    def test_create_child_settings_with_inconsistent_branch__with_orm(self) -> None:
        branch_1 = self.flush_model(StrategySettingsBranch, name="branch_1")
        branch_2 = self.flush_model(StrategySettingsBranch, name="branch_2")
        parent = self.flush_model(
            StrategySettings,
            branch=branch_1,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(
                StrategySettings,
                branch=branch_2,
                parent=parent,
                created_by="test",
                system_prompt="prompt",
                response_specification=self.response_specification,
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_strategy_settings_parent_id_branch_id_ada_901a"
        )

    def test_create_child_settings_with_inconsistent_branch__without_orm(self) -> None:
        branch_1 = self.flush_model(StrategySettingsBranch, name="branch_1")
        branch_2 = self.flush_model(StrategySettingsBranch, name="branch_2")
        parent = self.flush_model(
            StrategySettings,
            branch=branch_1,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )

        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.session.execute(
                sql.insert(StrategySettings).values(
                    branch_id=branch_2.id,
                    parent_id=parent.id,
                    created_by="test",
                    system_prompt="prompt",
                    _response_specification=self.response_specification.model_dump(),
                )
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.ForeignKeyViolation)
        self.assertEqual(
            cm.exception.orig.diag.constraint_name, "fk_adaptation_strategy_settings_parent_id_branch_id_ada_901a"
        )

    def test_create_settings_with_parent_but_without_branch__with_orm(self) -> None:
        parent = self.flush_model(
            StrategySettings,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(
                StrategySettings,
                branch=None,
                parent=parent,
                created_by="test",
                system_prompt="prompt",
                response_specification=self.response_specification,
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.CheckViolation)
        self.assertEqual(
            str(cm.exception.orig.diag.constraint_name), "ck_adaptation_strategy_settings_branch_required_if_parent"
        )

    def test_create_settings_with_parent_but_without_branch__without_orm(self) -> None:
        parent = self.flush_model(
            StrategySettings,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.session.execute(
                sql.insert(StrategySettings).values(
                    branch_id=None,
                    parent_id=parent.id,
                    created_by="test",
                    system_prompt="prompt",
                    _response_specification=self.response_specification.model_dump(),
                )
            )

        assert isinstance(cm.exception.orig, psycopg2.errors.CheckViolation)
        self.assertEqual(
            str(cm.exception.orig.diag.constraint_name), "ck_adaptation_strategy_settings_branch_required_if_parent"
        )

    def test_create_settings_without_branch(self) -> None:
        settings = self.flush_model(
            StrategySettings,
            branch=None,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )
        self.assertIsNone(settings.branch)

    def test_create_settings_with_branch(self) -> None:
        branch = self.flush_model(StrategySettingsBranch, name="branch")
        settings = self.flush_model(
            StrategySettings,
            branch=branch,
            created_by="test",
            system_prompt="prompt",
            response_specification=self.response_specification,
        )
        branch.head = settings
        self.session.flush()
        self.assertEqual(settings.branch_id, branch.id)
        self.assertEqual(branch.head_id, settings.id)
