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
from .. import new_orm_models as db
from .models import SingleBert


MAX_SEQUENCE_LENGTH = 256


# router = fastapi.APIRouter()


# @router.get("/test")
# def test_classification() -> dict[str, typing.Any]:
#     csv_input_file = io.StringIO(
#         textwrap.dedent(
#             """\
#             id,instruction,statement
#             P90Ex1,Recopie les deux mots de chaque phrase qui se prononcent de la même façon.,"a. Il a gagné le gros lot à la kermesse des écoles. b. À la fin du film, il y a une bonne surprise. c. Il a garé sa voiture dans le parking, à droite de la nôtre. d. Il m'a invité à venir chez lui. e. Mon oncle a un vélo à vendre."
#             P90Ex2,Recopie uniquement les phrases avec le verbe avoir.,a. Ce chien a mordu son maître*. b. Je rentre à la maison à midi pour déjeuner en famille. c. On a froid dans ce sous-bois ombragé. d. Il pense toujours qu'il a raison. e. Tu joues à chat avec moi ?
#             P90Ex3,Recopie et complète ces phrases avec à ou a. Écris avait pour justifier l'emploi de a. Il a (avait) une maison à la campagne.,"a. L'épicerie est ... côté, elle ... une façade jaune. b. L'ordinateur ... remplacé la machine ... écrire. c. Je ne sais pas ... quelle heure il ... décidé d'arriver. d. Elle ... invité tous ses amis ... son anniversaire. e. Maman ... une robe très ... la mode."
#             P90Ex4,Recopie ces phrases et mets un accent grave sur les a soulignés quand c'est nécessaire.,a. Je n'ai plus rien a lire. b. Ils attendent leurs amis a l'entrée du cinéma. c. Le match a mal commencé pour nous. d. Il a trouvé a manger dans le frigo. e. Ce n'est pas beau a voir.
#             P90Ex5,Recopie les deux mots de chaque phrase qui se prononcent de la même façon.,a. Mon frère est parti se promener et j'attends son retour. b. Paul et Léa ont un ami qui est hollandais. c. Il est arrivé premier et moi troisième. d. La Suisse est un pays situé entre la France et l'Italie. e. Mon ordinateur est en panne et je vais le faire réparer.
#             P90Ex6,Recopie uniquement les phrases avec le verbe être.,a. Mon père est très content de mon travail. b. J'ai acheté une bande dessinée et un livre illustré. c. Ce spectacle est formidable. d. J'aime aller à la plage et faire des châteaux de sable. e. C'est bien ici que vous habitez ?
#             P90Ex7,Recopie et complète ces phrases avec et ou est. Écris était pour justifier l'emploi de est. Elle est (était) contente et souriante.,a. On ... là pour le voir; on lui a apporté des livres ... des sucreries. b. Ce garçon ... serviable ... courageux. c. Le joli singe ... admiré par les visiteurs ... par les gardiens. d. C'... un bijou rare ... précieux. e. Où ... mon jeu vidéo ? J'ai fouillé ma chambre ... le salon.
#             P90Ex8,Recopie et complète ces phrases avec est ou et.,"a. Tu as fini ton entraînement* ... maintenant, tu vas te reposer. b. Le cerf a entendu les chasseurs ... il s'... sauvé. c. Il ... venu ... il ... reparti. d. Le pirate ... monté sur le bateau ... il a pris l'or ... l'argent. e. Rachid... très gentil... il ... agréable à fréquenter."
#             P90Ex9,Recopie uniquement les phrases avec le verbe avoir.,"a. On arrivera vers midi si la route est libre. b. Ils ont acheté un bateau à moteur. c. Dans ma famille, on aime se retrouver pour fêter Noël. d. Ces arbres ont l'air de bien pousser. e. Sur le quai, même les goélands ont froid."
#             """
#         )
#     )
#     return {"df": classify(pd.read_csv(csv_input_file, header=[0])).to_dict(orient="records")}


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


def submit_classifications(session: database_utils.Session) -> None:
    exercise_classes_by_name = {
        exercise_class.name: exercise_class
        for exercise_class in session.execute(sql.select(db.ExerciseClass)).scalars().all()
    }

    batches = (
        session.execute(
            sql.select(db.ClassificationBatch)
            .options(orm.load_only(db.ClassificationBatch.id))
            .join(db.AdaptableExercise)
            .where(db.AdaptableExercise.classified_at == None)
            .distinct()
        )
        .scalars()
        .all()
    )
    log(
        f"Found {len(batches)} classification batches with not-yet-classified exercises: {' '.join(str(batch.id) for batch in batches)}"
    )
    for batch in batches:
        exercises = list(batch.exercises)
        log(
            f"Classifying batch {batch.id} with {len(exercises)} exercises: {' '.join(str(exercise.id) for exercise in exercises)}"
        )
        dataframe = pd.DataFrame(
            {
                "id": exercise.id,
                "instruction": exercise.instruction_example_hint_text,
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
                # session.flush()
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
                    adaptation_batch=None,
                    raw_llm_conversations=[],
                    initial_assistant_response=None,
                    adjustments=[],
                    manual_edit=None,
                )
                session.add(adaptation)


def classify(dataframe: pd.DataFrame) -> None:
    # @todo Avoid loading these on every request.
    device = torch.device("cpu")
    model: SingleBert = torch.load(
        os.path.join(os.path.dirname(__file__), "models/classification_camembert.pt"),
        weights_only=False,
        map_location=device,
    )
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
