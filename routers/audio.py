from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from database import get_db
from models import MainCategory, SubCategory, KagyurAudio, KagyurText, User
from schemas import MainCategoryResponse, SubCategoryResponse, AudioResponse, PaginatedResponse
from dependencies.auth import require_admin
import math
import os
from datetime import datetime
from services.audio_service.handleGetAudioCategories import handle_get_audio_categories
from services.audio_service.handleGetAudioSubcategories import handle_get_audio_subcategories
from services.audio_service.handleGetSubcategoryAudio import handle_get_subcategory_audio
from services.audio_service.handleGetSpecificAudio import handle_get_specific_audio
from services.audio_service.handleGetTextAudio import handle_get_text_audio
from services.audio_service.handleGetAudioDetails import handle_get_audio_details
from services.audio_service.handleGetAllAudioAdmin import handle_get_all_audio_admin
from services.audio_service.handleGetTextAudioAdmin import handle_get_text_audio_admin
from services.audio_service.handleGetAudioDetailsAdmin import handle_get_audio_details_admin
from services.audio_service.handleDeleteAudio import handle_delete_audio

router = APIRouter(tags=["audio"])

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/categories")
async def get_audio_categories(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active main categories that have audio content"""
    return await handle_get_audio_categories(lang=lang, db=db)

@router.get("/categories/{category_id}/subcategories")
async def get_audio_subcategories(
    category_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get sub-categories under specific category that have audio content"""
    return await handle_get_audio_subcategories(category_id=category_id, lang=lang, db=db)

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/audio")
async def get_subcategory_audio(
    category_id: int,
    sub_category_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    narrator: Optional[str] = Query(None),
    quality: Optional[str] = Query(None),
    language: Optional[str] = Query(None, regex="^(tibetan|english)$"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all audio files under a specific sub-category"""
    return await handle_get_subcategory_audio(category_id=category_id, sub_category_id=sub_category_id, page=page, limit=limit, narrator=narrator, quality=quality, language=language, lang=lang, db=db)

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/audio/{audio_id}")
async def get_specific_audio(
    category_id: int,
    sub_category_id: int,
    audio_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific audio details and streaming URL"""
    return await handle_get_specific_audio(category_id=category_id, sub_category_id=sub_category_id, audio_id=audio_id, lang=lang, db=db)

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts/{text_id}/audio", tags=["Audio"])
async def get_text_audio(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    quality: Optional[str] = Query(None, regex="^(128kbps|320kbps)$"),
    db: Session = Depends(get_db)
):
    """Get all audio files for a specific text"""
    return await handle_get_text_audio(category_id=category_id, sub_category_id=sub_category_id, text_id=text_id, lang=lang, quality=quality, db=db)

@router.get("/audio/{audio_id}", tags=["Audio"])
async def get_audio_details(
    audio_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific audio file details and streaming URL"""
    return await handle_get_audio_details(audio_id=audio_id, lang=lang, db=db)

# ==================== ADMIN ENDPOINTS ====================

@router.get("/audio", tags=["Audio Management"])
async def get_all_audio_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    text_id: Optional[int] = Query(None),
    narrator: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all audio files with text information - Admin only"""
    return await handle_get_all_audio_admin(current_user=current_user, db=db, page=page, limit=limit, text_id=text_id, narrator=narrator, language=language, search=search)

@router.get("/texts/{text_id}/audio", tags=["Audio Management"])
async def get_text_audio_admin(
    text_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get audio files for specific text - Admin only"""
    return await handle_get_text_audio_admin(text_id=text_id, current_user=current_user, db=db)

@router.get("/audio/{audio_id}/details", tags=["Audio Management"])
async def get_audio_details_admin(
    audio_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific audio details for editing - Admin only"""
    return await handle_get_audio_details_admin(audio_id=audio_id, current_user=current_user, db=db)

@router.post("/texts/{text_id}/audio", tags=["Audio Management"])
async def create_audio(
    text_id: int,
    audio_file: UploadFile = File(...),
    narrator_name_english: str = Form(...),
    narrator_name_tibetan: str = Form(""),
    audio_quality: str = Form("standard"),
    audio_language: str = Form("tibetan"),
    order_index: int = Form(0),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new audio record with file upload - Admin only"""
    # Verify text exists
    text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Save audio file
    upload_dir = f"uploads/audio/{text_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = audio_file.filename.split('.')[-1] if audio_file.filename else "mp3"
    filename = f"{datetime.now().timestamp()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Create audio record
    audio_data = KagyurAudio(
        text_id=text_id,
        audio_url=f"/uploads/audio/{text_id}/{filename}",
        file_name=audio_file.filename or filename,
        file_size=len(content),
        narrator_name_english=narrator_name_english,
        narrator_name_tibetan=narrator_name_tibetan,
        audio_quality=audio_quality,
        audio_language=audio_language,
        order_index=order_index,
        is_active=True
    )
    
    db.add(audio_data)
    db.commit()
    db.refresh(audio_data)
    
    return audio_data

@router.delete("/audio/{audio_id}", tags=["Audio Management"])
async def delete_audio(
    audio_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete audio file - Admin only"""
    return await handle_delete_audio(audio_id=audio_id, current_user=current_user, db=db)