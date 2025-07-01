from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import MainCategory,User
from schemas import (MainCategoryResponse, MainCategoryWithSubCategories, MainCategoryLanguageResponse, MainCategoryCreate, MainCategoryUpdate)
from dependencies.auth import require_admin
from services.category_service.getCategoriesHandler import handle_get_categories
from services.category_service.getAllCategorieshandler import handle_get_all_categories
from services.category_service.handleGetCategory import handle_get_category
from services.category_service.handleCreateCategory import handle_create_category
from services.category_service.handleUpdateCategory import handle_update_category
from services.category_service.handleDeleteCategory import handle_delete_category
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
    return await handle_get_all_categories(admin_user, lang, db)

@router.get("/{category_id}", response_model=MainCategoryWithSubCategories)
async def get_category(category_id: int, 
                          lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
                          db: Session = Depends(get_db)):
    return await handle_get_category(category_id, lang, db)

# POST Endpoint - Create new category
@router.post("/", response_model=MainCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: MainCategoryCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create a new main category - Admin only"""
    return await handle_create_category(category_data, current_user, db)

# PUT Endpoint - Update existing category
@router.put("/{category_id}", response_model=MainCategoryResponse)
async def update_category(
    category_id: int,
    category_data: MainCategoryUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update an existing main category - Admin only"""
    return await handle_update_category(category_id, category_data, current_user, db)

# DELETE Endpoint - Delete category
@router.delete("/{category_id}")
async def delete_category(
    category_id: int, 
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete a main category - Admin only"""
    return await handle_delete_category(category_id, current_user, db)