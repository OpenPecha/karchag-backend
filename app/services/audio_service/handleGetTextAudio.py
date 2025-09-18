from sqlalchemy.orm import Session
from app.models import KagyurText, SubCategory, KagyurAudio
from app.schemas import AudioResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_text_audio(category_id: int, sub_category_id: int, text_id: int, lang: Optional[str], quality: Optional[str], db: Session) -> dict:
    text = db.query(KagyurText).filter(
        KagyurText.id == text_id,
        KagyurText.sub_category_id == sub_category_id
    ).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Invalid category/subcategory combination")
    query = db.query(KagyurAudio).filter(
        KagyurAudio.text_id == text_id,
        KagyurAudio.is_active == True
    )
    if quality:
        query = query.filter(KagyurAudio.audio_quality == quality)
    audio_files = query.order_by(KagyurAudio.order_index).all()
    return {"audio_files": [AudioResponse.model_validate(audio) for audio in audio_files]} 