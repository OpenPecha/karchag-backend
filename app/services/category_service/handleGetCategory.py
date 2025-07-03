from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.models import MainCategory

async def handle_get_category(category_id: int,
                           lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
                          db: Session = Depends(get_db)):
    """Get a main category by ID"""
    db_category = db.query(MainCategory).options(
        joinedload(MainCategory.sub_categories)
    ).filter(MainCategory.id == category_id).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Transform data based on language preference
    category_data = {
        "id": db_category.id,
        "name": db_category.name_english if lang != "tb" else db_category.name_tibetan,
        "description": db_category.description_english if lang != "tb" else db_category.description_tibetan,
        "order_index": db_category.order_index,
        "is_active": db_category.is_active,
        "created_at": db_category.created_at,
        "updated_at": db_category.updated_at,
        "sub_categories": [
            {
                "id": sub.id,
                "name": sub.name_english if lang != "tb" else sub.name_tibetan,
                "description": sub.description_english if lang != "tb" else sub.description_tibetan,
                "main_category_id": getattr(sub, 'main_category_id', category_id),  # Use category_id as fallback
                "order_index": getattr(sub, 'order_index', 0),  # Default to 0
                "is_active": sub.is_active,
                "created_at": getattr(sub, 'created_at', db_category.created_at),  # Use parent's timestamp as fallback
                "updated_at": getattr(sub, 'updated_at', db_category.updated_at)   # Use parent's timestamp as fallback
            } for sub in db_category.sub_categories
        ]
    }
    
    return category_data