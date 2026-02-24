# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Elise Lincker <elise.lincker@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
