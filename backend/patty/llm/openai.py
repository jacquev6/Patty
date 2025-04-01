from typing import Iterable, Literal, Type
import os
import unittest

import openai
import openai.types.chat
import pydantic

from .base import T, Model, SystemMessage, UserMessage, AssistantMessage
from .test_utils import costs_money


# Using a global client; we'll do dependency injection at a higher abstraction level
client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


class OpenAiModel(Model):
    provider: Literal["openai"] = "openai"
    name: Literal["gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], response_type: Type[T]
    ) -> AssistantMessage[T]:
        response = await client.beta.chat.completions.parse(
            model=self.name, messages=list(self.__make_messages(messages)), response_format=response_type
        )
        assert response.choices[0].message.parsed is not None
        return AssistantMessage[T](message=response.choices[0].message.parsed)

    def __make_messages(
        self, messages: Iterable[SystemMessage | UserMessage | AssistantMessage[T]]
    ) -> Iterable[openai.types.chat.ChatCompletionMessageParam]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield openai.types.chat.ChatCompletionDeveloperMessageParam(role="developer", content=message.message)
            elif isinstance(message, UserMessage):
                yield openai.types.chat.ChatCompletionUserMessageParam(role="user", content=message.message)
            elif isinstance(message, AssistantMessage):
                yield openai.types.chat.ChatCompletionAssistantMessageParam(
                    role="assistant", content=message.model_dump_json()
                )
            else:
                raise ValueError(f"Unknown message type: {message}")


class OpenAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    @costs_money
    async def test_call(self) -> None:
        class Response(pydantic.BaseModel):
            prose: str

            class Structured(pydantic.BaseModel):
                cheese: str

            structured: Structured

        model = OpenAiModel(name="gpt-4o-mini-2024-07-18")

        messages: list[SystemMessage | UserMessage | AssistantMessage[Response]] = [
            SystemMessage(
                message="Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible."
            ),
            UserMessage(message="Donne-moi le nom d'un fromage."),
        ]

        response1 = await model.complete(messages, Response)
        assert response1.message.structured is not None
        self.assertIn("fromage", response1.message.prose.lower())

        messages.append(response1)
        messages.append(UserMessage(message="Un autre."))

        response2 = await model.complete(messages, Response)
        assert response2.message.structured is not None
        self.assertNotEqual(response1.message.structured.cheese, response2.message.structured.cheese)

    @costs_money
    async def test_adaptation_schema(self) -> None:
        from ..adaptation.router import ProseAndExercise

        model = OpenAiModel(name="gpt-4o-mini-2024-07-18")

        response = await model.complete(
            [UserMessage(message="Donne-moi une réponse respectant le schema JSON fourni.")], ProseAndExercise
        )
        self.assertIsInstance(response.message, ProseAndExercise)
