from fastapi import Depends,Query
from sqlalchemy.orm import Session, joinedload
from typing import  Optional
from database import get_db
from models import MainCategory, SubCategory
from dependencies.auth import require_admin

async def handle_get_categories(
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all main categories with their sub-categories.
    
    Args:
        lang: Language preference (en=English, tb=Tibetan)
    
    Returns:
        Hierarchical category structure with all active main categories and their sub-categories
    """
    categories_query = db.query(MainCategory).options(
        joinedload(MainCategory.sub_categories.and_(SubCategory.is_active == True))
    ).filter(
        MainCategory.is_active == True
    )
    
    categories = categories_query.order_by(MainCategory.order_index).all()
    
    # Transform data based on language preference
    result = []
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name_english if lang != "tb" else (category.name_tibetan or category.name_english),
            "description": category.description_english if lang != "tb" else (category.description_tibetan or category.description_english),
            "order_index": category.order_index,
            "is_active": category.is_active,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "sub_categories": []
        }
        
        # Transform sub-categories too
        for sub_cat in category.sub_categories:
            sub_cat_data = {
                "id": sub_cat.id,
                "main_category_id": sub_cat.main_category_id,
                "name": sub_cat.name_english if lang != "tb" else (sub_cat.name_tibetan or sub_cat.name_english),
                "description": sub_cat.description_english if lang != "tb" else (sub_cat.description_tibetan or sub_cat.description_english),
                "order_index": sub_cat.order_index,
                "is_active": sub_cat.is_active,
                "created_at": sub_cat.created_at,
                "updated_at": sub_cat.updated_at
            }
            category_data["sub_categories"].append(sub_cat_data)
        
        result.append(category_data)
    
    return result
