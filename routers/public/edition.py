from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
import logging
from database import get_db
from models import Edition
from schemas import EditionResponse, EditionPaginatedResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=EditionPaginatedResponse)
async def get_editions(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    lang: Optional[str] = Query("en", regex="^(en|tb)$", description="Language: en for English, tb for Tibetan"),
    search: Optional[str] = Query(None, description="Search term for edition names"),
    db: Session = Depends(get_db)
):
    """
    Get all available Kangyur editions with pagination.
    
    - **page**: Page number (starts from 1)
    - **limit**: Items per page (1-100)
    - **lang**: Language preference (en/tb)
    - **search**: Optional search term for filtering editions
    """
    try:
        # Start building the query
        query = db.query(Edition).filter(Edition.is_active == True)
        
        # Apply search filter if provided
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            if lang == "tb":
                # Search in Tibetan fields
                query = query.filter(
                    func.lower(Edition.name_tibetan).like(func.lower(search_term))
                )
            else:
                # Search in English fields
                query = query.filter(
                    func.lower(Edition.name_english).like(func.lower(search_term))
                )
        
        # Order by order_index and then by name
        if lang == "tb":
            query = query.order_by(Edition.order_index, Edition.name_tibetan)
        else:
            query = query.order_by(Edition.order_index, Edition.name_english)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        editions = query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        logger.info(f"Retrieved {len(editions)} editions (page {page}/{total_pages}, "
                   f"total: {total_count}, lang: {lang})")
        
        return EditionPaginatedResponse(
            editions=editions,
            total=total_count,
            page=page,
            limit=limit,
            pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error in get_editions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{edition_id}", response_model=EditionResponse)
async def get_edition_by_id(
    edition_id: int,
    lang: Optional[str] = Query("en", regex="^(en|tb)$", description="Language: en for English, tb for Tibetan"),
    db: Session = Depends(get_db)
):
    """
    Get specific edition details by ID.
    
    - **edition_id**: ID of the edition to retrieve
    - **lang**: Language preference (en/tb) - affects logging and future features
    """
    try:
        # Query for the specific edition
        edition = db.query(Edition).filter(
            and_(
                Edition.id == edition_id,
                Edition.is_active == True
            )
        ).first()
        
        if not edition:
            logger.warning(f"Edition with ID {edition_id} not found or inactive")
            raise HTTPException(
                status_code=404, 
                detail=f"Edition with ID {edition_id} not found"
            )
        
        logger.info(f"Retrieved edition {edition_id}: "
                   f"{edition.name_english} (lang: {lang})")
        
        return edition
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in get_edition_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


