from sqlalchemy.orm import Session
from app.models import Edition
from app.schemas import EditionResponse
from typing import Optional
from fastapi import HTTPException

async def handle_get_edition_detail(edition_id: int, lang: Optional[str], db: Session) -> EditionResponse:
    edition = db.query(Edition).filter(
        Edition.id == edition_id,
        Edition.is_active == True
    ).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    return edition 