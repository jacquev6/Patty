# Copyright 2025 Elise Lincker <elise.lincker@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import typing

import torch.nn
import transformers  # type: ignore[import-untyped]


class SingleBert(torch.nn.Module):
    def __init__(self, model: str, labels: list[str]) -> None:
        super().__init__()
        config = transformers.AutoConfig.from_pretrained(model)
        assert "camembert" in model
        self.model: transformers.CamembertModel = transformers.CamembertModel.from_pretrained(model)
        self.drop = torch.nn.Dropout(0.2)
        self.classifier = torch.nn.Linear(config.hidden_size, len(labels))

    def forward(self, ids: torch.Tensor, attention_mask: torch.Tensor, token_type_ids: torch.Tensor) -> torch.Tensor:
        embedding: torch.Tensor = self.model(ids, attention_mask=attention_mask, token_type_ids=token_type_ids)[0]
        return typing.cast(torch.Tensor, self.classifier(self.drop(embedding.mean(dim=1))))
