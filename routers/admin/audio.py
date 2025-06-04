from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from datetime import datetime

from database import get_db
from models import KangyurAudio, KagyurText
from schemas import AudioResponse, AudioCreate, AudioUpdate

router = APIRouter(
    tags=["Audio Management"]
)

@router.get("/audio")
async def get_all_audio(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    text_id: Optional[int] = Query(None),
    narrator: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all audio files with text information"""
    query = db.query(KangyurAudio).join(KagyurText)
    
    # Apply filters
    if text_id:
        query = query.filter(KangyurAudio.text_id == text_id)
    if narrator:
        query = query.filter(
            KangyurAudio.narrator_name_english.ilike(f"%{narrator}%") |
            KangyurAudio.narrator_name_tibetan.ilike(f"%{narrator}%")
        )
    if language:
        query = query.filter(KangyurAudio.audio_language == language)
    if search:
        query = query.filter(
            KagyurText.english_title.ilike(f"%{search}%") |
            KagyurText.tibetan_title.ilike(f"%{search}%") |
            KangyurAudio.narrator_name_english.ilike(f"%{search}%")
        )
    
    # Pagination
    total = query.count()
    audio_files = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "audio_files": audio_files,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/texts/{text_id}/audio")
async def get_text_audio(
    text_id: int,
    db: Session = Depends(get_db)
):
    """Get audio files for specific text"""
    text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    audio_files = db.query(KangyurAudio).filter(
        KangyurAudio.text_id == text_id,
        KangyurAudio.is_active == True
    ).order_by(KangyurAudio.order_index).all()
    
    return {
        "text": text,
        "audio_files": audio_files
    }

@router.get("/audio/{audio_id}")
async def get_audio_details(
    audio_id: int,
    db: Session = Depends(get_db)
):
    """Get specific audio details for editing"""
    audio = db.query(KangyurAudio).filter(KangyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return audio

@router.post("/texts/{text_id}/audio")
async def create_audio(
    text_id: int,
    audio_file: UploadFile = File(...),
    narrator_name_english: str = Form(...),
    narrator_name_tibetan: str = Form(""),
    audio_quality: str = Form("standard"),
    audio_language: str = Form("tibetan"),
    order_index: int = Form(0),
    db: Session = Depends(get_db)
):
    """Create new audio record with file upload"""
    # Verify text exists
    text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Validate file type
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Save audio file
    upload_dir = f"uploads/audio/{text_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = audio_file.filename.split('.')[-1]
    filename = f"{datetime.now().timestamp()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Create audio record
    audio_data = KangyurAudio(
        text_id=text_id,
        audio_url=f"/uploads/audio/{text_id}/{filename}",
        file_name=audio_file.filename,
        file_size=len(content),
        narrator_name_english=narrator_name_english,
        narrator_name_tibetan=narrator_name_tibetan,
        audio_quality=audio_quality,
        audio_language=audio_language,
        order_index=order_index,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(audio_data)
    db.commit()
    db.refresh(audio_data)
    
    return audio_data

@router.put("/audio/{audio_id}")
async def update_audio_metadata(
    audio_id: int,
    audio_update: AudioUpdate,
    db: Session = Depends(get_db)
):
    """Update audio metadata (without file)"""
    audio = db.query(KangyurAudio).filter(KangyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    # Update fields
    for field, value in audio_update.dict(exclude_unset=True).items():
        setattr(audio, field, value)
    
    audio.updated_at = datetime.now()
    db.commit()
    db.refresh(audio)
    
    return audio

@router.put("/audio/{audio_id}/file")
async def update_audio_file(
    audio_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Update audio file"""
    audio = db.query(KangyurAudio).filter(KangyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    # Validate file type
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Delete old file if exists
    if audio.audio_url and os.path.exists(audio.audio_url[1:]):  # Remove leading slash
        os.remove(audio.audio_url[1:])
    
    # Save new audio file
    upload_dir = f"uploads/audio/{audio.text_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = audio_file.filename.split('.')[-1]
    filename = f"{datetime.now().timestamp()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Update audio record
    audio.audio_url = f"/uploads/audio/{audio.text_id}/{filename}"
    audio.file_name = audio_file.filename
    audio.file_size = len(content)
    audio.updated_at = datetime.now()
    
    db.commit()
    db.refresh(audio)
    
    return audio

@router.delete("/audio/{audio_id}")
async def delete_audio(
    audio_id: int,
    db: Session = Depends(get_db)
):
    """Delete audio file and record"""
    audio = db.query(KangyurAudio).filter(KangyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    # Delete file if exists
    if audio.audio_url and os.path.exists(audio.audio_url[1:]):  # Remove leading slash
        os.remove(audio.audio_url[1:])
    
    db.delete(audio)
    db.commit()
    
    return {"message": "Audio deleted successfully"}