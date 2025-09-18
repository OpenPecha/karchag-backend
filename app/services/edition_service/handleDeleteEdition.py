from sqlalchemy.orm import Session
from app.models import Edition, User
from fastapi import HTTPException

async def handle_delete_edition(edition_id: int, current_user: User, db: Session) -> dict:
    edition = db.query(Edition).filter(Edition.id == edition_id).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    db.delete(edition)
    db.commit()
    return {"message": "Edition deleted successfully"} 