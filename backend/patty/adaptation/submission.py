import asyncio
import datetime
import time
import traceback

import requests

from .. import database_utils
from .. import llm
from ..adapted import Exercise
from .adaptation import (
    Adaptation,
    AssistantInvalidJsonError,
    AssistantNotJsonError,
    AssistantUnknownError,
    AssistantSuccess,
)
from .router import LlmMessage
from .. import settings


# @todo Reload code changes in the development environment


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


async def daemon(engine: database_utils.Engine, parallelism: int, pause: float, exit_when_done: bool = False) -> None:
    last_time = time.monotonic()
    while True:
        log("Waking up...")
        try:
            with database_utils.Session(engine) as session:
                adaptations = (
                    session.query(Adaptation)
                    .filter(Adaptation._initial_assistant_response == None)
                    .limit(parallelism)
                    .all()
                )
                if len(adaptations) == 0:
                    log("No not-yet-submitted adaptation found")
                    if exit_when_done:
                        log("Exiting")
                        break
                else:
                    log(f"Found adaptation(s) {' '.join([str(adaptation.id) for adaptation in adaptations])}")
                    submissions = [submit_adaptation(adaptation) for adaptation in adaptations]
                    await asyncio.gather(*submissions)
                    session.commit()
            if time.monotonic() >= last_time + 60:
                log("Calling pulse monitoring URL")
                last_time = time.monotonic()
                requests.post(settings.SUBMISSION_DAEMON_PULSE_MONITORING_URL)
        except:  # Pokemon programming: gotta catch 'em all
            log("UNEXPECTED ERROR")
            traceback.print_exc()
        log(f"Sleeping for {pause}s...")
        await asyncio.sleep(pause)


async def submit_adaptation(adaptation: Adaptation) -> None:
    response_format = adaptation.strategy.settings.response_specification.make_response_format()

    messages: list[LlmMessage] = [
        llm.SystemMessage(content=adaptation.strategy.settings.system_prompt),
        llm.UserMessage(content=adaptation.input.text),
    ]

    # All branches must set 'adaptation.initial_assistant_response' to avoid infinite loop
    # (re-submitting failing adaptation again and again)
    try:
        log(f"Submitting adaptation {adaptation.id}")
        response = await adaptation.strategy.model.complete(messages, response_format)
    except llm.InvalidJsonLlmException as error:
        log(f"Error 'invalid JSON' on adaptation {adaptation.id}")
        adaptation.raw_llm_conversations = [error.raw_conversation]
        adaptation.initial_assistant_response = AssistantInvalidJsonError(
            kind="error", error="invalid-json", parsed=error.parsed
        )
    except llm.NotJsonLlmException as error:
        log(f"Error 'not JSON' on adaptation {adaptation.id}")
        adaptation.raw_llm_conversations = [error.raw_conversation]
        adaptation.initial_assistant_response = AssistantNotJsonError(kind="error", error="not-json", text=error.text)
    except:
        log(f"UNEXPECTED ERROR on adaptation {adaptation.id}")
        adaptation.initial_assistant_response = AssistantUnknownError(kind="error", error="unknown")
        traceback.print_exc()
    else:
        log(f"Success on adaptation {adaptation.id}")
        adaptation.raw_llm_conversations = [response.raw_conversation]
        adaptation.initial_assistant_response = AssistantSuccess(
            kind="success", exercise=Exercise(**response.message.content.model_dump())
        )
