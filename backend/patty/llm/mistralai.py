from __future__ import annotations

from typing import Iterable, Literal, Type
import os
import unittest

import mistralai
import mistralai.extra
import pydantic

from .base import Model, SystemMessage, UserMessage, AssistantMessage
from .utils import T, ResponseFormat, make_response_format_type, costs_money


# Using a global client; we'll do dependency injection at a higher abstraction level
client = mistralai.Mistral(api_key=os.environ["MISTRALAI_API_KEY"])


class MistralAiModel(Model):
    provider: Literal["mistralai"] = "mistralai"
    name: Literal["mistral-large-2411", "mistral-small-2501"]

    async def complete(
        self, messages: list[SystemMessage | UserMessage | AssistantMessage[T]], structured_type: Type[T]
    ) -> AssistantMessage[T]:
        response_format = make_response_format_type(structured_type)
        response = await client.chat.parse_async(
            model=self.name,
            messages=list(self.__make_messages(messages, response_format)),
            response_format=response_format,
        )
        assert response.choices is not None
        assert response.choices[0].message is not None
        assert response.choices[0].message.parsed is not None
        return AssistantMessage[T](
            prose=response.choices[0].message.parsed.prose, structured=response.choices[0].message.parsed.structured
        )

    def __make_messages(
        self,
        messages: Iterable[SystemMessage | UserMessage | AssistantMessage[T]],
        response_format: Type[ResponseFormat[T]],
    ) -> Iterable[mistralai.models.Messages]:
        for message in messages:
            if isinstance(message, SystemMessage):
                yield mistralai.models.SystemMessage(content=message.message)
            elif isinstance(message, UserMessage):
                yield mistralai.models.UserMessage(content=message.message)
            elif isinstance(message, AssistantMessage):
                yield mistralai.models.AssistantMessage(
                    content=response_format(prose=message.prose, structured=message.structured).model_dump_json()
                )
            else:
                raise ValueError(f"Unknown message type: {message}")


class MistralAiModelTestCase(unittest.IsolatedAsyncioTestCase):
    class Structured(pydantic.BaseModel):
        cheese: str

    def test_assistant_message(self) -> None:
        message = AssistantMessage[MistralAiModelTestCase.Structured](
            prose="Hello", structured=self.Structured(cheese="brie")
        )
        assert message.structured is not None
        self.assertEqual(message.structured.cheese, "brie")

    def test_response_format(self) -> None:
        response = ResponseFormat[MistralAiModelTestCase.Structured](
            prose="Hello", structured=self.Structured(cheese="brie")
        )
        assert response.structured is not None
        self.assertEqual(response.structured.cheese, "brie")

    def test_response_format_schema(self) -> None:
        self.assertEqual(
            mistralai.extra.response_format_from_pydantic_model(ResponseFormat[MistralAiModelTestCase.Structured]),
            mistralai.ResponseFormat(
                type="json_schema",
                json_schema=mistralai.JSONSchema(
                    name="ResponseFormat[MistralAiModelTestCase.Structured]",
                    schema_definition={
                        "$defs": {
                            "Structured": {
                                "properties": {"cheese": {"title": "Cheese", "type": "string"}},
                                "required": ["cheese"],
                                "title": "Structured",
                                "type": "object",
                                "additionalProperties": False,
                            }
                        },
                        "properties": {
                            "prose": {"title": "Prose", "type": "string"},
                            "structured": {"anyOf": [{"$ref": "#/$defs/Structured"}, {"type": "null"}]},
                        },
                        "required": ["prose", "structured"],
                        "title": "ResponseFormat[MistralAiModelTestCase.Structured]",
                        "type": "object",
                        "additionalProperties": False,
                    },
                    strict=True,
                ),
            ),
        )

    def test_jsonify_model(self) -> None:
        model = MistralAiModel(name="mistral-small-2501")
        self.assertEqual(model.model_dump(), {"provider": "mistralai", "name": "mistral-small-2501"})

    @costs_money
    async def test_call(self) -> None:
        model = MistralAiModel(name="mistral-small-2501")

        messages: list[SystemMessage | UserMessage | AssistantMessage[MistralAiModelTestCase.Structured]] = [
            SystemMessage(
                message="Utilise le champ `prose` pour tes commentaires, et le champs `structured` pour le contenu de ta réponse. Dans ce champs, donne des réponses aussi concises que possible."
            ),
            UserMessage(message="Donne-moi le nom d'un fromage."),
        ]

        response1 = await model.complete(messages, MistralAiModelTestCase.Structured)
        assert response1.structured is not None
        self.assertIn("fromage", response1.prose.lower())

        messages.append(response1)
        messages.append(UserMessage(message="Un autre."))

        response2 = await model.complete(messages, MistralAiModelTestCase.Structured)
        assert response2.structured is not None
        self.assertNotEqual(response1.structured.cheese, response2.structured.cheese)

    @costs_money
    async def test_adaptation_schema(self) -> None:
        from ..adaptation import AdaptedExercise

        model = MistralAiModel(name="mistral-small-2501")

        response = await model.complete(
            [UserMessage(message="Donne-moi une réponse respectant le schema JSON fourni.")], AdaptedExercise
        )
        self.assertIsInstance(response.structured, AdaptedExercise)
