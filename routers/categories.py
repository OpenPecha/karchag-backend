from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import MainCategory,User
from schemas import (MainCategoryResponse, MainCategoryWithSubCategories, MainCategoryLanguageResponse)
from dependencies.auth import require_admin
from services.category_service.getCategoriesHandler import handle_get_categories
from services.category_service.getAllCategorieshandler import handle_get_all_categories
from services.category_service.handleGetCategory import handle_get_category
import logging


router = APIRouter(prefix="/categories", tags=["Categories"])
logger = logging.getLogger(__name__)

# GET Endpoints
@router.get("/", response_model=List[MainCategoryLanguageResponse], tags=["Categories"])
async def get_categories(
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    
    return await handle_get_categories(lang, db)

@router.get("/all", response_model=List[MainCategoryLanguageResponse])  # Changed path to avoid conflict
async def get_all_categories(
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # Admin only for inactive categories
):
    return await handle_get_all_categories(lang, db, admin_user)

@router.get("/{category_id}", response_model=MainCategoryWithSubCategories)
async def get_category(category_id: int, 
                          lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
                          db: Session = Depends(get_db)):
    return await handle_get_category(category_id, lang, db)

@router.delete("/{category_id}")
async def delete_category(category_id: int, 
                          db: Session = Depends(get_db),
                          current_admin = Depends(require_admin)):
    """Delete a main category"""
    db_category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}