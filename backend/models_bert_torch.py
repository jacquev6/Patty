# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>
# Copyright 2025 Elise Lincker <elise.lincker@lecnam.net>

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

# This module's sole purpose is to allow unpickling the model. It's been pickled in an environment
# where there was a 'models_bert_torch' top-level module with the 'SingleBert' class, but I've
# refactored all that in 'patty.classification'.

from patty.classification.models import SingleBert

__all__ = ["SingleBert"]
