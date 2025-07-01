from sqlalchemy.orm import Session
from models import KagyurAudio, KagyurText, SubCategory
from schemas import AudioResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_specific_audio(category_id: int, sub_category_id: int, audio_id: int, lang: Optional[str], db: Session) -> AudioResponse:
    audio = db.query(KagyurAudio).join(KagyurText).join(SubCategory).filter(
        KagyurAudio.id == audio_id,
        KagyurText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id,
        KagyurAudio.is_active == True
    ).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return AudioResponse.from_orm(audio) 