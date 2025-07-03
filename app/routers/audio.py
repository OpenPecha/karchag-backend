from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import KagyurAudio, User
from app.schemas import AudioResponse
from app.dependencies.auth import require_admin
from app.services.audio_service.handleGetAudioDetails import handle_get_audio_details
from app.services.audio_service.handleGetAudioCategories import handle_get_audio_categories
from app.services.audio_service.handleGetTextAudio import handle_get_text_audio
from app.services.audio_service.handleCreateAudio import handle_create_audio
from app.services.audio_service.handleDeleteAudio import handle_delete_audio

router = APIRouter(tags=["audio"])

# GET /audio
@router.get("/audio")
async def list_audio(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    narrator: Optional[str] = Query(None),
    quality: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List audio files with optional filters (public)"""
    query = db.query(KagyurAudio)
    if narrator:
        query = query.filter(
            KagyurAudio.narrator_name_english.ilike(f"%{narrator}%") |
            KagyurAudio.narrator_name_tibetan.ilike(f"%{narrator}%")
        )
    if language:
        query = query.filter(KagyurAudio.audio_language == language)
    if search:
        query = query.filter(
            KagyurAudio.narrator_name_english.ilike(f"%{search}%")
        )
    total = query.count()
    audio_files = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "audio_files": audio_files,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# GET /audio/{audio_id}
@router.get("/audio/{audio_id}")
async def get_audio(audio_id: int, lang: Optional[str] = Query("en", regex="^(en|tb)$"), db: Session = Depends(get_db)):
    """Get audio file details (public)"""
    return await handle_get_audio_details(audio_id=audio_id, lang=lang, db=db)

# GET /texts/{category_id}/{sub_category_id}/{text_id}/audio
@router.get("/texts/{category_id}/{sub_category_id}/{text_id}/audio")
async def get_text_audio(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    quality: Optional[str] = Query(None, regex="^(128kbps|320kbps)$"),
    db: Session = Depends(get_db)
):
    """Get all audio files for a specific text (public)"""
    return await handle_get_text_audio(category_id=category_id, sub_category_id=sub_category_id, text_id=text_id, lang=lang, quality=quality, db=db)

# GET /audio/categories
@router.get("/audio/categories")
async def list_audio_categories(lang: Optional[str] = Query("en", regex="^(en|tb)$"), db: Session = Depends(get_db)):
    """List audio categories (public)"""
    return await handle_get_audio_categories(lang=lang, db=db)

# POST /audio (admin only)
@router.post("/audio", response_model=AudioResponse, status_code=status.HTTP_201_CREATED)
async def create_audio(
    text_id: int = Form(...),
    audio_file: UploadFile = File(...),
    narrator_name_english: str = Form(...),
    narrator_name_tibetan: str = Form(""),
    audio_quality: str = Form("standard"),
    audio_language: str = Form("tibetan"),
    order_index: int = Form(0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new audio record (admin only)"""
    return await handle_create_audio(
        text_id=text_id,
        audio_file=audio_file,
        narrator_name_english=narrator_name_english,
        narrator_name_tibetan=narrator_name_tibetan,
        audio_quality=audio_quality,
        audio_language=audio_language,
        order_index=order_index,
        current_user=current_user,
        db=db
    )

# DELETE /audio/{audio_id} (admin only)
@router.delete("/audio/{audio_id}")
async def delete_audio(
    audio_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete audio file (admin only)"""
    return await handle_delete_audio(audio_id=audio_id, current_user=current_user, db=db)