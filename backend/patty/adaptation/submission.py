# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import json
import traceback
import typing

import sqlalchemy as sql

from . import assistant_responses
from . import llm
from . import orm_models as db
from .. import database_utils
from .. import logs
from ..any_json import JsonList
from ..retry import RetryableError
from .adapted import Exercise


LlmMessage = (
    llm.UserMessage
    | llm.SystemMessage
    | llm.AssistantMessage[Exercise]
    | llm.InvalidJsonAssistantMessage
    | llm.NotJsonAssistantMessage
)


def submit_next_adaptation(
    can_retry: bool, session: database_utils.Session
) -> typing.Coroutine[None, None, None] | None:
    adaptation = (
        session.execute(sql.select(db.Adaptation).where(db.Adaptation._initial_assistant_response == sql.null()))
        .scalars()
        .first()
    )

    if adaptation is None:
        return None
    else:
        logs.log(f"Found pending adaptation: {adaptation.id}")
        return submit_adaptation(can_retry, adaptation)


async def submit_adaptation(can_retry: bool, adaptation: db.Adaptation) -> None:
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
        raw_llm_conversations: JsonList = [error.raw_conversation]
        initial_assistant_response: assistant_responses.Response = assistant_responses.InvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except llm.NotJsonLlmException as error:
        logs.log(f"Error 'not JSON' on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        raw_llm_conversations = [error.raw_conversation]
        initial_assistant_response = assistant_responses.NotJsonError(kind="error", error="not-json", text=error.text)
    except RetryableError:
        if can_retry:
            logs.log(f"RETRYABLE ERROR on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
            raise
        else:
            logs.log(f"Too many RETRYABLE ERRORS on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
            raw_llm_conversations = []
            initial_assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
    except Exception:
        logs.log(f"UNEXPECTED ERROR on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        raw_llm_conversations = []
        initial_assistant_response = assistant_responses.UnknownError(kind="error", error="unknown")
        traceback.print_exc()
    else:
        logs.log(f"Success on adaptation {adaptation.id} in {timing.elapsed:.1f} seconds")
        raw_llm_conversations = [response.raw_conversation]
        initial_assistant_response = assistant_responses.Success(
            kind="success", exercise=Exercise.model_validate(response.message.content.model_dump())
        )
    finally:
        try:
            json.dumps(raw_llm_conversations)
        except TypeError:
            logs.log(f"Raw conversation not JSON-serializable: {raw_llm_conversations}")
            raw_llm_conversations = ["Error: conversation not JSON-serializable"]
        adaptation.raw_llm_conversations = raw_llm_conversations
        adaptation.initial_assistant_response = initial_assistant_response
        adaptation.initial_timing = timing
