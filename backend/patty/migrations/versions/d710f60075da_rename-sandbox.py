from typing import Sequence, Union

from alembic import op

revision: str = "d710f60075da"
down_revision: Union[str, None] = "496af6d75cf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("textbooks", "editor", new_column_name="publisher")
    op.rename_table("adaptation_batches", "sandbox_adaptation_batches")
    op.rename_table("classification_batches", "sandbox_classification_batches")
    op.rename_table("extraction_batches", "sandbox_extraction_batches")
    op.drop_constraint(
        op.f("fk_adaptable_exercises_classified_by_classification_bat_228b"), "adaptable_exercises", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_adaptable_exercises_classified_by_classification_batch_id_sandbox_classification_batches"),
        "adaptable_exercises",
        "sandbox_classification_batches",
        ["classified_by_classification_batch_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategies_created_by_classification_batc_a26b"),
        "adaptation_strategies",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_adaptation_strategies_created_by_classification_batch_id_sandbox_classification_batches"),
        "adaptation_strategies",
        "sandbox_classification_batches",
        ["created_by_classification_batch_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_adaptations_classification_batch_id_classification_batches"), "adaptations", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_adaptations_adaptation_batch_id_adaptation_batches"), "adaptations", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_adaptations_classification_batch_id_sandbox_classification_batches"),
        "adaptations",
        "sandbox_classification_batches",
        ["classification_batch_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_adaptations_adaptation_batch_id_sandbox_adaptation_batches"),
        "adaptations",
        "sandbox_adaptation_batches",
        ["adaptation_batch_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_exercise_classes_created_by_classification_batch_id__2337"), "exercise_classes", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_exercise_classes_created_by_classification_batch_id_sandbox_classification_batches"),
        "exercise_classes",
        "sandbox_classification_batches",
        ["created_by_classification_batch_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_page_extractions_extraction_batch_id_extraction_batches"), "page_extractions", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_page_extractions_extraction_batch_id_sandbox_extraction_batches"),
        "page_extractions",
        "sandbox_extraction_batches",
        ["extraction_batch_id"],
        ["id"],
    )
    op.execute("ALTER SEQUENCE adaptation_batches_id_seq RENAME TO sandbox_adaptation_batches_id_seq")
    op.execute("ALTER SEQUENCE classification_batches_id_seq RENAME TO sandbox_classification_batches_id_seq")
    op.execute("ALTER SEQUENCE extraction_batches_id_seq RENAME TO sandbox_extraction_batches_id_seq")
