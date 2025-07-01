# text_service.py
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from models import KagyurText, SubCategory
from schemas import TextsListResponse, KagyurTextResponse, PaginationResponse

async def handle_fetch_texts(
        db: Session,
        page: int = 1,
        limit: int = 20,
        category_id: Optional[int] = None,
        sub_category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> TextsListResponse:
        """
        Get all texts with pagination and filters
        
        Args:
            db: Database session
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            category_id: Filter by category ID
            sub_category_id: Filter by sub-category ID
            search: Search in titles
            
        Returns:
            TextsListResponse with paginated texts and metadata
        """
        
        # Build base query with eager loading
        query = db.query(KagyurText).options(
            joinedload(KagyurText.sub_category),
            joinedload(KagyurText.text_summary),
            joinedload(KagyurText.sermon),
            joinedload(KagyurText.yana),
            joinedload(KagyurText.translation_type)
        )
        
        # Apply filters
        if sub_category_id:
            query = query.filter(KagyurText.sub_category_id == sub_category_id)
        elif category_id:
            query = query.join(SubCategory).filter(SubCategory.main_category_id == category_id)
        
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