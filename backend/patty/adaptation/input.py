from sqlalchemy import orm
import psycopg2.errors
import sqlalchemy as sql
import sqlalchemy.exc

from ..database_utils import OrmBase, TestCaseWithDatabase


class OldInput(OrmBase):
    __tablename__ = "old_adaptation_input"

    __table_args__ = (sql.CheckConstraint("exercise_number != ''", name="exercise_number_not_empty"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)

    created_by: orm.Mapped[str]

    page_number: orm.Mapped[int | None]
    # Custom collation: ../migrations/versions/429d2fb463dd_exercise_number_collation.py
    exercise_number: orm.Mapped[str | None] = orm.mapped_column(sql.String(collation="exercise_number"))

    text: orm.Mapped[str]


class InputTestCase(TestCaseWithDatabase):
    def test_create_with_empty_exercise_number(self) -> None:
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            self.flush_model(OldInput, created_by="test", page_number=1, exercise_number="", text="test")
        assert isinstance(cm.exception.orig, psycopg2.errors.CheckViolation)
        self.assertEqual(cm.exception.orig.diag.constraint_name, "ck_old_adaptation_input_exercise_number_not_empty")
