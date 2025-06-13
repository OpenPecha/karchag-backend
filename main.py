# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers.public import karchag, news, audio, video,auth,edition
from routers.admin import admin_router

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Buddhist Digital Library API",
    description="API for managing Buddhist texts, categories, and related content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(karchag.router, prefix="/api/karchag", tags=["karchag"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(edition.router, prefix="/api/editions", tags=["edition"])
app.include_router(admin_router)

@app.get("/")
async def root():
    return {
        "message": "Buddhist Digital Library API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }



@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)