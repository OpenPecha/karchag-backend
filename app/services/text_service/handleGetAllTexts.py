from fastapi import Depends
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models import KagyurText, User
from app.schemas import TextsListResponse, KagyurTextResponse, PaginationResponse

async def handle_get_all_texts(
        admin_user: User,  # Admin user passed from router
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> TextsListResponse:
        """
        Get all texts without category filtering - just pagination and search
        
        Args:
            db: Database session
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            search: Search in titles (optional)
            
        Returns:
            TextsListResponse with all texts (paginated)
        """
        
        # Build base query with eager loading
        query = db.query(KagyurText).options(
            joinedload(KagyurText.sub_category),
            joinedload(KagyurText.text_summary),
            joinedload(KagyurText.sermon),
            joinedload(KagyurText.yana),
            joinedload(KagyurText.translation_type)
        )
        
        # Apply search filter if provided
        if search:
            search_filter = or_(
                KagyurText.english_title.ilike(f"%{search}%"),
                KagyurText.tibetan_title.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        texts = query.order_by(KagyurText.order_index).offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        
        return TextsListResponse(
            texts=[KagyurTextResponse.from_orm(text) for text in texts],
            pagination=PaginationResponse(
                current_page=page,
                total_pages=total_pages,
                total_items=total_count,
                items_per_page=limit,
                has_next=page < total_pages,
                has_prev=page > 1
            )
        )
