from __future__ import annotations

from typing import Iterable, Literal, Type
import os
import unittest

import mistralai
import mistralai.extra
import pydantic

from .base import T, Model, SystemMessage, UserMessage, AssistantMessage
from .test_utils import costs_money


# Using a global client; we'll do dependency injection at a higher abstraction level
client = mistralai.Mistral(api_key=os.environ["MISTRALAI_API_KEY"])


class MistralAiModel(Model):
    provider: Literal["mistralai"] = "mistralai"
    name: Literal["mistral-large-2411", "mistral-small-2501"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], response_type: Type[T]
    ) -> AssistantMessage[T]:
        response = await client.chat.parse_async(
            model=self.name, messages=list(self.__make_messages(messages)), response_format=response_type
        )
        assert response.choices is not None
        assert response.choices[0].message is not None
        assert response.choices[0].message.parsed is not None
        return AssistantMessage[T](message=response.choices[0].message.parsed)

    def __make_messages(
        self, messages: Iterable[SystemMessage | UserMessage | AssistantMessage[T]]
    ) -> Iterable[mistralai.models.Messages]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield mistralai.models.SystemMessage(content=message.message)
            elif isinstance(message, UserMessage):
                yield mistralai.models.UserMessage(content=message.message)
            elif isinstance(message, AssistantMessage):
                yield mistralai.models.AssistantMessage(content=message.model_dump_json())
            else:
                raise ValueError(f"Unknown message type: {message}")


class MistralAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    @costs_money
    async def test_call(self) -> None:
        class Response(pydantic.BaseModel):
            prose: str

            class Structured(pydantic.BaseModel):
                cheese: str

            structured: Structured

        model = MistralAiModel(name="mistral-small-2501")

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

        model = MistralAiModel(name="mistral-small-2501")

        response = await model.complete(
            [UserMessage(message="Donne-moi une réponse respectant le schema JSON fourni.")], ProseAndExercise
        )
        self.assertIsInstance(response.message, ProseAndExercise)
