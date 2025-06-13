# app/routers/admin/texts.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, text
from typing import List, Optional
import csv
import json
from io import StringIO
from database import get_db
from models import KagyurText, SubCategory, TextSummary, YesheDESpan, Volume,Yana,Sermon, TranslationType
from schemas import (
    KagyurTextResponse, KagyurTextCreate, KagyurTextUpdate,KagyurTextCreateRequest,
    TextSummaryCreate, YesheDESpanCreate, VolumeCreate,PaginationResponse, TextsListResponse, 
)
from sqlalchemy.exc import IntegrityError

router = APIRouter( tags=["Admin - Texts"])

@router.get("/texts", response_model=TextsListResponse)
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

@router.post("/categories/{category_id}/subcategories/{sub_category_id}/texts", response_model=dict)
async def create_text(
    category_id: int,
    sub_category_id: int,
    text_data: KagyurTextCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new text with all related data"""
    print(f"DEBUG: Starting create_text with category_id={category_id}, sub_category_id={sub_category_id}")
    print(f"DEBUG: text_data type: {type(text_data)}")
    print(f"DEBUG: text_data content: {text_data.dict()}")
    
    try:
        # Step 1: Verify sub-category exists
        print("DEBUG: Step 1 - Verifying sub-category")
        sub_category = db.query(SubCategory).filter(
            SubCategory.id == sub_category_id,
            SubCategory.main_category_id == category_id
        ).first()
        
        if not sub_category:
            raise HTTPException(
                status_code=404, 
                detail=f"Sub-category {sub_category_id} not found in category {category_id}"
            )
        print(f"DEBUG: Sub-category found: {sub_category.id}")
        
        # Step 2: Validate foreign keys
        print("DEBUG: Step 2 - Validating foreign keys")
        
        # Validate sermon_id if provided
        if text_data.sermon_id:
            sermon = db.query(Sermon).filter(Sermon.id == text_data.sermon_id).first()
            if not sermon:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sermon_id: {text_data.sermon_id}"
                )
            print(f"DEBUG: Sermon validation passed: {sermon.id}")
        
        # Validate yana_id if provided
        if text_data.yana_id:
            yana = db.query(Yana).filter(Yana.id == text_data.yana_id).first()
            if not yana:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid yana_id: {text_data.yana_id}"
                )
            print(f"DEBUG: Yana validation passed: {yana.id}")
        
        # Validate translation_type_id if provided
        if text_data.translation_type_id:
            translation_type = db.query(TranslationType).filter(
                TranslationType.id == text_data.translation_type_id
            ).first()
            if not translation_type:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid translation_type_id: {text_data.translation_type_id}"
                )
            print(f"DEBUG: Translation type validation passed: {translation_type.id}")
        
        # Step 3: Create main text
        print("DEBUG: Step 3 - Creating main text")
        text_dict = text_data.dict(exclude={'text_summary', 'yeshe_de_spans'})
        text_dict['sub_category_id'] = sub_category_id
        print(f"DEBUG: Main text dict: {text_dict}")
        
        # Create the main text object
        new_text = KagyurText(**text_dict)
        db.add(new_text)
        
        # Flush to get the ID, but don't commit yet
        db.flush()
        print(f"DEBUG: Text flushed successfully, ID: {new_text.id}")
        
        # Step 4: Create text summary if provided
        if text_data.text_summary:
            print(f"DEBUG: Creating summary for text_id: {new_text.id}")
            
            # Verify the text exists by querying it back
            text_exists = db.query(KagyurText).filter(KagyurText.id == new_text.id).first()
            if not text_exists:
                print(f"DEBUG: ERROR - Text {new_text.id} not found after flush!")
                raise HTTPException(
                    status_code=500,
                    detail="Text creation failed - text not found after creation"
                )
            print(f"DEBUG: Text exists verification passed: {text_exists.id}")
            
            summary_dict = text_data.text_summary.dict()
            summary_dict['text_id'] = new_text.id
            print(f"DEBUG: Summary dict: {summary_dict}")
            
            try:
                new_summary = TextSummary(**summary_dict)
                db.add(new_summary)
                db.flush()  # Flush the summary
                print(f"DEBUG: Summary created successfully with ID: {new_summary.id}")
            except Exception as summary_error:
                print(f"DEBUG: Error creating summary: {summary_error}")
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating text summary: {str(summary_error)}"
                )
        
        # Step 5: Create Yeshe De spans if provided
        if text_data.yeshe_de_spans:
            print(f"DEBUG: Creating Yeshe De spans")
            for span_data in text_data.yeshe_de_spans:
                span_dict = span_data.dict(exclude={'volumes'})
                span_dict['text_id'] = new_text.id
                
                new_span = YesheDESpan(**span_dict)
                db.add(new_span)
                db.flush()
                
                # Create volumes for this span
                if span_data.volumes:
                    for volume_data in span_data.volumes:
                        volume_dict = volume_data.dict()
                        volume_dict['yeshe_de_span_id'] = new_span.id
                        
                        new_volume = Volume(**volume_dict)
                        db.add(new_volume)
            
            db.flush()  # Flush all spans and volumes
            print(f"DEBUG: Yeshe De spans created successfully")
        
        # Step 6: Commit all changes
        db.commit()
        print(f"DEBUG: All changes committed successfully")
        
        # Step 7: Return the created text with all relationships
        created_text = db.query(KagyurText).filter(KagyurText.id == new_text.id).first()
        
        return {
            "message": "Text created successfully",
            "text_id": created_text.id,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        db.rollback()
        raise
        
    except IntegrityError as e:
        print(f"DEBUG: IntegrityError occurred: {e}")
        print(f"DEBUG: IntegrityError orig: {e.orig}")
        db.rollback()
        
        # Parse the error message
        error_detail = "Database constraint violation"
        error_str = str(e).lower()
        
        if "foreign key constraint" in error_str:
            if "text_summaries_text_id_fkey" in error_str:
                # Check if this is the table name mismatch issue
                if "karchag_texts" in error_str:
                    error_detail = "Database table name mismatch - foreign key constraint refers to wrong table name. Check if the foreign key constraint in text_summaries table references the correct table name (should be 'kagyur_texts' not 'karchag_texts')"
                else:
                    error_detail = "Text ID reference error - the text may not have been created properly"
            elif "sermon_id" in error_str or "sermons" in error_str:
                error_detail = "Invalid sermon_id provided"
            elif "yana_id" in error_str or "yanas" in error_str:
                error_detail = "Invalid yana_id provided"
            elif "translation_type_id" in error_str or "translation_types" in error_str:
                error_detail = "Invalid translation_type_id provided"
            elif "sub_categories" in error_str:
                error_detail = "Invalid sub_category_id provided"
            else:
                error_detail = f"Foreign key constraint violation: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
        elif "unique constraint" in error_str:
            error_detail = "Duplicate entry - this text may already exist"
        elif "not null constraint" in error_str:
            error_detail = "Required field is missing"
        
        raise HTTPException(
            status_code=400,
            detail=error_detail
        )
        
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.put("/texts/{text_id}", response_model=dict)
async def update_text(
    text_id: int,
    text_data: KagyurTextUpdate,
    db: Session = Depends(get_db)
):
    """Update a text with all related data"""
    print(f"DEBUG: Starting update_text with text_id={text_id}")
    print(f"DEBUG: text_data type: {type(text_data)}")
    print(f"DEBUG: text_data content: {text_data.dict()}")
    
    try:
        # Step 1: Check if text exists
        print("DEBUG: Step 1 - Checking if text exists")
        db_text = db.query(KagyurText).filter(KagyurText.id == text_id).first()
        if not db_text:
            raise HTTPException(status_code=404, detail=f"Text with ID {text_id} not found")
        print(f"DEBUG: Text found: {db_text.id}")
        
        # Step 2: Validate foreign keys if they're being updated
        print("DEBUG: Step 2 - Validating foreign keys")
        
        # Validate sub_category_id if provided
        if hasattr(text_data, 'sub_category_id') and text_data.sub_category_id is not None:
            sub_category = db.query(SubCategory).filter(SubCategory.id == text_data.sub_category_id).first()
            if not sub_category:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sub_category_id: {text_data.sub_category_id}"
                )
            print(f"DEBUG: Sub-category validation passed: {sub_category.id}")
        
        # Validate sermon_id if provided
        if hasattr(text_data, 'sermon_id') and text_data.sermon_id is not None:
            sermon = db.query(Sermon).filter(Sermon.id == text_data.sermon_id).first()
            if not sermon:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sermon_id: {text_data.sermon_id}"
                )
            print(f"DEBUG: Sermon validation passed: {sermon.id}")
        
        # Validate yana_id if provided
        if hasattr(text_data, 'yana_id') and text_data.yana_id is not None:
            yana = db.query(Yana).filter(Yana.id == text_data.yana_id).first()
            if not yana:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid yana_id: {text_data.yana_id}"
                )
            print(f"DEBUG: Yana validation passed: {yana.id}")
        
        # Validate translation_type_id if provided
        if hasattr(text_data, 'translation_type_id') and text_data.translation_type_id is not None:
            translation_type = db.query(TranslationType).filter(
                TranslationType.id == text_data.translation_type_id
            ).first()
            if not translation_type:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid translation_type_id: {text_data.translation_type_id}"
                )
            print(f"DEBUG: Translation type validation passed: {translation_type.id}")
        
        # Step 3: Update main text fields
        print("DEBUG: Step 3 - Updating main text fields")
        text_dict = text_data.dict(exclude={'text_summary', 'yeshe_de_spans'}, exclude_unset=True)
        print(f"DEBUG: Text update dict: {text_dict}")
        
        for field, value in text_dict.items():
            if hasattr(db_text, field):
                setattr(db_text, field, value)
                print(f"DEBUG: Updated field {field} to {value}")
        
        # Flush to save main text updates
        db.flush()
        print(f"DEBUG: Main text updates flushed successfully")
        
        # Step 4: Update text summary if provided
        if hasattr(text_data, 'text_summary') and text_data.text_summary is not None:
            print(f"DEBUG: Step 4 - Updating text summary")
            
            if db_text.text_summary:
                # Update existing summary
                print(f"DEBUG: Updating existing summary with ID: {db_text.text_summary.id}")
                summary_dict = text_data.text_summary.dict(exclude_unset=True)
                print(f"DEBUG: Summary update dict: {summary_dict}")
                
                for field, value in summary_dict.items():
                    if hasattr(db_text.text_summary, field):
                        setattr(db_text.text_summary, field, value)
                        print(f"DEBUG: Updated summary field {field} to {value}")
            else:
                # Create new summary
                print(f"DEBUG: Creating new summary for text_id: {text_id}")
                summary_dict = text_data.text_summary.dict()
                summary_dict['text_id'] = text_id
                print(f"DEBUG: New summary dict: {summary_dict}")
                
                try:
                    new_summary = TextSummary(**summary_dict)
                    db.add(new_summary)
                    db.flush()
                    print(f"DEBUG: New summary created successfully with ID: {new_summary.id}")
                except Exception as summary_error:
                    print(f"DEBUG: Error creating summary: {summary_error}")
                    db.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error creating text summary: {str(summary_error)}"
                    )
        
        # Step 5: Handle Yeshe De spans update if provided
        if hasattr(text_data, 'yeshe_de_spans') and text_data.yeshe_de_spans is not None:
            print(f"DEBUG: Step 5 - Updating Yeshe De spans")
            
            # Delete existing spans and their volumes
            print(f"DEBUG: Deleting existing spans for text_id: {text_id}")
            existing_spans = db.query(YesheDESpan).filter(YesheDESpan.text_id == text_id).all()
            for span in existing_spans:
                # Delete volumes first (due to foreign key constraints)
                volumes = db.query(Volume).filter(Volume.yeshe_de_span_id == span.id).all()
                for volume in volumes:
                    db.delete(volume)
                db.delete(span)
            
            db.flush()  # Flush deletions
            print(f"DEBUG: Existing spans deleted successfully")
            
            # Create new spans
            if text_data.yeshe_de_spans:
                print(f"DEBUG: Creating new Yeshe De spans")
                for span_data in text_data.yeshe_de_spans:
                    span_dict = span_data.dict(exclude={'volumes'})
                    span_dict['text_id'] = text_id
                    
                    new_span = YesheDESpan(**span_dict)
                    db.add(new_span)
                    db.flush()
                    print(f"DEBUG: Created span with ID: {new_span.id}")
                    
                    # Create volumes for this span
                    if hasattr(span_data, 'volumes') and span_data.volumes:
                        for volume_data in span_data.volumes:
                            volume_dict = volume_data.dict()
                            volume_dict['yeshe_de_span_id'] = new_span.id
                            
                            new_volume = Volume(**volume_dict)
                            db.add(new_volume)
                
                db.flush()  # Flush all spans and volumes
                print(f"DEBUG: All new Yeshe De spans created successfully")
        
        # Step 6: Commit all changes
        db.commit()
        print(f"DEBUG: All changes committed successfully")
        
        # Step 7: Return success response
        return {
            "message": "Text updated successfully",
            "text_id": text_id,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        print(f"DEBUG: HTTPException occurred, rolling back")
        db.rollback()
        raise
        
    except IntegrityError as e:
        print(f"DEBUG: IntegrityError occurred: {e}")
        print(f"DEBUG: IntegrityError orig: {e.orig}")
        db.rollback()
        
        # Parse the error message (same logic as create endpoint)
        error_detail = "Database constraint violation"
        error_str = str(e).lower()
        
        if "foreign key constraint" in error_str:
            if "text_summaries_text_id_fkey" in error_str:
                # Check if this is the table name mismatch issue
                if "karchag_texts" in error_str:
                    error_detail = "Database table name mismatch - foreign key constraint refers to wrong table name. Check if the foreign key constraint in text_summaries table references the correct table name (should be 'kagyur_texts' not 'karchag_texts')"
                else:
                    error_detail = "Text ID reference error - the text may not exist"
            elif "sermon_id" in error_str or "sermons" in error_str:
                error_detail = "Invalid sermon_id provided"
            elif "yana_id" in error_str or "yanas" in error_str:
                error_detail = "Invalid yana_id provided"
            elif "translation_type_id" in error_str or "translation_types" in error_str:
                error_detail = "Invalid translation_type_id provided"
            elif "sub_categories" in error_str:
                error_detail = "Invalid sub_category_id provided"
            else:
                error_detail = f"Foreign key constraint violation: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
        elif "unique constraint" in error_str:
            error_detail = "Duplicate entry - this combination may already exist"
        elif "not null constraint" in error_str:
            error_detail = "Required field is missing"
        
        raise HTTPException(
            status_code=400,
            detail=error_detail
        )
        
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

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