from sqlalchemy.orm import Session
from models import Edition, User

async def handle_get_all_editions_admin(current_user: User, db: Session) -> dict:
    editions = db.query(Edition).order_by(Edition.order_index).all()
    return {"editions": editions} 