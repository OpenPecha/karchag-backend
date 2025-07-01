from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import MainCategory, User
from schemas import MainCategoryCreate, MainCategoryResponse

async def handle_create_category(
    category_data: MainCategoryCreate,
    current_user: User,  # Admin user passed from router
    db: Session
) -> MainCategoryResponse:
    """Create a new main category - Admin only"""
    
    # Check if category with same name already exists
    existing_category = db.query(MainCategory).filter(
        MainCategory.name_english == category_data.name_english
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )
    
    # Create new category
    db_category = MainCategory(
        name_english=category_data.name_english,
        name_tibetan=category_data.name_tibetan,
        description_english=category_data.description_english,
        description_tibetan=category_data.description_tibetan,
        order_index=category_data.order_index,
        is_active=category_data.is_active
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category 