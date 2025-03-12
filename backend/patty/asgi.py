from __future__ import annotations
import textwrap
from typing import Literal
import uuid

from fastapi import FastAPI
import mistralai
import pydantic


mistral = mistralai.Mistral(api_key="9iLjdlvUZDpc77IgNn005O2ggLO6a9Gi")


app = FastAPI()


class Cheese(pydantic.BaseModel):
    name: str


messages: list[mistralai.models.Messages] = [
    mistralai.SystemMessage(content="Please answer each question with a single word."),
    mistralai.UserMessage(content="Please name a French cheese."),
]


@app.get("/api/get-cheese")
async def get_cheese() -> Cheese:
    response = await mistral.chat.complete_async(model="mistral-small-latest", messages=messages, max_tokens=4000)
    assert response.choices is not None
    assert isinstance(response.choices[0].message.content, str)

    messages.append(response.choices[0].message)
    messages.append(mistralai.UserMessage(content="Please name another French cheese."))

    return Cheese(name=response.choices[0].message.content)


class TokenizedText(pydantic.BaseModel):
    sentences: list[Sentence]


class Sentence(pydantic.BaseModel):
    tokens: list[Token]


class Word(pydantic.BaseModel):
    kind: Literal["word"]
    text: str


class Punctuation(pydantic.BaseModel):
    kind: Literal["punctuation"]
    text: str


Token = Word | Punctuation


class InitialStep(pydantic.BaseModel):
    kind: Literal["initial"]
    system_prompt: str
    input_text: str
    messages: list[mistralai.models.Messages]
    assistant_prose: str
    tokenized_text: TokenizedText | None


class AdjustmentStep(pydantic.BaseModel):
    kind: Literal["adjustment"]
    user_prompt: str
    messages: list[mistralai.models.Messages]
    assistant_prose: str
    tokenized_text: TokenizedText | None


Step = InitialStep | AdjustmentStep


MistralModelName = Literal["mistral-large-2411", "mistral-small-2501"]


class Tokenization(pydantic.BaseModel):
    id: str
    mistral_model: MistralModelName
    steps: list[Step]


tokenizations: dict[str, Tokenization] = {}

tokenizations["0"] = Tokenization(
    id="0",
    mistral_model="mistral-small-2501",
    steps=[
        {  # type: ignore
            "kind": "initial",
            "system_prompt": "Le premier message de l'utilisateur sera un texte, que tu dois diviser en phrases et tokens.\nLes tokens peuvent être des mots ou de la ponctuation.\nOn appelle le résultat de cette division une tokenisation.\n\nDans ses messages suivants, l'utilisateur te demandera de faire des ajustements à la tokenisation du texte initial.\nA chaque ajustement, tu dois répondre avec la nouvelle tokenisation du texte initial,\nen respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.\n\nLe format pour tes réponses comporte deux champs: `prose` et `tokenized_text`.\nTu dois utiliser `prose` pour interagir avec l'utilisateur, et `tokenized_text` pour renvoyer la tokenisation.\nPar exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.\nTu peux aussi indiquer brièvement les ajustements que tu as faits dans `prose`.\nTu dois utiliser `tokenized_text` pour renvoyer la tokenisation du texte initial, après les ajustements demandés par l'utilisateur.\nCe champs comporte une liste de phrases, et chaque phrase comporte une liste de tokens.\nLes types de tokens sont distingués par le champ `kind`.\nUtilise des tokens de type `word` pour les mots, et de type `punctuation` pour la ponctuation.\n",
            "input_text": "Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...\n\nLes enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.\nIls sont prêts à aller jouer dehors.",
            "messages": [
                {
                    "content": "Le premier message de l'utilisateur sera un texte, que tu dois diviser en phrases et tokens.\nLes tokens peuvent être des mots ou de la ponctuation.\nOn appelle le résultat de cette division une tokenisation.\n\nDans ses messages suivants, l'utilisateur te demandera de faire des ajustements à la tokenisation du texte initial.\nA chaque ajustement, tu dois répondre avec la nouvelle tokenisation du texte initial,\nen respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.\n\nLe format pour tes réponses comporte deux champs: `prose` et `tokenized_text`.\nTu dois utiliser `prose` pour interagir avec l'utilisateur, et `tokenized_text` pour renvoyer la tokenisation.\nPar exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.\nTu peux aussi indiquer brièvement les ajustements que tu as faits dans `prose`.\nTu dois utiliser `tokenized_text` pour renvoyer la tokenisation du texte initial, après les ajustements demandés par l'utilisateur.\nCe champs comporte une liste de phrases, et chaque phrase comporte une liste de tokens.\nLes types de tokens sont distingués par le champ `kind`.\nUtilise des tokens de type `word` pour les mots, et de type `punctuation` pour la ponctuation.\n",
                    "role": "system",
                },
                {
                    "content": "Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...\n\nLes enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.\nIls sont prêts à aller jouer dehors.",
                    "role": "user",
                },
                {
                    "content": '{"prose":"J\'ai tokenisé le texte initial en phrases et tokens.","tokenized_text":{"sentences":[{"tokens":[{"kind":"word","text":"Aujourd\'hui"},{"kind":"punctuation","text":","},{"kind":"word","text":"l\'école"},{"kind":"word","text":"est"},{"kind":"word","text":"fermée"},{"kind":"word","text":"à"},{"kind":"word","text":"cause"},{"kind":"word","text":"de"},{"kind":"word","text":"la"},{"kind":"word","text":"neige"},{"kind":"punctuation","text":"!"},{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"sont"},{"kind":"word","text":"ravis"},{"kind":"punctuation","text":","},{"kind":"word","text":"mais"},{"kind":"word","text":"les"},{"kind":"word","text":"parents"},{"kind":"word","text":"un"},{"kind":"word","text":"peu"},{"kind":"word","text":"moins"},{"kind":"punctuation","text":"..."}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"ont"},{"kind":"word","text":"enfilé"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bottes"},{"kind":"punctuation","text":","},{"kind":"word","text":"leurs"},{"kind":"word","text":"moufles"},{"kind":"punctuation","text":","},{"kind":"word","text":"et"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bonnets"},{"kind":"punctuation","text":"."}]},{"tokens":[{"kind":"word","text":"Ils"},{"kind":"word","text":"sont"},{"kind":"word","text":"prêts"},{"kind":"word","text":"à"},{"kind":"word","text":"aller"},{"kind":"word","text":"jouer"},{"kind":"word","text":"dehors"},{"kind":"punctuation","text":"."}]}]}}',
                    "prefix": False,
                    "role": "assistant",
                },
            ],
            "assistant_prose": "J'ai tokenisé le texte initial en phrases et tokens.",
            "tokenized_text": {
                "sentences": [
                    {
                        "tokens": [
                            {"kind": "word", "text": "Aujourd'hui"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "l'école"},
                            {"kind": "word", "text": "est"},
                            {"kind": "word", "text": "fermée"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "cause"},
                            {"kind": "word", "text": "de"},
                            {"kind": "word", "text": "la"},
                            {"kind": "word", "text": "neige"},
                            {"kind": "punctuation", "text": "!"},
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "ravis"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "mais"},
                            {"kind": "word", "text": "les"},
                            {"kind": "word", "text": "parents"},
                            {"kind": "word", "text": "un"},
                            {"kind": "word", "text": "peu"},
                            {"kind": "word", "text": "moins"},
                            {"kind": "punctuation", "text": "..."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "ont"},
                            {"kind": "word", "text": "enfilé"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bottes"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "moufles"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "et"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bonnets"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Ils"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "prêts"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "aller"},
                            {"kind": "word", "text": "jouer"},
                            {"kind": "word", "text": "dehors"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                ]
            },
        },
        {  # type: ignore
            "kind": "adjustment",
            "user_prompt": "Sépare bien les phrases selon la ponctuation.",
            "messages": [
                {"content": "Sépare bien les phrases selon la ponctuation.", "role": "user"},
                {
                    "content": '{"prose":"J\'ai ajusté la tokenisation en séparant les phrases selon la ponctuation.","tokenized_text":{"sentences":[{"tokens":[{"kind":"word","text":"Aujourd\'hui"},{"kind":"punctuation","text":","},{"kind":"word","text":"l\'école"},{"kind":"word","text":"est"},{"kind":"word","text":"fermée"},{"kind":"word","text":"à"},{"kind":"word","text":"cause"},{"kind":"word","text":"de"},{"kind":"word","text":"la"},{"kind":"word","text":"neige"},{"kind":"punctuation","text":"!"}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"sont"},{"kind":"word","text":"ravis"},{"kind":"punctuation","text":","},{"kind":"word","text":"mais"},{"kind":"word","text":"les"},{"kind":"word","text":"parents"},{"kind":"word","text":"un"},{"kind":"word","text":"peu"},{"kind":"word","text":"moins"},{"kind":"punctuation","text":"..."}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"ont"},{"kind":"word","text":"enfilé"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bottes"},{"kind":"punctuation","text":","},{"kind":"word","text":"leurs"},{"kind":"word","text":"moufles"},{"kind":"punctuation","text":","},{"kind":"word","text":"et"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bonnets"},{"kind":"punctuation","text":"."}]},{"tokens":[{"kind":"word","text":"Ils"},{"kind":"word","text":"sont"},{"kind":"word","text":"prêts"},{"kind":"word","text":"à"},{"kind":"word","text":"aller"},{"kind":"word","text":"jouer"},{"kind":"word","text":"dehors"},{"kind":"punctuation","text":"."}]}]}}',
                    "prefix": False,
                    "role": "assistant",
                },
            ],
            "assistant_prose": "J'ai ajusté la tokenisation en séparant les phrases selon la ponctuation.",
            "tokenized_text": {
                "sentences": [
                    {
                        "tokens": [
                            {"kind": "word", "text": "Aujourd'hui"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "l'école"},
                            {"kind": "word", "text": "est"},
                            {"kind": "word", "text": "fermée"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "cause"},
                            {"kind": "word", "text": "de"},
                            {"kind": "word", "text": "la"},
                            {"kind": "word", "text": "neige"},
                            {"kind": "punctuation", "text": "!"},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "ravis"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "mais"},
                            {"kind": "word", "text": "les"},
                            {"kind": "word", "text": "parents"},
                            {"kind": "word", "text": "un"},
                            {"kind": "word", "text": "peu"},
                            {"kind": "word", "text": "moins"},
                            {"kind": "punctuation", "text": "..."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "ont"},
                            {"kind": "word", "text": "enfilé"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bottes"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "moufles"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "et"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bonnets"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Ils"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "prêts"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "aller"},
                            {"kind": "word", "text": "jouer"},
                            {"kind": "word", "text": "dehors"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                ]
            },
        },
        {  # type: ignore
            "kind": "adjustment",
            "user_prompt": 'Sépare "l\'école" en deux mots : "l\'" et "école".',
            "messages": [
                {"content": 'Sépare "l\'école" en deux mots : "l\'" et "école".', "role": "user"},
                {
                    "content": '{"prose":"J\'ai ajusté la tokenisation en séparant \'l\'école\' en \'l\' et \'école\'.","tokenized_text":{"sentences":[{"tokens":[{"kind":"word","text":"Aujourd\'hui"},{"kind":"punctuation","text":","},{"kind":"word","text":"l"},{"kind":"punctuation","text":"\'"},{"kind":"word","text":"école"},{"kind":"word","text":"est"},{"kind":"word","text":"fermée"},{"kind":"word","text":"à"},{"kind":"word","text":"cause"},{"kind":"word","text":"de"},{"kind":"word","text":"la"},{"kind":"word","text":"neige"},{"kind":"punctuation","text":"!"}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"sont"},{"kind":"word","text":"ravis"},{"kind":"punctuation","text":","},{"kind":"word","text":"mais"},{"kind":"word","text":"les"},{"kind":"word","text":"parents"},{"kind":"word","text":"un"},{"kind":"word","text":"peu"},{"kind":"word","text":"moins"},{"kind":"punctuation","text":"..."}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"ont"},{"kind":"word","text":"enfilé"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bottes"},{"kind":"punctuation","text":","},{"kind":"word","text":"leurs"},{"kind":"word","text":"moufles"},{"kind":"punctuation","text":","},{"kind":"word","text":"et"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bonnets"},{"kind":"punctuation","text":"."}]},{"tokens":[{"kind":"word","text":"Ils"},{"kind":"word","text":"sont"},{"kind":"word","text":"prêts"},{"kind":"word","text":"à"},{"kind":"word","text":"aller"},{"kind":"word","text":"jouer"},{"kind":"word","text":"dehors"},{"kind":"punctuation","text":"."}]}]}}',
                    "prefix": False,
                    "role": "assistant",
                },
            ],
            "assistant_prose": "J'ai ajusté la tokenisation en séparant 'l'école' en 'l' et 'école'.",
            "tokenized_text": {
                "sentences": [
                    {
                        "tokens": [
                            {"kind": "word", "text": "Aujourd'hui"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "l"},
                            {"kind": "punctuation", "text": "'"},
                            {"kind": "word", "text": "école"},
                            {"kind": "word", "text": "est"},
                            {"kind": "word", "text": "fermée"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "cause"},
                            {"kind": "word", "text": "de"},
                            {"kind": "word", "text": "la"},
                            {"kind": "word", "text": "neige"},
                            {"kind": "punctuation", "text": "!"},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "ravis"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "mais"},
                            {"kind": "word", "text": "les"},
                            {"kind": "word", "text": "parents"},
                            {"kind": "word", "text": "un"},
                            {"kind": "word", "text": "peu"},
                            {"kind": "word", "text": "moins"},
                            {"kind": "punctuation", "text": "..."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "ont"},
                            {"kind": "word", "text": "enfilé"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bottes"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "moufles"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "et"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bonnets"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Ils"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "prêts"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "aller"},
                            {"kind": "word", "text": "jouer"},
                            {"kind": "word", "text": "dehors"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                ]
            },
        },
        {  # type: ignore
            "kind": "adjustment",
            "user_prompt": 'On considère que les apostrophes marquant une elision font partie du mot, et ne sont pas de la ponctuation. Par example, pour "l\'école", tu dois former un mot comportant le "l" initial et l\'apostrophe, et un mot classique "école".',
            "messages": [
                {
                    "content": 'On considère que les apostrophes marquant une elision font partie du mot, et ne sont pas de la ponctuation. Par example, pour "l\'école", tu dois former un mot comportant le "l" initial et l\'apostrophe, et un mot classique "école".',
                    "role": "user",
                },
                {
                    "content": '{"prose":"J\'ai ajusté la tokenisation en considérant que les apostrophes marquant une élision font partie du mot.","tokenized_text":{"sentences":[{"tokens":[{"kind":"word","text":"Aujourd\'hui"},{"kind":"punctuation","text":","},{"kind":"word","text":"l\'"},{"kind":"word","text":"école"},{"kind":"word","text":"est"},{"kind":"word","text":"fermée"},{"kind":"word","text":"à"},{"kind":"word","text":"cause"},{"kind":"word","text":"de"},{"kind":"word","text":"la"},{"kind":"word","text":"neige"},{"kind":"punctuation","text":"!"}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"sont"},{"kind":"word","text":"ravis"},{"kind":"punctuation","text":","},{"kind":"word","text":"mais"},{"kind":"word","text":"les"},{"kind":"word","text":"parents"},{"kind":"word","text":"un"},{"kind":"word","text":"peu"},{"kind":"word","text":"moins"},{"kind":"punctuation","text":"..."}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"ont"},{"kind":"word","text":"enfilé"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bottes"},{"kind":"punctuation","text":","},{"kind":"word","text":"leurs"},{"kind":"word","text":"moufles"},{"kind":"punctuation","text":","},{"kind":"word","text":"et"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bonnets"},{"kind":"punctuation","text":"."}]},{"tokens":[{"kind":"word","text":"Ils"},{"kind":"word","text":"sont"},{"kind":"word","text":"prêts"},{"kind":"word","text":"à"},{"kind":"word","text":"aller"},{"kind":"word","text":"jouer"},{"kind":"word","text":"dehors"},{"kind":"punctuation","text":"."}]}]}}',
                    "prefix": False,
                    "role": "assistant",
                },
            ],
            "assistant_prose": "J'ai ajusté la tokenisation en considérant que les apostrophes marquant une élision font partie du mot.",
            "tokenized_text": {
                "sentences": [
                    {
                        "tokens": [
                            {"kind": "word", "text": "Aujourd'hui"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "l'"},
                            {"kind": "word", "text": "école"},
                            {"kind": "word", "text": "est"},
                            {"kind": "word", "text": "fermée"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "cause"},
                            {"kind": "word", "text": "de"},
                            {"kind": "word", "text": "la"},
                            {"kind": "word", "text": "neige"},
                            {"kind": "punctuation", "text": "!"},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "ravis"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "mais"},
                            {"kind": "word", "text": "les"},
                            {"kind": "word", "text": "parents"},
                            {"kind": "word", "text": "un"},
                            {"kind": "word", "text": "peu"},
                            {"kind": "word", "text": "moins"},
                            {"kind": "punctuation", "text": "..."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "ont"},
                            {"kind": "word", "text": "enfilé"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bottes"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "moufles"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "et"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bonnets"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Ils"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "prêts"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "aller"},
                            {"kind": "word", "text": "jouer"},
                            {"kind": "word", "text": "dehors"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                ]
            },
        },
        {  # type: ignore
            "kind": "adjustment",
            "user_prompt": "Merci c'est parfait!",
            "messages": [
                {"content": "Merci c'est parfait!", "role": "user"},
                {
                    "content": '{"prose":"Avec plaisir!","tokenized_text":{"sentences":[{"tokens":[{"kind":"word","text":"Aujourd\'hui"},{"kind":"punctuation","text":","},{"kind":"word","text":"l\'"},{"kind":"word","text":"école"},{"kind":"word","text":"est"},{"kind":"word","text":"fermée"},{"kind":"word","text":"à"},{"kind":"word","text":"cause"},{"kind":"word","text":"de"},{"kind":"word","text":"la"},{"kind":"word","text":"neige"},{"kind":"punctuation","text":"!"}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"sont"},{"kind":"word","text":"ravis"},{"kind":"punctuation","text":","},{"kind":"word","text":"mais"},{"kind":"word","text":"les"},{"kind":"word","text":"parents"},{"kind":"word","text":"un"},{"kind":"word","text":"peu"},{"kind":"word","text":"moins"},{"kind":"punctuation","text":"..."}]},{"tokens":[{"kind":"word","text":"Les"},{"kind":"word","text":"enfants"},{"kind":"word","text":"ont"},{"kind":"word","text":"enfilé"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bottes"},{"kind":"punctuation","text":","},{"kind":"word","text":"leurs"},{"kind":"word","text":"moufles"},{"kind":"punctuation","text":","},{"kind":"word","text":"et"},{"kind":"word","text":"leurs"},{"kind":"word","text":"bonnets"},{"kind":"punctuation","text":"."}]},{"tokens":[{"kind":"word","text":"Ils"},{"kind":"word","text":"sont"},{"kind":"word","text":"prêts"},{"kind":"word","text":"à"},{"kind":"word","text":"aller"},{"kind":"word","text":"jouer"},{"kind":"word","text":"dehors"},{"kind":"punctuation","text":"."}]}]}}',
                    "prefix": False,
                    "role": "assistant",
                },
            ],
            "assistant_prose": "Avec plaisir!",
            "tokenized_text": {
                "sentences": [
                    {
                        "tokens": [
                            {"kind": "word", "text": "Aujourd'hui"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "l'"},
                            {"kind": "word", "text": "école"},
                            {"kind": "word", "text": "est"},
                            {"kind": "word", "text": "fermée"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "cause"},
                            {"kind": "word", "text": "de"},
                            {"kind": "word", "text": "la"},
                            {"kind": "word", "text": "neige"},
                            {"kind": "punctuation", "text": "!"},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "ravis"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "mais"},
                            {"kind": "word", "text": "les"},
                            {"kind": "word", "text": "parents"},
                            {"kind": "word", "text": "un"},
                            {"kind": "word", "text": "peu"},
                            {"kind": "word", "text": "moins"},
                            {"kind": "punctuation", "text": "..."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Les"},
                            {"kind": "word", "text": "enfants"},
                            {"kind": "word", "text": "ont"},
                            {"kind": "word", "text": "enfilé"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bottes"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "moufles"},
                            {"kind": "punctuation", "text": ","},
                            {"kind": "word", "text": "et"},
                            {"kind": "word", "text": "leurs"},
                            {"kind": "word", "text": "bonnets"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                    {
                        "tokens": [
                            {"kind": "word", "text": "Ils"},
                            {"kind": "word", "text": "sont"},
                            {"kind": "word", "text": "prêts"},
                            {"kind": "word", "text": "à"},
                            {"kind": "word", "text": "aller"},
                            {"kind": "word", "text": "jouer"},
                            {"kind": "word", "text": "dehors"},
                            {"kind": "punctuation", "text": "."},
                        ]
                    },
                ]
            },
        },
    ],
)


class AssistantResponse(pydantic.BaseModel):
    prose: str
    tokenized_text: TokenizedText | None


default_tokenization_system_prompt = textwrap.dedent(
    """\
    Le premier message de l'utilisateur sera un texte, que tu dois diviser en phrases et tokens.
    Les tokens peuvent être des mots ou de la ponctuation.
    On appelle le résultat de cette division une tokenisation.

    Dans ses messages suivants, l'utilisateur te demandera de faire des ajustements à la tokenisation du texte initial.
    A chaque ajustement, tu dois répondre avec la nouvelle tokenisation du texte initial,
    en respectant les consignes de ce messages système et les ajustements demandés par l'utilisateur.

    Tu dois séparer les phrases selon la ponctuation.

    Le format pour tes réponses comporte deux champs: `prose` et `tokenized_text`.
    Tu dois utiliser `prose` pour interagir avec l'utilisateur, et `tokenized_text` pour renvoyer la tokenisation.
    Par exemple, si les instructions sont ambiguës, ou contradictoire, tu peux demander des clarifications dans `prose`.
    Tu peux aussi indiquer brièvement les ajustements que tu as faits dans `prose`.
    Tu dois utiliser `tokenized_text` pour renvoyer la tokenisation du texte initial, après les ajustements demandés par l'utilisateur.
    Ce champs comporte une liste de phrases, et chaque phrase comporte une liste de tokens.
    Les types de tokens sont distingués par le champ `kind`.
    Utilise des tokens de type `word` pour les mots, et de type `punctuation` pour la ponctuation.
    Tu peux laisser le champ `tokenized_text` null si le message de l'utilisateur ne demande pas de changement à la tokenisation.
    """
)


@app.get("/api/default-tokenization-system-prompt")
def get_default_tokenization_system_prompt() -> str:
    return default_tokenization_system_prompt


class PostTokenizationRequest(pydantic.BaseModel):
    mistral_model: MistralModelName
    # @todo Let experimenter set temperature
    # @todo Let experimenter set top_p
    # @todo Let experimenter set random_seed
    system_prompt: str
    input_text: str


@app.post("/api/tokenization")
async def post_tokenization(req: PostTokenizationRequest) -> Tokenization:
    messages: list[mistralai.models.Messages] = [
        mistralai.SystemMessage(content=req.system_prompt),
        mistralai.UserMessage(content=req.input_text),
    ]

    response = mistral.chat.parse(model=req.mistral_model, messages=messages, response_format=AssistantResponse)
    assert response.choices is not None
    assert response.choices is not None
    assert response.choices[0].message is not None
    messages.append(mistralai.AssistantMessage(content=response.choices[0].message.content))
    assert response.choices[0].message.parsed is not None

    tokenization = Tokenization(
        id=str(uuid.uuid4()),
        mistral_model=req.mistral_model,
        steps=[
            InitialStep(
                kind="initial",
                system_prompt=req.system_prompt,
                input_text=req.input_text,
                messages=messages,
                assistant_prose=response.choices[0].message.parsed.prose,
                tokenized_text=response.choices[0].message.parsed.tokenized_text,
            )
        ],
    )
    tokenizations[tokenization.id] = tokenization
    return tokenization


@app.get("/api/tokenization/{id}")
async def get_tokenization(id: str) -> Tokenization:
    return tokenizations[id]


class PostTokenizationAdjustmentRequest(pydantic.BaseModel):
    adjustment: str


@app.post("/api/tokenization/{id}/adjustment")
async def post_tokenization_adjustment(id: str, req: PostTokenizationAdjustmentRequest) -> Tokenization:
    tokenization = tokenizations[id]
    previous_messages: list[mistralai.models.Messages] = []
    for step in tokenization.steps:
        previous_messages.extend(step.messages)
    step_messages: list[mistralai.models.Messages] = [mistralai.UserMessage(content=req.adjustment)]

    response = mistral.chat.parse(
        model=tokenization.mistral_model, messages=previous_messages + step_messages, response_format=AssistantResponse
    )
    assert response.choices is not None
    assert response.choices[0].message is not None
    step_messages.append(mistralai.AssistantMessage(content=response.choices[0].message.content))
    assert response.choices[0].message.parsed is not None

    tokenization.steps.append(
        AdjustmentStep(
            kind="adjustment",
            user_prompt=req.adjustment,
            messages=step_messages,
            assistant_prose=response.choices[0].message.parsed.prose,
            tokenized_text=response.choices[0].message.parsed.tokenized_text,
        )
    )

    return tokenization


@app.delete("/api/tokenization/{id}/last-step")
def delete_tokenization_last_step(id: str) -> Tokenization:
    tokenization = tokenizations[id]
    tokenization.steps.pop()
    return tokenization
