from sqlalchemy.orm import Session
from models import KagyurAudio, User
from fastapi import HTTPException
import os
from typing import Any

async def handle_delete_audio(audio_id: int, current_user: User, db: Session) -> dict:
    audio = db.query(KagyurAudio).filter(KagyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    try:
        audio_url = getattr(audio, 'audio_url', None)
        if audio_url and isinstance(audio_url, str):
            file_path = audio_url[1:] if audio_url.startswith('/') else audio_url
            if os.path.exists(str(file_path)):
                os.remove(str(file_path))
    except (AttributeError, TypeError, OSError):
        pass
    db.delete(audio)
    db.commit()
    return {"message": "Audio deleted successfully"} 