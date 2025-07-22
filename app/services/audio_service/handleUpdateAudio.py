from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import KagyurAudio, User
from typing import Optional


async def handle_update_audio(
    audio_id: int,
    narrator_name_english: Optional[str] = None,
    narrator_name_tibetan: Optional[str] = None,
    audio_quality: Optional[str] = None,
    audio_language: Optional[str] = None,
    order_index: Optional[int] = None,
    current_user: User = None,
    db: Session = None
):
    """Update audio metadata"""
    
    # Get the audio record
    audio = db.query(KagyurAudio).filter(KagyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found"
        )
    
    # Update fields if provided
    if narrator_name_english is not None:
        audio.narrator_name_english = narrator_name_english
    
    if narrator_name_tibetan is not None:
        audio.narrator_name_tibetan = narrator_name_tibetan
    
    if audio_quality is not None:
        audio.audio_quality = audio_quality
    
    if audio_language is not None:
        audio.audio_language = audio_language
    
    if order_index is not None:
        audio.order_index = order_index
    
    # Update timestamp
    audio.updated_at = datetime.now()
    
    try:
        db.commit()
        db.refresh(audio)
        return audio
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update audio: {str(e)}"
        )
