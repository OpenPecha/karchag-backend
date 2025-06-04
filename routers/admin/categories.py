from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import MainCategory, SubCategory
from schemas import MainCategoryResponse, SubCategoryResponse, MainCategoryCreate, SubCategoryCreate

router = APIRouter( tags=["Admin - Categories"])

@router.get("/categories", response_model=List[MainCategoryResponse])
async def get_all_categories(db: Session = Depends(get_db)):
    """Get all main categories (including inactive)"""
    categories = db.query(MainCategory).order_by(MainCategory.order_index).all()
    return categories

@router.post("/categories", response_model=MainCategoryResponse, status_code=201)
async def create_category(
    category_data: MainCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new main category"""
    db_category = MainCategory(**category_data.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=MainCategoryResponse)
async def update_category(
    category_id: int,
    category_data: MainCategoryCreate,
    db: Session = Depends(get_db)
):
    """Update a main category"""
    db_category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for field, value in category_data.model_dump().items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a main category"""
    db_category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

@router.get("/categories/{category_id}/subcategories", response_model=List[SubCategoryResponse])
async def get_subcategories(category_id: int, db: Session = Depends(get_db)):
    """Get sub-categories under specific main category"""
    # Verify category exists
    if not db.query(MainCategory).filter(MainCategory.id == category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    
    subcategories = db.query(SubCategory).filter(
        SubCategory.main_category_id == category_id
    ).order_by(SubCategory.order_index).all()
    
    return subcategories

@router.post("/categories/{category_id}/subcategories", response_model=SubCategoryResponse, status_code=201)
async def create_subcategory(
    category_id: int,
    subcategory_data: SubCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new sub-category"""
    # Verify category exists
    if not db.query(MainCategory).filter(MainCategory.id == category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_subcategory = SubCategory(**subcategory_data.model_dump(), main_category_id=category_id)
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

@router.put("/categories/{category_id}/subcategories/{sub_category_id}", response_model=SubCategoryResponse)
async def update_subcategory(
    category_id: int,
    sub_category_id: int,
    subcategory_data: SubCategoryCreate,
    db: Session = Depends(get_db)
):
    """Update a sub-category"""
    db_subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    for field, value in subcategory_data.model_dump().items():
        setattr(db_subcategory, field, value)
    
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

@router.delete("/categories/{category_id}/subcategories/{sub_category_id}")
async def delete_subcategory(
    category_id: int,
    sub_category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a sub-category"""
    db_subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    db.delete(db_subcategory)
    db.commit()
    return {"message": "Sub-category deleted successfully"}