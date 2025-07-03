from fastapi import APIRouter
from .sermons import router as sermons_router
from .translation_types import router as translation_types_router

router = APIRouter(prefix="/lookups", tags=["Lookups"])

# Include sub-routers
router.include_router(sermons_router, prefix="/sermons", tags=["Sermons"])
router.include_router(translation_types_router, prefix="/translation-types", tags=["Translation Types"])
