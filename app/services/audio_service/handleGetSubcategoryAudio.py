from sqlalchemy.orm import Session
from sqlalchemy import func
from models import SubCategory, KagyurText, KagyurAudio
from schemas import AudioResponse, PaginatedResponse
from typing import Optional
import math

async def handle_get_subcategory_audio(category_id: int, sub_category_id: int, page: int, limit: int, narrator: Optional[str], quality: Optional[str], language: Optional[str], lang: Optional[str], db: Session) -> PaginatedResponse:
    subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).first()
    if not subcategory:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Subcategory not found")
    offset = (page - 1) * limit
    query = db.query(KagyurAudio).join(KagyurText).filter(
        KagyurText.sub_category_id == sub_category_id,
        KagyurText.is_active == True,
        KagyurAudio.is_active == True
    )
    if narrator:
        query = query.filter(
            (KagyurAudio.narrator_name_english.ilike(f"%{narrator}%")) |
            (KagyurAudio.narrator_name_tibetan.ilike(f"%{narrator}%"))
        )
    if quality:
        query = query.filter(KagyurAudio.audio_quality == quality)
    if language:
        query = query.filter(KagyurAudio.audio_language == language)
    total = query.count()
    audio_files = query.order_by(KagyurAudio.order_index).offset(offset).limit(limit).all()
    return PaginatedResponse(
        items=[AudioResponse.from_orm(audio).dict() for audio in audio_files],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit)
    ) 