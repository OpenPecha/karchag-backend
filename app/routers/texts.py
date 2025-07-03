from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import  Optional
from app.database import get_db
from app.models import KagyurText,  YesheDESpan, User, SubCategory
from app.schemas import (
    KagyurTextResponse,  KagyurTextUpdate,KagyurTextCreateRequest,TextsListResponse, 
)
from app.dependencies.auth import require_admin
from app.services.text_service.handleGetAllTexts import handle_get_all_texts
from app.services.text_service.handleFetchTexts import handle_fetch_texts
from app.services.text_service.handleCreateText import handle_create_text
from app.services.text_service.handlePutText import handle_put_text
from app.services.text_service.handleDeleteText import handle_delete_text
from app.services.text_service.handleBulkImportTexts import handle_bulk_import_texts

router = APIRouter( prefix="", tags=[" Texts"])

@router.get("/texts", response_model=TextsListResponse)
async def get_all_texts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in titles"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # Admin only
):
    return await handle_get_all_texts(admin_user=admin_user, page=page, limit=limit, search=search, db=db)

@router.get("/texts/{text_id}", response_model=KagyurTextResponse)
async def get_text(text_id: int, db: Session = Depends(get_db)):
    """Get complete text data for editing"""
    
    text = db.query(KagyurText).options(
        joinedload(KagyurText.text_summary),
        joinedload(KagyurText.sermon),
        joinedload(KagyurText.yana),
        joinedload(KagyurText.translation_type),
        joinedload(KagyurText.yeshe_de_spans).joinedload(YesheDESpan.volumes),
        joinedload(KagyurText.sub_category)
    ).filter(KagyurText.id == text_id).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    return text

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts/",
            response_model=TextsListResponse, tags=["Texts"])
async def fetch_text(
    category_id: int,
    sub_category_id: int,
    lang: Optional[str] = Query(None, regex="^(en|tb)$", description="Language preference: en or tb"),
    db: Session = Depends(get_db)
):
    return await handle_fetch_texts(category_id=category_id, sub_category_id=sub_category_id, db=db)


@router.post(
    "/categories/{category_id}/subcategories/{sub_category_id}/texts",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new text",
    description="Create a new Kagyur text with all related data including summaries and Yeshe De spans"
)
def create_new_text(
    category_id: int,
    sub_category_id: int,
    text_data: KagyurTextCreateRequest,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """
    Create a new text in the specified category and subcategory.
    
    - **category_id**: ID of the main category
    - **sub_category_id**: ID of the subcategory
    - **text_data**: Text data including optional summary and Yeshe De spans
    """
    return handle_create_text(
        category_id=category_id,
        sub_category_id=sub_category_id,
        text_data=text_data,
        current_user=current_user,
        db=db
    )
    

@router.put("/texts/{text_id}", response_model=dict)
async def update_text(
    text_id: int,
    text_data: KagyurTextUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    return await handle_put_text(text_id=text_id, text_data=text_data, current_user=current_user, db=db)

@router.delete("/texts/{text_id}")
async def delete_text(
    text_id: int, 
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete a text - Admin only"""
    return await handle_delete_text(text_id=text_id, current_user=current_user, db=db)

@router.post("/texts/bulk-import")
async def bulk_import_texts(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Bulk import texts from CSV/JSON file - Admin only"""
    return await handle_bulk_import_texts(file=file, current_user=current_user, db=db)