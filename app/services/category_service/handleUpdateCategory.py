from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import MainCategory, User
from app.schemas import MainCategoryUpdate, MainCategoryResponse

async def handle_update_category(
    category_id: int,
    category_data: MainCategoryUpdate,
    current_user: User,  # Admin user passed from router
    db: Session
) -> MainCategoryResponse:
    """Update an existing main category - Admin only"""
    
    # Check if category exists
    db_category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    # Check if name is being updated and if it conflicts with existing category
    if category_data.name_english and category_data.name_english != db_category.name_english:
        existing_category = db.query(MainCategory).filter(
            MainCategory.name_english == category_data.name_english,
            MainCategory.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Category with this name already exists"
            )
    
    # Update category fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category 