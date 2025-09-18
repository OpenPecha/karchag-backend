from sqlalchemy.orm import Session
from app.models import Edition, User
from app.schemas import EditionCreate

async def handle_create_edition(edition_data: EditionCreate, current_user: User, db: Session):
    edition = Edition(
        name_english=edition_data.name_english,
        name_tibetan=edition_data.name_tibetan,
        description_english=edition_data.description_english,
        description_tibetan=edition_data.description_tibetan,
        abbreviation=edition_data.abbreviation,
        publisher=edition_data.publisher,
        publication_year=edition_data.publication_year,
        location=edition_data.location,
        total_volumes=edition_data.total_volumes,
        order_index=edition_data.order_index,
        is_active=edition_data.is_active
    )
    db.add(edition)
    db.commit()
    db.refresh(edition)
    return edition 