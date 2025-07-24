#!/usr/bin/env python3
"""
Main entry point for the Buddhist Digital Library API
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import categories, subcategories, news, audio, videos, auth, editions, texts, users
from app.routers.lookups import sermons, translation_types, yanas

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
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(subcategories.router)
app.include_router(texts.router)
app.include_router(news.router)
app.include_router(audio.router)
app.include_router(videos.router)
app.include_router(editions.router)
app.include_router(users.router)
app.include_router(sermons.router)
app.include_router(translation_types.router)
app.include_router(yanas.router)

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