# Copyright 2025 Elise Lincker <elise.lincker@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

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


from . import orm_models as db
from .. import adaptation
from .. import database_utils
from .. import logs
from .. import settings
from .models import SingleBert

MAX_SEQUENCE_LENGTH = 256


def submit_classifications(session: database_utils.Session, parallelism: int) -> bool:
    exercise_classes_by_name = {
        exercise_class.name: exercise_class
        for exercise_class in session.execute(sql.select(adaptation.ExerciseClass)).scalars().all()
    }

    chunk = (
        session.execute(
            sql.select(db.ClassificationChunk)
            .options(orm.load_only(db.ClassificationChunk.id))
            .join(db.ClassificationByChunk)
            .where(db.ClassificationByChunk.exercise_class == sql.null())
            .distinct()
        )
        .scalars()
        .first()
    )
    if chunk is None:
        return False
    else:
        logs.log(
            f"Classifying {len(chunk.classifications)} exercises from chunk {chunk.id}: {' '.join(str(classification.exercise.id) for classification in chunk.classifications)}"
        )
        dataframe = pd.DataFrame(
            {
                "id": classification.exercise.id,
                "instruction": classification.exercise.instruction_hint_example_text,
                "statement": classification.exercise.statement_text,
            }
            for classification in chunk.classifications
        )
        with logs.timer() as timing:
            classify(dataframe)
        chunk.timing = timing
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        for classification, (_, row) in zip(chunk.classifications, dataframe.iterrows()):
            exercise_class_name = row["predicted_label"]
            logs.log(f"Classified exercise {classification.exercise.id}: {exercise_class_name}")
            exercise_class = exercise_classes_by_name.get(exercise_class_name, None)
            if exercise_class is None:
                exercise_class = adaptation.ExerciseClass(
                    created=db.ExerciseClassCreationByChunk(at=now, classification_chunk=chunk),
                    name=exercise_class_name,
                    latest_strategy_settings=None,
                )
                session.add(exercise_class)
                exercise_classes_by_name[exercise_class_name] = exercise_class
            classification.exercise_class = exercise_class
            classification.at = now

            if chunk.model_for_adaptation is not None and exercise_class.latest_strategy_settings is not None:
                exercise_adaptation = adaptation.Adaptation(
                    created=db.AdaptationCreationByChunk(at=now, classification_chunk=chunk),
                    exercise=classification.exercise,
                    settings=exercise_class.latest_strategy_settings,
                    model=chunk.model_for_adaptation,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    initial_timing=None,
                    adjustments=[],
                    manual_edit=None,
                    approved_by=None,
                    approved_at=None,
                )
                session.add(exercise_adaptation)
        return True


device = torch.device("cpu")
model: SingleBert | None = None


def classify(dataframe: pd.DataFrame) -> None:
    global model

    if model is None:
        logs.log(f"Loading classification model from {settings.CLASSIFICATION_CAMEMBERT_2025_05_20_PATH}")
        model_: SingleBert = torch.load(
            settings.CLASSIFICATION_CAMEMBERT_2025_05_20_PATH, weights_only=False, map_location=device
        )
        model = model_
        model.to(device)
        model.eval()

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        os.path.join(os.path.dirname(__file__), "models/camembert_base"), do_lower_case=True, use_fast=False
    )

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
