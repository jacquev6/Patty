import datetime
import os
import typing

from sqlalchemy import orm
import datasets  # type: ignore[import-untyped]
import numpy as np
import pandas as pd
import sqlalchemy as sql
import torch
import torch.utils.data
import transformers  # type: ignore[import-untyped]

from .. import database_utils
from .. import orm_models as db
from .models import SingleBert


MAX_SEQUENCE_LENGTH = 256


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


def submit_classifications(session: database_utils.Session, parallelism: int) -> bool:
    exercise_classes_by_name = {
        exercise_class.name: exercise_class
        for exercise_class in session.execute(sql.select(db.ExerciseClass)).scalars().all()
    }

    batch = (
        session.execute(
            sql.select(db.ClassificationBatch)
            .options(orm.load_only(db.ClassificationBatch.id))
            .join(db.AdaptableExercise)
            .where(db.AdaptableExercise.classified_at == sql.null())
            .distinct()
        )
        .scalars()
        .first()
    )
    if batch is None:
        return False
    else:
        exercises = list(
            session.execute(
                sql.select(db.AdaptableExercise)
                .where(
                    db.AdaptableExercise.classified_by_classification_batch == batch,
                    db.AdaptableExercise.classified_at == sql.null(),
                )
                .limit(parallelism)
            )
            .scalars()
            .all()
        )
        log(
            f"Classifying {len(exercises)} exercises from batch {batch.id}: {' '.join(str(exercise.id) for exercise in exercises)}"
        )
        dataframe = pd.DataFrame(
            {
                "id": exercise.id,
                "instruction": exercise.instruction_hint_example_text,
                "statement": exercise.statement_text,
            }
            for exercise in exercises
        )
        classify(dataframe)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        for exercise, (_, row) in zip(exercises, dataframe.iterrows()):
            exercise.classified_at = now
            exercise_class_name = row["predicted_label"]
            log(f"Classified exercise {exercise.id}: {exercise_class_name}")
            exercise_class = exercise_classes_by_name.get(exercise_class_name, None)
            if exercise_class is None:
                exercise_class = db.ExerciseClass(
                    created_at=now,
                    created_by_username="Classification",
                    name=exercise_class_name,
                    latest_strategy_settings=None,
                )
                session.add(exercise_class)
                exercise_classes_by_name[exercise_class_name] = exercise_class
            exercise.exercise_class = exercise_class

            if batch.model_for_adaptation is not None and exercise_class.latest_strategy_settings is not None:
                adaptation_strategy = db.AdaptationStrategy(
                    created_at=now,
                    created_by_username="Classification",
                    model=batch.model_for_adaptation,
                    settings=exercise_class.latest_strategy_settings,
                )
                session.add(adaptation_strategy)
                adaptation = db.Adaptation(
                    created_at=now,
                    created_by_username="Classification",
                    exercise=exercise,
                    strategy=adaptation_strategy,
                    classification_batch=batch,
                    adaptation_batch=None,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
                session.add(adaptation)
        return True


device = torch.device("cpu")
model: SingleBert | None = None


def classify(dataframe: pd.DataFrame) -> None:
    global model

    if model is None:
        model_: SingleBert = torch.load(
            os.path.join(os.path.dirname(__file__), "models/classification_camembert.pt"),
            weights_only=False,
            map_location=device,
        )
        model = model_
        model.to(device)
        model.eval()

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        os.path.join(os.path.dirname(__file__), "models/camembert_base"), do_lower_case=True, use_fast=False
    )
    # End of things to avoid loading on every request.

    input_columns = dataframe[["instruction", "statement"]].fillna("")

    input_ids: list[int] = []
    attention_mask: list[int] = []
    token_type_ids: list[int] = []
    for _, instance in input_columns.iterrows():
        inputs = tokenizer(
            instance["instruction"],
            instance["statement"],
            max_length=MAX_SEQUENCE_LENGTH,
            truncation=True,
            return_token_type_ids=True,
            add_special_tokens=True,
        )

        padding_length = MAX_SEQUENCE_LENGTH - len(inputs["input_ids"])
        input_ids.append(inputs["input_ids"] + ([tokenizer.pad_token_id] * padding_length))
        attention_mask.append(inputs["attention_mask"] + ([0] * padding_length))
        token_type_ids.append(inputs["token_type_ids"] + ([0] * padding_length))

    eval_dataset = datasets.Dataset.from_dict(
        {
            "input_ids": torch.tensor(input_ids),
            "attention_mask": torch.tensor(attention_mask),
            "token_type_ids": torch.tensor(token_type_ids),
        }
    )
    eval_dataset.set_format(type="torch", device=device)
    eval_dataloader = torch.utils.data.DataLoader(
        eval_dataset, sampler=torch.utils.data.SequentialSampler(eval_dataset), batch_size=1
    )

    predicted_label_ids: list[int] = []
    for batch in eval_dataloader:
        with torch.no_grad():
            outputs: torch.Tensor = model(
                batch["input_ids"], attention_mask=batch["attention_mask"], token_type_ids=batch["token_type_ids"]
            )
            prediction: np.ndarray[typing.Any, np.dtype[np.int32]]
            for prediction in outputs.detach().cpu().numpy():
                predicted_label_ids.append(prediction.argmax(-1))

    labels_by_id = [
        "Associe",
        "AssocieCoche",
        "CM",
        "CacheIntrus",
        "Classe",
        "ClasseCM",
        "CliqueEcrire",
        "CocheGroupeMots",
        "CocheIntrus",
        "CocheLettre",
        "CocheMot",
        "CocheMot*",
        "CochePhrase",
        "Echange",
        "EditPhrase",
        "EditTexte",
        "ExpressionEcrite",
        "GenreNombre",
        "Phrases",
        "Question",
        "RC",
        "RCCadre",
        "RCDouble",
        "RCImage",
        "Texte",
        "Trait",
        "TransformeMot",
        "TransformePhrase",
        "VraiFaux",
    ]
    dataframe.loc[:, "predicted_label"] = [labels_by_id[id] for id in predicted_label_ids]
