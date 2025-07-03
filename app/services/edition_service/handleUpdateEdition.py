from sqlalchemy.orm import Session
from app.models import Edition, User
from app.schemas import EditionUpdate
from fastapi import HTTPException

async def handle_update_edition(edition_id: int, edition_data: EditionUpdate, current_user: User, db: Session):
    edition = db.query(Edition).filter(Edition.id == edition_id).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    update_data = edition_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(edition, field, value)
    db.commit()
    db.refresh(edition)
    return edition 