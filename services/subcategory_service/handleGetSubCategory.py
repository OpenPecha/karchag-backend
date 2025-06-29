from fastapi import  Depends, HTTPException,  Query
from sqlalchemy.orm import Session ,joinedload
from typing import  Optional
from database import get_db
from models import  SubCategory

async def handle_get_subcategory(
    subcategory_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific sub-category by ID.
    
    Args:
        subcategory_id: The ID of the sub-category
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        Sub-category with complete info
    
    Raises:
        HTTPException: 404 if sub-category not found
    """
    # Get subcategory with main category info
    subcategory = db.query(SubCategory).options(
        joinedload(SubCategory.main_category)
    ).filter(
        SubCategory.id == subcategory_id,
        SubCategory.is_active == True
    ).first()
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    # Transform data based on language preference
    subcategory_data = {
        "id": subcategory.id,
        "name": subcategory.name_english if lang != "tb" else subcategory.name_tibetan,
        "description": subcategory.description_english if lang != "tb" else subcategory.description_tibetan,
        "main_category_id": subcategory.main_category_id,
        "main_category": {
            "id": subcategory.main_category.id,
            "name": subcategory.main_category.name_english if lang != "tb" else subcategory.main_category.name_tibetan,
            "description": subcategory.main_category.description_english if lang != "tb" else subcategory.main_category.description_tibetan,
        } if subcategory.main_category else None,
        "order_index": subcategory.order_index,
        "is_active": subcategory.is_active,
        "created_at": subcategory.created_at,
        "updated_at": subcategory.updated_at
    }
    
    return subcategory_data