from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import Edition, User
from app.schemas import EditionResponse, EditionCreate, EditionUpdate
from app.dependencies.auth import require_admin
from app.services.edition_service.handleGetEditions import handle_get_editions
from app.services.edition_service.handleGetEditionDetail import handle_get_edition_detail
from app.services.edition_service.handleGetAllEditionsAdmin import handle_get_all_editions_admin
from app.services.edition_service.handleGetEditionDetailAdmin import handle_get_edition_detail_admin
from app.services.edition_service.handleCreateEdition import handle_create_edition
from app.services.edition_service.handleUpdateEdition import handle_update_edition
from app.services.edition_service.handleDeleteEdition import handle_delete_edition

router = APIRouter(tags=["editions"])

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/editions", response_model=List[EditionResponse])
async def get_editions(
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get all active editions"""
    return await handle_get_editions(lang=lang, db=db)

@router.get("/editions/{edition_id}", response_model=EditionResponse)
async def get_edition_detail(
    edition_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$"),
    db: Session = Depends(get_db)
):
    """Get specific edition detail"""
    return await handle_get_edition_detail(edition_id=edition_id, lang=lang, db=db)

# ==================== ADMIN ENDPOINTS ====================

@router.get("/editions/all", tags=["Edition Management"])
async def get_all_editions_admin(
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get all editions (including inactive) - Admin only"""
    return await handle_get_all_editions_admin(current_user=current_user, db=db)

@router.get("/editions/{edition_id}/details", tags=["Edition Management"])
async def get_edition_detail_admin(
    edition_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Get specific edition detail for editing - Admin only"""
    return await handle_get_edition_detail_admin(edition_id=edition_id, current_user=current_user, db=db)

@router.post("/editions", response_model=EditionResponse, status_code=status.HTTP_201_CREATED, tags=["Edition Management"])
async def create_edition(
    edition_data: EditionCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Create new edition - Admin only"""
    return await handle_create_edition(edition_data=edition_data, current_user=current_user, db=db)

@router.put("/editions/{edition_id}", response_model=EditionResponse, tags=["Edition Management"])
async def update_edition(
    edition_id: int,
    edition_data: EditionUpdate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Update edition - Admin only"""
    return await handle_update_edition(edition_id=edition_id, edition_data=edition_data, current_user=current_user, db=db)

@router.delete("/editions/{edition_id}", tags=["Edition Management"])
async def delete_edition(
    edition_id: int,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    """Delete edition - Admin only"""
    return await handle_delete_edition(edition_id=edition_id, current_user=current_user, db=db)
