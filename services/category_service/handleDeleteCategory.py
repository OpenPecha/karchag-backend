from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import MainCategory, User

async def handle_delete_category(
    category_id: int,
    current_user: User,  # Admin user passed from router
    db: Session
) -> dict:
    """Delete a main category - Admin only"""
    
    # Check if category exists
    db_category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    # Check if category has sub-categories (optional validation)
    sub_categories_count = db.query(MainCategory).filter(
        MainCategory.id == category_id
    ).first()
    
    if sub_categories_count and hasattr(sub_categories_count, 'sub_categories') and len(sub_categories_count.sub_categories) > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category that has sub-categories. Please delete sub-categories first."
        )
    
    # Delete the category
    db.delete(db_category)
    db.commit()
    
    return {"message": "Category deleted successfully"} 