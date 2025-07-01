from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import KagyurText, SubCategory, TextSummary, YesheDESpan, Volume, Yana, Sermon, TranslationType,User
from schemas import KagyurTextCreateRequest
from sqlalchemy.exc import IntegrityError
import logging

# Set up logging
logger = logging.getLogger(__name__)

def handle_create_text(
    category_id: int,
    sub_category_id: int,
    text_data: KagyurTextCreateRequest,
    current_user: User,  # Admin user passed from router
    db: Session = Depends(get_db)
):
    """Create a new text with all related data"""
    logger.info(f"Starting create_text with category_id={category_id}, sub_category_id={sub_category_id}")
    logger.debug(f"text_data content: {text_data.dict()}")
    
    try:
        # Step 1: Verify sub-category exists
        logger.debug("Step 1 - Verifying sub-category")
        sub_category = db.query(SubCategory).filter(
            SubCategory.id == sub_category_id,
            SubCategory.main_category_id == category_id
        ).first()
        
        if not sub_category:
            raise HTTPException(
                status_code=404, 
                detail=f"Sub-category {sub_category_id} not found in category {category_id}"
            )
        logger.debug(f"Sub-category found: {sub_category.id}")
        
        # Step 2: Validate foreign keys
        logger.debug("Step 2 - Validating foreign keys")
        
        # Validate sermon_id if provided
        if text_data.sermon_id:
            sermon = db.query(Sermon).filter(Sermon.id == text_data.sermon_id).first()
            if not sermon:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid sermon_id: {text_data.sermon_id}"
                )
            logger.debug(f"Sermon validation passed: {sermon.id}")
        
        # Validate yana_id if provided
        if text_data.yana_id:
            yana = db.query(Yana).filter(Yana.id == text_data.yana_id).first()
            if not yana:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid yana_id: {text_data.yana_id}"
                )
            logger.debug(f"Yana validation passed: {yana.id}")
        
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
            logger.debug(f"Translation type validation passed: {translation_type.id}")
        
        # Step 3: Create main text
        logger.debug("Step 3 - Creating main text")
        text_dict = text_data.dict(exclude={'text_summary', 'yeshe_de_spans'})
        text_dict['sub_category_id'] = sub_category_id
        logger.debug(f"Main text dict: {text_dict}")
        
        # Create the main text object
        new_text = KagyurText(**text_dict)
        db.add(new_text)
        
        # Flush to get the ID, but don't commit yet
        db.flush()
        logger.debug(f"Text flushed successfully, ID: {new_text.id}")
        
        # Step 4: Create text summary if provided
        if text_data.text_summary:
            logger.debug(f"Creating summary for text_id: {new_text.id}")
            
            summary_dict = text_data.text_summary.dict()
            summary_dict['text_id'] = new_text.id
            logger.debug(f"Summary dict: {summary_dict}")
            
            try:
                new_summary = TextSummary(**summary_dict)
                db.add(new_summary)
                db.flush()  # Flush the summary
                logger.debug(f"Summary created successfully with ID: {new_summary.id}")
            except Exception as summary_error:
                logger.error(f"Error creating summary: {summary_error}")
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating text summary: {str(summary_error)}"
                )
        
        # Step 5: Create Yeshe De spans if provided
        if text_data.yeshe_de_spans:
            logger.debug("Creating Yeshe De spans")
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
            logger.debug("Yeshe De spans created successfully")
        
        # Step 6: Commit all changes
        db.commit()
        logger.info("All changes committed successfully")
        
        # Step 7: Refresh the object to get the latest state
        db.refresh(new_text)
        
        return {
            "message": "Text created successfully",
            "text_id": new_text.id,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        db.rollback()
        raise
        
    except IntegrityError as e:
        logger.error(f"IntegrityError occurred: {e}")
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
        logger.error(f"Unexpected error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )