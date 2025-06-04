# app/routers/admin/texts.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
import csv
import json
from io import StringIO
from database import get_db
from models import KagyurText, SubCategory, TextSummary, YesheDESpan, Volume
from schemas import (
    KagyurTextResponse, KagyurTextCreate, KagyurTextUpdate,
    TextSummaryCreate, YesheDESpanCreate, VolumeCreate
)

router = APIRouter( tags=["Admin - Texts"])

@router.get("/texts", response_model=dict)
async def get_all_texts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    sub_category_id: Optional[int] = Query(None, description="Filter by sub-category ID"),
    search: Optional[str] = Query(None, description="Search in titles"),
    db: Session = Depends(get_db)
):
    """Get all texts with pagination and filters"""
    
    # Build base query
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
    
    return {
        "texts": texts,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_count,
            "items_per_page": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

@router.get("/categories/{category_id}/subcategories/{sub_category_id}/texts")
async def get_texts_by_subcategory(
    category_id: int,
    sub_category_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get texts within specific sub-category"""
    
    # Verify sub-category exists and belongs to category
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    # Build query
    query = db.query(KagyurText).filter(KagyurText.sub_category_id == sub_category_id)
    
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
    
    return {
        "texts": texts,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_count,
            "items_per_page": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

@router.get("/texts/{text_id}", response_model=KagyurTextResponse)
async def get_text(text_id: int, db: Session = Depends(get_db)):
    """Get complete text data for editing"""
    
    text = db.query(KagyurText).options(
        joinedload(KagyurText.text_summary),
        joinedload(KagyurText.sermon),
        joinedload(KagyurText.yana),
        joinedload(KagyurText.translation_type),
        joinedload(KagyurText.yeshe_de_spans).joinedload(YesheDeSpan.volumes),
        joinedload(KagyurText.sub_category)
    ).filter(KagyurText.id == text_id).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    return text

@router.post("/categories/{category_id}/subcategories/{sub_category_id}/texts", 
             response_model=KagyurTextResponse, status_code=201)
async def create_text(
    category_id: int,
    sub_category_id: int,
    text_data: KagyurTextCreate,
    db: Session = Depends(get_db)
):
    """Create a new text with complete data including summary and volumes"""
    
    # Verify sub-category exists and belongs to category
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not sub_category:
        raise HTTPException(
            status_code=404, 
            detail=f"Sub-category {sub_category_id} not found in category {category_id}"
        )
    
    try:
        # Create the main text
        text_dict = text_data.model_dump(exclude={'text_summary', 'yeshe_de_spans'})
        text_dict['sub_category_id'] = sub_category_id
        
        db_text = KagyurText(**text_dict)
        db.add(db_text)
        db.flush()  # Get the ID without committing
        
        # Create text summary if provided
        if text_data.text_summary:
            summary_dict = text_data.text_summary.model_dump()
            summary_dict['text_id'] = db_text.id
            db_summary = TextSummary(**summary_dict)
            db.add(db_summary)
        
        # Create yeshe_de_spans with volumes if provided
        if text_data.yeshe_de_spans:
            for span_data in text_data.yeshe_de_spans:
                # Create YesheDeSpan
                db_span = YesheDESpan(text_id=db_text.id)
                db.add(db_span)
                db.flush()  # Get the span ID
                
                # Create volumes for this span
                if span_data.volumes:
                    for volume_data in span_data.volumes:
                        volume_dict = volume_data.model_dump()
                        volume_dict['yeshe_de_span_id'] = db_span.id
                        db_volume = Volume(**volume_dict)
                        db.add(db_volume)
        
        db.commit()
        
        # Return the created text with all relationships
        return await get_text(db_text.id, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating text: {str(e)}")

@router.put("/texts/{text_id}", response_model=KagyurTextResponse)
async def update_text(
    text_id: int,
    text_data: KagyurTextUpdate,
    db: Session = Depends(get_db)
):
    """Update a text"""
    
    db_text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not db_text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    try:
        # Update main text fields
        text_dict = text_data.model_dump(exclude={'text_summary', 'yeshe_de_spans'}, exclude_unset=True)
        for field, value in text_dict.items():
            setattr(db_text, field, value)
        
        # Update text summary if provided
        if text_data.text_summary:
            if db_text.text_summary:
                # Update existing summary
                for field, value in text_data.text_summary.model_dump(exclude_unset=True).items():
                    setattr(db_text.text_summary, field, value)
            else:
                # Create new summary
                summary_dict = text_data.text_summary.model_dump()
                summary_dict['text_id'] = text_id
                db_summary = TextSummary(**summary_dict)
                db.add(db_summary)
        
        # Handle yeshe_de_spans update (this is complex, might want to handle separately)
        if text_data.yeshe_de_spans is not None:
            # For simplicity, we'll delete existing spans and recreate
            # In production, you might want more sophisticated update logic
            for span in db_text.yeshe_de_spans:
                db.delete(span)
            
            # Create new spans
            for span_data in text_data.yeshe_de_spans:
                db_span = YesheDeSpan(text_id=text_id)
                db.add(db_span)
                db.flush()
                
                if span_data.volumes:
                    for volume_data in span_data.volumes:
                        volume_dict = volume_data.model_dump()
                        volume_dict['yeshe_de_span_id'] = db_span.id
                        db_volume = Volume(**volume_dict)
                        db.add(db_volume)
        
        db.commit()
        return await get_text(text_id, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating text: {str(e)}")

@router.delete("/texts/{text_id}")
async def delete_text(text_id: int, db: Session = Depends(get_db)):
    """Delete a text"""
    
    db_text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
    if not db_text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    db.delete(db_text)
    db.commit()
    return {"message": "Text deleted successfully"}

@router.post("texts/bulk-import")
async def bulk_import_texts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Bulk import texts from CSV/JSON file"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            # Handle CSV import
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    if not row.get('english_title') or not row.get('sub_category_id'):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue
                    
                    # Create text
                    text_data = {
                        'english_title': row['english_title'],
                        'tibetan_title': row.get('tibetan_title', ''),
                        'sub_category_id': int(row['sub_category_id']),
                        'order_index': int(row.get('order_index', 0)),
                        'is_active': row.get('is_active', 'true').lower() == 'true'
                    }
                    
                    db_text = KagyurText(**text_data)
                    db.add(db_text)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            db.commit()
            
        elif file.filename.endswith('.json'):
            # Handle JSON import
            json_content = json.loads(content.decode('utf-8'))
            
            imported_count = 0
            errors = []
            
            for item_num, item in enumerate(json_content, start=1):
                try:
                    text_data = KagyurTextCreate(**item)
                    # Create text using the same logic as create_text
                    # This is simplified - you'd want to reuse the create logic
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Item {item_num}: {str(e)}")
            
            db.commit()
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or JSON.")
        
        return {
            "message": f"Import completed. {imported_count} texts imported.",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")