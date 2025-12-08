# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

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
