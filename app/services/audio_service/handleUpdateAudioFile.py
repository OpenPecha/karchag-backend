from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil
from pathlib import Path
from app.models import KagyurAudio, User


async def handle_update_audio_file(
    audio_id: int,
    audio_file: UploadFile,
    current_user: User = None,
    db: Session = None
):
    """Update audio file"""
    
    # Get the audio record
    audio = db.query(KagyurAudio).filter(KagyurAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found"
        )
    
    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only audio files are allowed."
        )
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/audio")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate file path
        file_extension = Path(audio_file.filename).suffix if audio_file.filename else '.mp3'
        file_name = f"audio_{audio_id}_{int(datetime.now().timestamp())}{file_extension}"
        file_path = upload_dir / file_name
        
        # Save the new file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Remove old file if it exists
        if audio.audio_file_path and os.path.exists(audio.audio_file_path):
            try:
                os.remove(audio.audio_file_path)
            except OSError:
                pass  # File might not exist or be in use
        
        # Update the database record
        audio.audio_file_path = str(file_path)
        audio.file_size = os.path.getsize(file_path)
        audio.updated_at = datetime.now()
        
        db.commit()
        db.refresh(audio)
        
        return {
            "message": "Audio file updated successfully",
            "audio": audio,
            "file_path": str(file_path),
            "file_size": audio.file_size
        }
        
    except Exception as e:
        db.rollback()
        # Clean up the uploaded file if database update fails
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update audio file: {str(e)}"
        )
