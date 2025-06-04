from fastapi import APIRouter
from . import categories, texts, audio, video, news, lookups, users

# Create main admin router
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Include all sub-routers
admin_router.include_router(categories.router)
admin_router.include_router(texts.router)
admin_router.include_router(audio.router)
admin_router.include_router(video.router)
admin_router.include_router(news.router)
admin_router.include_router(lookups.router)
admin_router.include_router(users.router)