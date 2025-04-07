import json
import os
from typing import Any, Literal
import fastapi

from .. import adapted
from .. import database_utils
from .. import llm
from ..adapted import Exercise
from ..api_utils import ApiModel
from ..api_utils import ApiModel
from .adaptation import Adaptation as DbAdaptation, Adjustment
from .input import Input as DbInput
from .strategy import Strategy as DbStrategy


__all__ = ["router"]

router = fastapi.APIRouter()


LlmMessage = llm.UserMessage | llm.SystemMessage | llm.AssistantMessage[Exercise]


class InitialStep(ApiModel):
    kind: Literal["initial"]
    system_prompt: str
    input_text: str
    messages: list[LlmMessage]
    adapted_exercise: Exercise | None


class AdjustmentStep(ApiModel):
    kind: Literal["adjustment"]
    userPrompt: str
    messages: list[LlmMessage]
    adapted_exercise: Exercise | None


Step = InitialStep | AdjustmentStep


class InputStrategy(ApiModel):
    id: int
    # Abstract type `llm.AbstractModel` would be fine for backend functionality, but this type appears in the API, so it must be concrete.
    model: llm.ConcreteModel
    system_prompt: str
    allow_choice_in_instruction: bool
    allow_arrow_in_statement: bool
    allow_free_text_input_in_statement: bool
    allow_multiple_choices_input_in_statement: bool
    allow_selectable_input_in_statement: bool


class OutputStrategy(InputStrategy):
    llm_response_schema: dict[str, Any]


class OutputAdaptation(ApiModel):
    id: int
    strategy: OutputStrategy
    steps: list[Step]
    manual_edit: Exercise | None


@router.get(
    "/latest-strategy",
    response_model=InputStrategy,  # Not 'OutputStrategy' because it will be used as the input for 'post_adaptation'
)
def get_latest_strategy(session: database_utils.SessionDependable) -> DbStrategy:
    strategy = session.query(DbStrategy).order_by(-DbStrategy.id).first()
    assert strategy is not None
    return strategy


@router.get("/llm-response-schema")
def get_llm_response_schema(
    allow_choice_in_instruction: bool,
    allow_arrow_in_statement: bool,
    allow_free_text_input_in_statement: bool,
    allow_multiple_choices_input_in_statement: bool,
    allow_selectable_input_in_statement: bool,
) -> dict[str, Any]:
    return DbStrategy(
        allow_choice_in_instruction=allow_choice_in_instruction,
        allow_arrow_in_statement=allow_arrow_in_statement,
        allow_free_text_input_in_statement=allow_free_text_input_in_statement,
        allow_multiple_choices_input_in_statement=allow_multiple_choices_input_in_statement,
        allow_selectable_input_in_statement=allow_selectable_input_in_statement,
    ).make_llm_response_schema()


class Input(ApiModel):
    id: int
    text: str


@router.get("/latest-input", response_model=Input)
def get_latest_input(session: database_utils.SessionDependable) -> DbInput:
    input = session.query(DbInput).order_by(-DbInput.id).first()
    assert input is not None
    return input


class PostAdaptationRequest(ApiModel):
    strategy: InputStrategy
    input: Input


@router.post("")
async def post_adaptation(req: PostAdaptationRequest, session: database_utils.SessionDependable) -> OutputAdaptation:
    strategy = session.get(DbStrategy, req.strategy.id)
    assert strategy is not None
    if (
        strategy.system_prompt != req.strategy.system_prompt
        or strategy.model != req.strategy.model
        or strategy.allow_choice_in_instruction != req.strategy.allow_choice_in_instruction
        or strategy.allow_arrow_in_statement != req.strategy.allow_arrow_in_statement
        or strategy.allow_free_text_input_in_statement != req.strategy.allow_free_text_input_in_statement
        or strategy.allow_multiple_choices_input_in_statement != req.strategy.allow_multiple_choices_input_in_statement
        or strategy.allow_selectable_input_in_statement != req.strategy.allow_selectable_input_in_statement
    ):
        strategy = DbStrategy(
            parent_id=strategy.id,
            model=req.strategy.model,
            system_prompt=req.strategy.system_prompt,
            allow_choice_in_instruction=req.strategy.allow_choice_in_instruction,
            allow_arrow_in_statement=req.strategy.allow_arrow_in_statement,
            allow_free_text_input_in_statement=req.strategy.allow_free_text_input_in_statement,
            allow_multiple_choices_input_in_statement=req.strategy.allow_multiple_choices_input_in_statement,
            allow_selectable_input_in_statement=req.strategy.allow_selectable_input_in_statement,
        )
        session.add(strategy)

    input = session.get(DbInput, req.input.id)
    assert input is not None
    if input.text != req.input.text:
        input = DbInput(text=req.input.text)
        session.add(input)

    session.flush()

    messages: list[LlmMessage] = [
        llm.SystemMessage(message=strategy.system_prompt),
        llm.UserMessage(message=input.text),
    ]

    response = await strategy.model.complete(messages, strategy.make_llm_response_type())
    messages.append(response)

    db_adaptation = DbAdaptation(
        strategy_id=strategy.id, input_id=input.id, initial_response=response.message, adjustments=[]
    )
    session.add(db_adaptation)
    session.flush()

    return make_output_adaptation(db_adaptation)


@router.get("/{id}")
async def get_adaptation(id: str, session: database_utils.SessionDependable) -> OutputAdaptation:
    db_adaptation = session.get(DbAdaptation, id)
    if db_adaptation is None:
        raise fastapi.HTTPException(status_code=404, detail="Adaptation not found")
    else:
        return make_output_adaptation(db_adaptation)


class PostAdaptationAdjustmentRequest(ApiModel):
    adjustment: str


@router.post("/{id}/adjustment")
async def post_adaptation_adjustment(
    id: str, req: PostAdaptationAdjustmentRequest, session: database_utils.SessionDependable
) -> OutputAdaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    assert db_adaptation.initial_response is not None

    messages: list[LlmMessage] = [
        llm.SystemMessage(message=db_adaptation.strategy.system_prompt),
        llm.UserMessage(message=db_adaptation.input.text),
        llm.AssistantMessage[Exercise](message=db_adaptation.initial_response),
    ]
    for adjustment in db_adaptation.adjustments:
        messages.append(llm.UserMessage(message=adjustment.user_prompt))
        messages.append(llm.AssistantMessage[Exercise](message=adjustment.assistant_response))
    messages.append(llm.UserMessage(message=req.adjustment))

    response = await db_adaptation.strategy.model.complete(messages, db_adaptation.strategy.make_llm_response_type())

    adjustments = list(db_adaptation.adjustments)
    adjustments.append(
        Adjustment(user_prompt=req.adjustment, assistant_response=Exercise(**response.message.model_dump()))
    )
    db_adaptation.adjustments = adjustments

    return make_output_adaptation(db_adaptation)


@router.delete("/{id}/last-step")
def delete_adaptation_last_step(id: str, session: database_utils.SessionDependable) -> OutputAdaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    adjustments = list(db_adaptation.adjustments)
    adjustments.pop()
    db_adaptation.adjustments = adjustments
    return make_output_adaptation(db_adaptation)


@router.put("/{id}/manual-edit")
def put_adaptation_manual_edit(id: str, req: Exercise, session: database_utils.SessionDependable) -> OutputAdaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    db_adaptation.manual_edit = req
    return make_output_adaptation(db_adaptation)


@router.delete("/{id}/manual-edit")
def delete_adaptation_manual_edit(id: str, session: database_utils.SessionDependable) -> OutputAdaptation:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    db_adaptation.manual_edit = None
    return make_output_adaptation(db_adaptation)


def make_output_adaptation(adaptation: DbAdaptation) -> OutputAdaptation:
    assert adaptation.initial_response is not None
    return OutputAdaptation(
        id=adaptation.id,
        strategy=make_output_strategy(adaptation.strategy),
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=adaptation.strategy.system_prompt,
                input_text=adaptation.input.text,
                messages=[
                    llm.SystemMessage(message=adaptation.strategy.system_prompt),
                    llm.UserMessage(message=adaptation.input.text),
                    llm.AssistantMessage[Exercise](message=adaptation.initial_response),
                ],
                adapted_exercise=adaptation.initial_response,
            )
        ]
        + [
            AdjustmentStep(
                kind="adjustment",
                userPrompt=adjustment.user_prompt,
                messages=[
                    llm.UserMessage(message=adjustment.user_prompt),
                    llm.AssistantMessage[Exercise](message=adjustment.assistant_response),
                ],
                adapted_exercise=adjustment.assistant_response,
            )
            for adjustment in adaptation.adjustments
        ],
        manual_edit=adaptation.manual_edit,
    )


def make_output_strategy(strategy: DbStrategy) -> OutputStrategy:
    return OutputStrategy(
        id=strategy.id,
        model=strategy.model,
        system_prompt=strategy.system_prompt,
        allow_choice_in_instruction=strategy.allow_choice_in_instruction,
        allow_arrow_in_statement=strategy.allow_arrow_in_statement,
        allow_free_text_input_in_statement=strategy.allow_free_text_input_in_statement,
        allow_multiple_choices_input_in_statement=strategy.allow_multiple_choices_input_in_statement,
        allow_selectable_input_in_statement=strategy.allow_selectable_input_in_statement,
        llm_response_schema=strategy.make_llm_response_schema(),
    )


export_adaptation_template_file_path = os.path.join(
    os.path.dirname(__file__), "templates", "adaptation-export", "index.html"
)


@router.get("/export/{id}.html", response_class=fastapi.responses.HTMLResponse)
def export_adaptation(
    id: str, session: database_utils.SessionDependable, download: bool = True
) -> fastapi.responses.HTMLResponse:
    db_adaptation = session.get(DbAdaptation, id)
    assert db_adaptation is not None
    assert db_adaptation.initial_response is not None

    if db_adaptation.manual_edit is None:
        exercise = db_adaptation.initial_response
        for adjustment in db_adaptation.adjustments:
            if adjustment.assistant_response is not None:
                exercise = adjustment.assistant_response
    else:
        exercise = db_adaptation.manual_edit

    data = exercise.model_dump_json().replace("\\", "\\\\").replace('"', '\\"')
    with open(export_adaptation_template_file_path) as f:
        template = f.read()

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{id}.html"'

    return fastapi.responses.HTMLResponse(content=template.replace("{{ data }}", data), headers=headers)
