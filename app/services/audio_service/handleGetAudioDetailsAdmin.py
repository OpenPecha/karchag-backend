from sqlalchemy.orm import Session
from models import KagyurAudio, User
from fastapi import HTTPException

async def handle_get_audio_details_admin(audio_id: int, current_user: User, db: Session):
    audio = db.query(KagyurAudio).filter(KagyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio 