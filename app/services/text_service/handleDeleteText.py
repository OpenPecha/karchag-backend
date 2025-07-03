from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import KagyurText, User

async def handle_delete_text(
    text_id: int,
    current_user: User,  # Admin user passed from router
    db: Session
) -> dict:
    """Delete a text - Admin only"""
    
    # Check if text exists
    db_text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not db_text:
        raise HTTPException(
            status_code=404,
            detail="Text not found"
        )
    
    # Delete the text
    db.delete(db_text)
    db.commit()
    
    return {"message": "Text deleted successfully"} 