from fastapi import  Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import KagyurText, SubCategory, TextSummary, YesheDESpan, Volume,Yana,Sermon, TranslationType,User
from schemas import  KagyurTextUpdate
from sqlalchemy.exc import IntegrityError

async def handle_put_text(
    text_id: int,
    text_data: KagyurTextUpdate,
    current_user: User,  # Admin user passed from router
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
        sub_category_id = getattr(text_data, 'sub_category_id', None)
        if sub_category_id is not None:
            sub_category = db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()
            if not sub_category:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sub_category_id: {sub_category_id}"
                )
            print(f"DEBUG: Sub-category validation passed: {sub_category.id}")
        
        # Validate sermon_id if provided
        sermon_id = getattr(text_data, 'sermon_id', None)
        if sermon_id is not None:
            sermon = db.query(Sermon).filter(Sermon.id == sermon_id).first()
            if not sermon:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sermon_id: {sermon_id}"
                )
            print(f"DEBUG: Sermon validation passed: {sermon.id}")
        
        # Validate yana_id if provided
        yana_id = getattr(text_data, 'yana_id', None)
        if yana_id is not None:
            yana = db.query(Yana).filter(Yana.id == yana_id).first()
            if not yana:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid yana_id: {yana_id}"
                )
            print(f"DEBUG: Yana validation passed: {yana.id}")
        
        # Validate translation_type_id if provided
        translation_type_id = getattr(text_data, 'translation_type_id', None)
        if translation_type_id is not None:
            translation_type = db.query(TranslationType).filter(
                TranslationType.id == translation_type_id
            ).first()
            if not translation_type:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid translation_type_id: {translation_type_id}"
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