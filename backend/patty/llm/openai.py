from typing import Iterable, Literal, Type
import os
import unittest

import openai
import openai.types.chat
import pydantic

from .base import Model, SystemMessage, UserMessage, AssistantMessage
from .utils import T, ResponseFormat, make_response_format_type


# Using a global client; we'll do dependency injection at a higher abstraction level
client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


class OpenAiModel(Model):
    provider: Literal["openai"] = "openai"
    name: Literal["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], structured_type: Type[T]
    ) -> AssistantMessage[T]:
        response_format = make_response_format_type(structured_type)
        response = await client.beta.chat.completions.parse(
            model=self.name,
            messages=list(self.__make_messages(messages, response_format)),
            response_format=response_format,
        )
        assert response.choices[0].message.parsed is not None
        return AssistantMessage[T](
            prose=response.choices[0].message.parsed.prose, structured=response.choices[0].message.parsed.structured
        )

    def __make_messages(
        self,
        messages: Iterable[SystemMessage | UserMessage | AssistantMessage[T]],
        response_format: Type[ResponseFormat[T]],
    ) -> Iterable[openai.types.chat.ChatCompletionMessageParam]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield openai.types.chat.ChatCompletionDeveloperMessageParam(role="developer", content=message.message)
            elif isinstance(message, UserMessage):
                yield openai.types.chat.ChatCompletionUserMessageParam(role="user", content=message.message)
            elif isinstance(message, AssistantMessage):
                yield openai.types.chat.ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=response_format(prose=message.prose, structured=message.structured).model_dump_json(),
                )
            else:
                raise ValueError(f"Unknown message type: {message}")


class OpenAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    class Structured(pydantic.BaseModel):
        cheese: str

    @unittest.skipUnless("PATTY_RUN_TESTS_COSTING_MONEY" in os.environ, "Costs money")
    async def test_call(self) -> None:
        model = OpenAiModel(name="gpt-4o-mini-2024-07-18")

        messages: list[SystemMessage | UserMessage | AssistantMessage[OpenAiModelTestCase.Structured]] = [
            SystemMessage(
                message="Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible."
            ),
            UserMessage(message="Donne-moi le nom d'un fromage."),
        ]

        response1 = await model.complete(messages, OpenAiModelTestCase.Structured)
        self.assertIn("fromage", response1.prose.lower())

        messages.append(response1)
        messages.append(UserMessage(message="Un autre."))

        response2 = await model.complete(messages, OpenAiModelTestCase.Structured)
        self.assertNotEqual(response1.structured.cheese, response2.structured.cheese)
