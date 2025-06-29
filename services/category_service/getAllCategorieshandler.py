from fastapi import Depends, Query
from sqlalchemy.orm import Session
from typing import  Optional
from database import get_db
from models import MainCategory,User
from dependencies.auth import require_admin

async def handle_get_all_categories(
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # Admin only for inactive categories
):
    """Get all main categories (including inactive) - Admin only"""
    categories = db.query(MainCategory).order_by(MainCategory.order_index).all()
    
    # Transform data based on language preference
    result = []
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name_english if lang != "tb" else category.name_tibetan,
            "description": category.description_english if lang != "tb" else category.description_tibetan,
            "order_index": category.order_index,
            "is_active": category.is_active,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }
        result.append(category_data)
    return result
    
