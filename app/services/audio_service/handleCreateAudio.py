from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models import KagyurAudio, KagyurText, User
from datetime import datetime
import os

async def handle_create_audio(
    text_id: int,
    audio_file: UploadFile,
    narrator_name_english: str,
    current_user: User,  # Admin user passed from router
    db: Session,
    narrator_name_tibetan: str = "",
    audio_quality: str = "standard",
    audio_language: str = "tibetan",
    order_index: int = 0
) -> KagyurAudio:
    """Create new audio record with file upload - Admin only"""
    
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
    audio_data = KagyurAudio(
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