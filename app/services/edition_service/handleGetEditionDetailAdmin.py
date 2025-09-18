from sqlalchemy.orm import Session
from app.models import Edition, User
from fastapi import HTTPException

async def handle_get_edition_detail_admin(edition_id: int, current_user: User, db: Session):
    edition = db.query(Edition).filter(Edition.id == edition_id).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    return edition 