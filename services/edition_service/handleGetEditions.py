from sqlalchemy.orm import Session
from models import Edition
from schemas import EditionResponse
from typing import Optional, List

async def handle_get_editions(lang: Optional[str], db: Session) -> list:
    editions = db.query(Edition).filter(
        Edition.is_active == True
    ).order_by(Edition.order_index).all()
    return editions 