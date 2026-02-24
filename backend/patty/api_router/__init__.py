# MALIN Platform https://malin.cahiersfantastiques.fr/
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

import fastapi

from .. import authentication
from .adaptations import router as adaptations_router
from .export import router as export_router
from .pdfs import router as pdfs_router
from .sandbox_adaptation import router as sandbox_adaptation_router
from .sandbox_classification import router as sandbox_classification_router
from .sandbox_extraction import router as sandbox_extraction_router
from .textbooks import router as textbooks_router


api_router = fastapi.APIRouter(dependencies=[fastapi.Depends(authentication.auth_bearer_dependable)])
api_router.include_router(adaptations_router)
api_router.include_router(pdfs_router)
api_router.include_router(sandbox_adaptation_router)
api_router.include_router(sandbox_classification_router)
api_router.include_router(sandbox_extraction_router)
api_router.include_router(textbooks_router)

__all__ = ["api_router", "export_router"]
