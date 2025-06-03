import copy
import datetime
import typing

from . import database_utils
from . import orm_models


def migrate(session: database_utils.Session) -> None:
    data_before = database_utils.dump(session)

    for table_name, rows in sorted(data_before.items()):
        print(f"{table_name}: {len(rows)} rows")

    data_after = migrate_data(data_before, datetime.datetime.now(datetime.timezone.utc).isoformat())

    print("-->")
    for table_name, rows in sorted(data_after.items()):
        print(f"{table_name}: {len(rows)} rows")

    database_utils.load(
        session,
        data_after,
        {"old_adaptation_strategy_settings_branches": ["head_id"], "exercise_classes": ["latest_strategy_settings_id"]},
    )

    session.flush()

    check_parsed_fields(session)


def migrate_data(
    data_before: dict[str, list[dict[str, typing.Any]]], migration_date: str
) -> dict[str, list[dict[str, typing.Any]]]:
    for key in [
        "adaptable_exercises",
        "adaptation_batches",
        "adaptation_strategies",
        "adaptation_strategy_settings",
        "adaptations",
        "classification_strategies",
        "classification_batches",
        "exercise_classes",
        "exercises",
        "external_exercises",
        "extraction_strategies",
        "extractions",
        "pdf_files",
        "textbook_ranges",
        "textbooks",
    ]:
        assert len(data_before[key]) == 0, key
        del data_before[key]

    data_after: dict[str, list[dict[str, typing.Any]]] = {}

    old_adaptation_input = data_before.pop("old_adaptation_input")
    old_adaptation_strategy_settings_branches = data_before.pop("old_adaptation_strategy_settings_branches")
    old_adaptation_textbooks = data_before.pop("old_adaptation_textbooks")
    old_adaptation_external_exercises = data_before.pop("old_adaptation_external_exercises")
    old_adaptation_strategy_settings = data_before.pop("old_adaptation_strategy_settings")
    old_adaptation_strategies = data_before.pop("old_adaptation_strategies")
    old_adaptation_batches = data_before.pop("old_adaptation_batches")
    old_adaptation_adaptations = data_before.pop("old_adaptation_adaptations")
    assert len(data_before) == 0, data_before.keys()

    assert len(old_adaptation_external_exercises) == 0

    data_after["exercise_classes"] = []
    for old_branch in old_adaptation_strategy_settings_branches:
        old_branch = copy.deepcopy(old_branch)
        id = old_branch.pop("id")
        head_id = old_branch.pop("head_id")
        name = old_branch.pop("name")
        assert len(old_branch) == 0
        data_after["exercise_classes"].append(
            {
                "id": id,
                "name": name,
                "created_at": migration_date,
                "created_by_username": "Migration",
                "latest_strategy_settings_id": head_id,
            }
        )

    data_after["adaptation_strategy_settings"] = []
    for old_settings in old_adaptation_strategy_settings:
        old_settings = copy.deepcopy(old_settings)
        id = old_settings.pop("id")
        exercise_class_id = old_settings.pop("branch_id")
        parent_id = old_settings.pop("parent_id")
        created_by = old_settings.pop("created_by")
        system_prompt = old_settings.pop("system_prompt")
        response_specification = old_settings.pop("response_specification")
        assert len(old_settings) == 0
        data_after["adaptation_strategy_settings"].append(
            {
                "id": id,
                "created_at": migration_date,
                "created_by_username": created_by,
                "exercise_class_id": exercise_class_id,
                "parent_id": parent_id,
                "system_prompt": system_prompt,
                "response_specification": response_specification,
            }
        )

    data_after["textbooks"] = []
    for old_textbook in old_adaptation_textbooks:
        old_textbook = copy.deepcopy(old_textbook)
        id = old_textbook.pop("id")
        created_by = old_textbook.pop("created_by")
        created_at = old_textbook.pop("created_at")
        title = old_textbook.pop("title", None)
        assert len(old_textbook) == 0
        data_after["textbooks"].append(
            {"id": id, "created_at": created_at, "created_by_username": created_by, "title": title}
        )

    data_after["adaptation_strategies"] = []
    for old_strategy in old_adaptation_strategies:
        old_strategy = copy.deepcopy(old_strategy)
        id = old_strategy.pop("id")
        created_by = old_strategy.pop("created_by")
        model = old_strategy.pop("model")
        settings_id = old_strategy.pop("settings_id")
        assert len(old_strategy) == 0
        data_after["adaptation_strategies"].append(
            {
                "id": id,
                "created_at": migration_date,
                "created_by_username": created_by,
                "model": model,
                "settings_id": settings_id,
            }
        )

    data_after["adaptation_batches"] = []
    for old_batch in old_adaptation_batches:
        old_batch = copy.deepcopy(old_batch)
        id = old_batch.pop("id")
        created_by = old_batch.pop("created_by")
        created_at = old_batch.pop("created_at")
        strategy_id = old_batch.pop("strategy_id")
        textbook_id = old_batch.pop("textbook_id")
        removed_from_textbook = old_batch.pop("removed_from_textbook")
        assert len(old_batch) == 0
        data_after["adaptation_batches"].append(
            {
                "id": id,
                "created_at": created_at,
                "created_by_username": created_by,
                "strategy_id": strategy_id,
                "textbook_id": textbook_id,
                "removed_from_textbook": removed_from_textbook,
            }
        )

    data_after["exercises"] = []
    data_after["adaptable_exercises"] = []
    data_after["adaptations"] = []
    for old_adaptation in sorted(old_adaptation_adaptations, key=lambda x: x["id"]):
        old_adaptation = copy.deepcopy(old_adaptation)
        adaptation_id = old_adaptation.pop("id")
        adaptation_created_by = old_adaptation.pop("created_by")
        adaptation_batch_id = old_adaptation.pop("batch_id")
        adaptation_removed_from_textbook = old_adaptation.pop("removed_from_textbook")
        adaptation_strategy_id = old_adaptation.pop("strategy_id")
        adaptation_input_id = old_adaptation.pop("input_id")
        adaptation_raw_llm_conversations = old_adaptation.pop("raw_llm_conversations")
        adaptation_initial_assistant_response = old_adaptation.pop("initial_assistant_response")
        adaptation_adjustments = old_adaptation.pop("adjustments")
        adaptation_manual_edit = old_adaptation.pop("manual_edit")
        assert len(old_adaptation) == 0, old_adaptation

        old_input = get_one_by(old_adaptation_input, id=adaptation_input_id)
        old_input = copy.deepcopy(old_input)
        assert old_input.pop("id") == adaptation_input_id
        input_created_by = old_input.pop("created_by")
        input_page_number = old_input.pop("page_number")
        input_exercise_number = old_input.pop("exercise_number")
        input_text = old_input.pop("text")
        assert len(old_input) == 0

        if adaptation_batch_id is None:
            textbook_id = None
        else:
            old_batch = get_one_by(old_adaptation_batches, id=adaptation_batch_id)
            textbook_id = old_batch["textbook_id"]

        strategy = get_one_by(old_adaptation_strategies, id=adaptation_strategy_id)
        strategy_settings = get_one_by(old_adaptation_strategy_settings, id=strategy["settings_id"])
        exercise_class_id = strategy_settings["branch_id"]

        data_after["adaptations"].append(
            {
                "id": adaptation_id,
                "created_at": migration_date,
                "created_by_username": adaptation_created_by,
                "exercise_id": adaptation_id,
                "strategy_id": adaptation_strategy_id,
                "adaptation_batch_id": adaptation_batch_id,
                "raw_llm_conversations": adaptation_raw_llm_conversations,
                "initial_assistant_response": adaptation_initial_assistant_response,
                "adjustments": adaptation_adjustments,
                "manual_edit": adaptation_manual_edit,
            }
        )
        data_after["exercises"].append(
            {
                "id": adaptation_id,
                "kind": "adaptable",
                "created_at": migration_date,
                "created_by_username": input_created_by,
                "textbook_id": textbook_id,
                "removed_from_textbook": adaptation_removed_from_textbook,
                "page_number": input_page_number,
                "exercise_number": input_exercise_number,
            }
        )
        data_after["adaptable_exercises"].append(
            {
                "id": adaptation_id,
                "created_by_extraction_id": None,
                "full_text": input_text,
                "classified_at": None if exercise_class_id is None else migration_date,
                "classified_by_classification_batch_id": None,
                "classified_by_username": None if exercise_class_id is None else adaptation_created_by,
                "exercise_class_id": exercise_class_id,
            }
        )

    return data_after


def get_some_by(data: list[dict[str, typing.Any]], **kwargs: typing.Any) -> list[dict[str, typing.Any]]:
    items = []
    for item in data:
        if all(item[key] == value for key, value in kwargs.items()):
            items.append(item)
    return items


def get_one_by(data: list[dict[str, typing.Any]], **kwargs: typing.Any) -> dict[str, typing.Any]:
    items = list(get_some_by(data, **kwargs))
    assert len(items) == 1
    return items[0]


def check_parsed_fields(session: database_utils.Session) -> None:
    for adaptation in session.query(orm_models.Adaptation).all():
        adaptation.created_at
        adaptation.raw_llm_conversations
        adaptation.initial_assistant_response
        adaptation.adjustments
        adaptation.manual_edit
    for adapted_exercise in session.query(orm_models.AdaptableExercise).all():
        adapted_exercise.created_at
        adapted_exercise.classified_at
    for external_exercise in session.query(orm_models.ExternalExercise).all():
        external_exercise.created_at
    for exercise_class in session.query(orm_models.ExerciseClass).all():
        exercise_class.created_at
    for strategy_settings in session.query(orm_models.AdaptationStrategySettings).all():
        strategy_settings.created_at
        strategy_settings.response_specification
    for adaptation_batch in session.query(orm_models.AdaptationBatch).all():
        adaptation_batch.created_at
    for strategy in session.query(orm_models.AdaptationStrategy).all():
        strategy.created_at
    for textbook in session.query(orm_models.Textbook).all():
        textbook.created_at
