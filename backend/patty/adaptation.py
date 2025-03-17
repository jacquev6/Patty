from __future__ import annotations

from typing import Literal
import fastapi
import textwrap
import uuid

import pydantic

from . import llm


__all__ = ["router"]

router = fastapi.APIRouter()


class AdaptedExercise(pydantic.BaseModel):
    instructions: str
    wording: str


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[AdaptedExercise]


class InitialStep(pydantic.BaseModel):
    kind: Literal["initial"]
    system_prompt: str
    input_text: str
    messages: list[LlmMessage]
    assistant_prose: str
    adapted_exercise: AdaptedExercise | None


class AdjustmentStep(pydantic.BaseModel):
    kind: Literal["adjustment"]
    user_prompt: str
    messages: list[LlmMessage]
    assistant_prose: str
    adapted_exercise: AdaptedExercise | None


Step = InitialStep | AdjustmentStep


class Adaptation(pydantic.BaseModel):
    id: str
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    llm_model: llm.ConcreteModel
    steps: list[Step]


adaptations: dict[str, Adaptation] = {}


default_system_prompt = textwrap.dedent(
    """\
    Le premier message de l'utilisateur sera un exercice scolaire.
    Tu dois répondre en séparant et explicitant la consigne et l'énoncé de cet exercice.
    On appelle cette opération une "adaptation".

    Tu ne dois jamais résoudre les exercices, seulement les adapter.

    Dans ses messages suivants, l'utilisateur te demandera de faire des ajustements à ta réponse.
    A chaque ajustement, tu dois répondre avec la nouvelle adaptation de l'exercice initial,
    en respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.

    Le format pour tes réponses comporte deux champs: `prose` et `structured`.
    Tu dois utiliser `prose` pour interagir avec l'utilisateur, et `structured` pour renvoyer la séparation.
    Par exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.
    Tu peux aussi utiliser `prose` pour décrire brièvement les ajustements que tu as faits.
    Tu dois utiliser `structured` pour renvoyer l'adaptation de l'exercice initial, après les ajustements demandés par l'utilisateur.
    Tu peux laisser le champ `structured` null si le message de l'utilisateur ne demande pas de changement à l'adaptation."""
)


@router.get("/default-system-prompt")
def get_default_system_prompt() -> str:
    return default_system_prompt


class PostAdaptationRequest(pydantic.BaseModel):
    llm_model: llm.ConcreteModel
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    system_prompt: str
    input_text: str


@router.post("")
async def post_adaptation(req: PostAdaptationRequest) -> Adaptation:
    adaptation_id = str(uuid.uuid4())

    messages: list[LlmMessage] = [llm.SystemMessage(message=req.system_prompt), llm.UserMessage(message=req.input_text)]

    response = await req.llm_model.complete(messages, AdaptedExercise)
    messages.append(response)

    adaptation = Adaptation(
        id=adaptation_id,
        llm_model=req.llm_model,
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=req.system_prompt,
                input_text=req.input_text,
                messages=messages,
                assistant_prose=response.prose,
                adapted_exercise=response.structured,
            )
        ],
    )

    adaptations[adaptation.id] = adaptation
    return adaptation


@router.get("/{id}")
async def get_adaptation(id: str) -> Adaptation:
    return adaptations[id]


class PostAdaptationAdjustmentRequest(pydantic.BaseModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(id: str, req: PostAdaptationAdjustmentRequest) -> Adaptation:
    adaptation = adaptations[id]

    previous_messages: list[LlmMessage] = []
    for step in adaptation.steps:
        previous_messages.extend(step.messages)
    step_messages: list[LlmMessage] = [llm.UserMessage(message=req.adjustment)]

    response = await adaptation.llm_model.complete(previous_messages + step_messages, AdaptedExercise)
    step_messages.append(response)

    adaptation.steps.append(
        AdjustmentStep(
            kind="adjustment",
            user_prompt=req.adjustment,
            messages=step_messages,
            assistant_prose=response.prose,
            adapted_exercise=response.structured,
        )
    )

    return adaptation


@router.delete("/{id}/last-step")
def delete_adaptation_last_step(id: str) -> Adaptation:
    adaptation = adaptations[id]
    adaptation.steps.pop()
    return adaptation
