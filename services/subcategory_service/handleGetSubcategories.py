from fastapi import  Depends, HTTPException,  Query
from sqlalchemy.orm import Session 
from typing import Optional
from database import get_db
from models import MainCategory, SubCategory

async def handle_get_subcategories(
    category_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all sub-categories under a specific main category.
    
    Args:
        category_id: The ID of the main category
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        List of sub-categories with their basic info
    
    Raises:
        HTTPException: 404 if main category not found
    """
    # Verify main category exists
    category = db.query(MainCategory).filter(
        MainCategory.id == category_id,
        MainCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    sub_categories = db.query(SubCategory).filter(
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).order_by(SubCategory.order_index).all()
    
    subcategories_data = [
        {
            "id": sub.id,
            "name": sub.name_english if lang != "tb" else sub.name_tibetan,
            "description": sub.description_english if lang != "tb" else sub.description_tibetan,
            "main_category_id": sub.main_category_id,
            "order_index": sub.order_index,
            "is_active": sub.is_active,
            "created_at": sub.created_at,
            "updated_at": sub.updated_at
        }
        for sub in sub_categories
    ]
    return subcategories_data