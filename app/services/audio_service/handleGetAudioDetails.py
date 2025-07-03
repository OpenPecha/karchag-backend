from sqlalchemy.orm import Session
from app.models import KagyurAudio
from app.schemas import AudioResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_audio_details(audio_id: int, lang: Optional[str], db: Session) -> AudioResponse:
    audio = db.query(KagyurAudio).filter(
        KagyurAudio.id == audio_id,
        KagyurAudio.is_active == True
    ).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return AudioResponse.from_orm(audio) 