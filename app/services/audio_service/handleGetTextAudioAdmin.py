from sqlalchemy.orm import Session
from app.models import KagyurText, KagyurAudio, User
from fastapi import HTTPException

async def handle_get_text_audio_admin(text_id: int, current_user: User, db: Session) -> dict:
    text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    audio_files = db.query(KagyurAudio).filter(
        KagyurAudio.text_id == text_id,
        KagyurAudio.is_active == True
    ).order_by(KagyurAudio.order_index).all()
    return {
        "text": text,
        "audio_files": audio_files
    } 