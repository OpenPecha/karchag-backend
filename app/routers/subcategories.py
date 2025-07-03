from fastapi import APIRouter, Depends, HTTPException,  Query
from sqlalchemy.orm import Session  
from typing import List, Optional
from app.database import get_db
from app.models import MainCategory, SubCategory,User
from app.schemas import ( SubCategoryUpdate,SubCategoryLanguageResponse,SubCategoryResponse,SubCategoryCreateRequest )
from app.dependencies.auth import require_admin
from app.services.subcategory_service.handleGetSubcategories import handle_get_subcategories
from app.services.subcategory_service.handleGetSubCategory import handle_get_subcategory
import logging

router = APIRouter( tags=["Sub-Categories"])
logger = logging.getLogger(__name__)

    
@router.get("/categories/{category_id}/subcategories", response_model=List[SubCategoryLanguageResponse])
async def get_subcategories(
    category_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    return await handle_get_subcategories(category_id, lang, db)
    
@router.get("/categories/{category_id}/subcategories/{subcategory_id}", response_model=SubCategoryLanguageResponse)
async def get_subcategory(
    category_id: int,
    subcategory_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):  
    return await handle_get_subcategory(subcategory_id, lang, db)

@router.post("/categories/{category_id}/subcategories", response_model=SubCategoryResponse, status_code=201)
async def create_subcategory(
    category_id: int,
    subcategory_data: SubCategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new sub-category"""
    # Verify category exists
    if not db.query(MainCategory).filter(MainCategory.id == category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    
    subcategory_dict = subcategory_data.model_dump()
    subcategory_dict['main_category_id'] = category_id
    db_subcategory = SubCategory(**subcategory_dict)
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

@router.put("/categories/{category_id}/subcategories/{sub_category_id}", response_model=SubCategoryResponse)
async def update_subcategory(
    category_id: int,
    sub_category_id: int,
    subcategory_data: SubCategoryUpdate,  # Changed from SubCategoryCreate
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a sub-category"""
    db_subcategory = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    # Update only the fields from SubCategoryUpdate (excludes main_category_id)
    for field, value in subcategory_data.model_dump(exclude_unset=True).items():
        setattr(db_subcategory, field, value)
    
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory


@router.delete("/categories/{category_id}/subcategories/{sub_category_id}")
async def delete_subcategory(
    category_id: int,
    sub_category_id: int,
    current_user: User = Depends(require_admin),
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
