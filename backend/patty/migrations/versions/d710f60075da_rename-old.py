from typing import Sequence, Union

from alembic import op

revision: str = "d710f60075da"
down_revision: Union[str, None] = "496af6d75cf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for name in [
        "textbooks",
        "page_extractions",
        "exercises",
        "extraction_strategies",
        "adaptation_strategies",
        "adaptable_exercises",
        "adaptation_batches",
        "pdf_file_ranges",
        "adaptations",
        "adaptation_strategy_settings",
        "pdf_files",
        "external_exercises",
        "extraction_batches",
        "exercise_classes",
        "classification_batches",
    ]:
        op.execute(f"ALTER TABLE {name} RENAME CONSTRAINT pk_{name} TO pk_old_{name};")
        op.rename_table(name, f"old_{name}")
        if name not in ["adaptable_exercises", "pdf_files", "external_exercises"]:
            op.execute(f"ALTER SEQUENCE {name}_id_seq RENAME TO old_{name}_id_seq")

    op.drop_constraint(
        op.f("fk_adaptable_exercises_exercise_class_id_exercise_classes"), "old_adaptable_exercises", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_adaptable_exercises_classified_by_classification_bat_228b"),
        "old_adaptable_exercises",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptable_exercises_created_by_page_extraction_id_pa_8c42"),
        "old_adaptable_exercises",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_batches_textbook_id_textbooks"), "old_adaptation_batches", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_adaptation_batches_strategy_id_adaptation_strategies"), "old_adaptation_batches", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategies_created_by_classification_batc_a26b"),
        "old_adaptation_strategies",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategies_settings_id_adaptation_strateg_7bff"),
        "old_adaptation_strategies",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategy_settings_parent_id_adaptation_st_cf34"),
        "old_adaptation_strategy_settings",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategy_settings_exercise_class_id_exerc_7f39"),
        "old_adaptation_strategy_settings",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptations_classification_batch_id_classification_batches"), "old_adaptations", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_adaptations_strategy_id_adaptation_strategies"), "old_adaptations", type_="foreignkey")
    op.drop_constraint(op.f("fk_adaptations_exercise_id_adaptable_exercises"), "old_adaptations", type_="foreignkey")
    op.drop_constraint(
        op.f("fk_adaptations_adaptation_batch_id_adaptation_batches"), "old_adaptations", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_classification_batches_created_by_page_extraction_id_728e"),
        "old_classification_batches",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_exercise_classes_created_by_classification_batch_id__2337"), "old_exercise_classes", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_exercise_classes_latest_strategy_settings_id_adaptat_9a1e"), "old_exercise_classes", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_exercises_textbook_id_textbooks"), "old_exercises", type_="foreignkey")
    op.drop_constraint(
        op.f("fk_extraction_batches_range_id_pdf_file_ranges"), "old_extraction_batches", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_extraction_batches_strategy_id_extraction_strategies"), "old_extraction_batches", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_page_extractions_extraction_batch_id_extraction_batches"), "old_page_extractions", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_pdf_file_ranges_pdf_file_sha256_pdf_files"), "old_pdf_file_ranges", type_="foreignkey")
