# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import traceback
import typing

import sqlalchemy as sql

from . import assistant_responses
from . import llm
from . import orm_models as db
from .. import database_utils
from .. import logs
from .adapted import Exercise


LlmMessage = (
    llm.UserMessage
    | llm.SystemMessage
    | llm.AssistantMessage[Exercise]
    | llm.InvalidJsonAssistantMessage
    | llm.NotJsonAssistantMessage
)


def submit_adaptations(session: database_utils.Session, parallelism: int) -> list[typing.Coroutine[None, None, None]]:
    adaptations = (
        session.query(db.Adaptation)
        .filter(db.Adaptation._initial_assistant_response == sql.null())
        .limit(parallelism)
        .all()
    )
    if len(adaptations) > 0:
        logs.log(
            f"Found {len(adaptations)} not-yet-submitted adaptations: {' '.join(str(adaptation.id) for adaptation in adaptations)}"
        )
    return [submit_adaptation(adaptation) for adaptation in adaptations]


async def submit_adaptation(adaptation: db.Adaptation) -> None:
    response_format = adaptation.settings.response_specification.make_response_format()

    messages: list[LlmMessage] = [
        llm.SystemMessage(content=adaptation.settings.system_prompt),
        llm.UserMessage(content=adaptation.exercise.full_text),
    ]

    # All branches must set 'adaptation.initial_assistant_response' to avoid infinite loop
    # (re-submitting failing adaptation again and again)
    try:
        logs.log(f"Submitting adaptation {adaptation.id}")
        with logs.timer() as timing:
            response = await adaptation.model.complete(messages, response_format)
    except llm.InvalidJsonLlmException as error:
        logs.log(f"Error 'invalid JSON' on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        adaptation.raw_llm_conversations = [error.raw_conversation]
        adaptation.initial_assistant_response = assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except llm.NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        adaptation.raw_llm_conversations = [error.raw_conversation]
        adaptation.initial_assistant_response = assistant_responses.NotJsonError(
            kind="error", error="not-json", text=error.text
        )
    except Exception:
        logs.log(f"UNEXPECTED ERROR on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        adaptation.initial_assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
        traceback.print_exc()
    else:
        logs.log(f"Success on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        adaptation.raw_llm_conversations = [response.raw_conversation]
        adaptation.initial_assistant_response = assistant_responses.Success(
            kind="success", exercise=Exercise.model_validate(response.message.content.model_dump())
        )
    finally:
        adaptation.initial_timing = timing
