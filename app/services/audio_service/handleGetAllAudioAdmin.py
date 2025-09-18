from sqlalchemy.orm import Session
from app.models import KagyurAudio, KagyurText, User
from typing import Optional

async def handle_get_all_audio_admin(current_user: User, db: Session, page: int = 1, limit: int = 20, text_id: Optional[int] = None, narrator: Optional[str] = None, language: Optional[str] = None, search: Optional[str] = None) -> dict:
    query = db.query(KagyurAudio).join(KagyurText)
    if text_id:
        query = query.filter(KagyurAudio.text_id == text_id)
    if narrator:
        query = query.filter(
            KagyurAudio.narrator_name_english.ilike(f"%{narrator}%") |
            KagyurAudio.narrator_name_tibetan.ilike(f"%{narrator}%")
        )
    if language:
        query = query.filter(KagyurAudio.audio_language == language)
    if search:
        query = query.filter(
            KagyurText.english_title.ilike(f"%{search}%") |
            KagyurText.tibetan_title.ilike(f"%{search}%") |
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