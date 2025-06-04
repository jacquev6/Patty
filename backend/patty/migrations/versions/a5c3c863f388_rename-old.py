from typing import Sequence, Union

from alembic import op


revision: str = "a5c3c863f388"
down_revision: Union[str, None] = "c58370feed85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("fk_adaptation_adaptations_batch_id_strategy_id_adaptati_52e6"),
        "adaptation_adaptations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategy_settings_parent_id_branch_id_ada_901a"),
        "adaptation_strategy_settings",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_adaptation_strategy_settings_branches_head_id_id_ada_7eb5"),
        "adaptation_strategy_settings_branches",
        type_="foreignkey",
    )
    op.drop_constraint(op.f("uq_adaptation_batches_id_strategy_id"), "adaptation_batches", type_="unique")
    op.drop_constraint(
        op.f("uq_adaptation_strategy_settings_id_branch_id"), "adaptation_strategy_settings", type_="unique"
    )
    op.drop_constraint(
        op.f("uq_adaptation_strategy_settings_branches_name"), "adaptation_strategy_settings_branches", type_="unique"
    )
    op.drop_constraint(
        op.f("ck_adaptation_strategy_settings_branches_name_not_empty"),
        "adaptation_strategy_settings_branches",
        type_="check",
    )
    op.drop_constraint(op.f("ck_adaptation_textbooks_title_not_empty"), "adaptation_textbooks", type_="check")
    op.drop_constraint(
        op.f("ck_adaptation_strategy_settings_branch_required_if_parent"), "adaptation_strategy_settings", type_="check"
    )
    op.drop_constraint(op.f("ck_adaptation_input_exercise_number_not_empty"), "adaptation_input", type_="check")

    for name in [
        "adaptation_adaptations",
        "adaptation_batches",
        "adaptation_input",
        "adaptation_strategy_settings_branches",
        "adaptation_strategy_settings",
        "adaptation_strategies",
        "adaptation_textbooks",
        "adaptation_external_exercises",
    ]:
        op.execute(f"ALTER TABLE {name} RENAME CONSTRAINT pk_{name} TO pk_old_{name};")
        op.rename_table(name, f"old_{name}")
        op.execute(f"ALTER SEQUENCE {name}_id_seq RENAME TO old_{name}_id_seq")

    op.create_unique_constraint(
        op.f("uq_old_adaptation_batches_id_strategy_id"), "old_adaptation_batches", ["id", "strategy_id"]
    )
    op.create_unique_constraint(
        op.f("uq_old_adaptation_strategy_settings_id_branch_id"),
        "old_adaptation_strategy_settings",
        ["id", "branch_id"],
    )
    op.create_unique_constraint(
        op.f("uq_old_adaptation_strategy_settings_branches_name"), "old_adaptation_strategy_settings_branches", ["name"]
    )
    op.create_foreign_key(
        op.f("fk_old_adaptation_adaptations_batch_id_strategy_id_old_adaptation_batches"),
        "old_adaptation_adaptations",
        "old_adaptation_batches",
        ["batch_id", "strategy_id"],
        ["id", "strategy_id"],
    )
    op.create_foreign_key(
        op.f("fk_old_adaptation_strategy_settings_parent_id_branch_id_old_adaptation_strategy_settings"),
        "old_adaptation_strategy_settings",
        "old_adaptation_strategy_settings",
        ["parent_id", "branch_id"],
        ["id", "branch_id"],
    )
    op.create_foreign_key(
        op.f("fk_old_adaptation_strategy_settings_branches_head_id_id_old_adaptation_strategy_settings"),
        "old_adaptation_strategy_settings_branches",
        "old_adaptation_strategy_settings",
        ["head_id", "id"],
        ["id", "branch_id"],
        use_alter=True,
    )
    op.create_check_constraint(
        op.f("ck_old_adaptation_strategy_settings_branch_required_if_parent"),
        "old_adaptation_strategy_settings",
        "parent_id IS NULL OR branch_id IS NOT NULL",
    )
    op.create_check_constraint(
        op.f("ck_old_adaptation_strategy_settings_branches_name_not_empty"),
        "old_adaptation_strategy_settings_branches",
        "name != ''",
    )
    op.create_check_constraint(
        op.f("ck_old_adaptation_textbooks_title_not_empty"), "old_adaptation_textbooks", "title != ''"
    )
    op.create_check_constraint(
        op.f("ck_old_adaptation_input_exercise_number_not_empty"), "old_adaptation_input", "exercise_number != ''"
    )
