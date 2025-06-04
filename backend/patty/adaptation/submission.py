import datetime
import traceback
import typing


from .. import database_utils
from .. import llm
from ..adapted import Exercise
from .adaptation import AssistantInvalidJsonError, AssistantNotJsonError, AssistantUnknownError, AssistantSuccess
from ..new_orm_models import Adaptation


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


LlmMessage = (
    llm.UserMessage
    | llm.SystemMessage
    | llm.AssistantMessage[Exercise]
    | llm.InvalidJsonAssistantMessage
    | llm.NotJsonAssistantMessage
)


def submit_adaptations(session: database_utils.Session, parallelism: int) -> list[typing.Coroutine[None, None, None]]:
    adaptations = (
        session.query(Adaptation).filter(Adaptation._initial_assistant_response == None).limit(parallelism).all()
    )
    log(
        f"Found {len(adaptations)} not-yet-submitted adaptations: {' '.join(str(adaptation.id) for adaptation in adaptations)}"
    )
    return [submit_adaptation(adaptation) for adaptation in adaptations]


async def submit_adaptation(adaptation: Adaptation) -> None:
    response_format = adaptation.strategy.settings.response_specification.make_response_format()

    messages: list[LlmMessage] = [
        llm.SystemMessage(content=adaptation.strategy.settings.system_prompt),
        llm.UserMessage(content=adaptation.exercise.full_text),
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
