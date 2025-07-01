from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import KagyurText, SubCategory, TextSummary, YesheDESpan, Volume, Yana, Sermon, TranslationType, User
from schemas import KagyurTextCreateRequest, TextSummaryCreate, YesheDESpanCreate, VolumeCreate
import csv
import json
from io import StringIO
import logging

# Set up logging
logger = logging.getLogger(__name__)

async def handle_bulk_import_texts(
    file: UploadFile,
    current_user: User,  # Admin user passed from router
    db: Session
) -> dict:
    """Bulk import texts from CSV/JSON file with comprehensive validation and error handling"""
    
    logger.info(f"Starting bulk import for file: {file.filename}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        content = await file.read()
        logger.debug(f"File content read successfully, size: {len(content)} bytes")
        
        imported_count = 0
        errors = []
        
        if file.filename.endswith('.csv'):
            logger.info("Processing CSV file")
            imported_count, errors = await _process_csv_import(content, db)
            
        elif file.filename.endswith('.json'):
            logger.info("Processing JSON file")
            imported_count, errors = await _process_json_import(content, db)
            
        else:
            raise HTTPException(
                status_code=415, 
                detail="Unsupported Media Type. Only CSV and JSON files are supported."
            )
        
        # Commit all successful imports
        db.commit()
        logger.info(f"Bulk import completed. {imported_count} texts imported, {len(errors)} errors")
        
        return {
            "message": f"Import completed. {imported_count} texts imported successfully.",
            "imported_count": imported_count,
            "error_count": len(errors),
            "errors": errors,
            "status": "success" if imported_count > 0 else "failed"
        }
        
    except HTTPException:
        db.rollback()
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during bulk import: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during bulk import: {str(e)}"
        )

async def _process_csv_import(content: bytes, db: Session) -> tuple[int, list]:
    """Process CSV file import"""
    try:
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                logger.debug(f"Processing CSV row {row_num}: {row}")
                
                # Validate required fields
                if not row.get('english_title'):
                    errors.append(f"Row {row_num}: Missing required field 'english_title'")
                    continue
                
                if not row.get('sub_category_id'):
                    errors.append(f"Row {row_num}: Missing required field 'sub_category_id'")
                    continue
                
                # Parse and validate sub_category_id
                try:
                    sub_category_id = int(row['sub_category_id'])
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid sub_category_id format")
                    continue
                
                # Extract category_id if provided, otherwise derive from sub_category
                category_id = None
                if row.get('category_id'):
                    try:
                        category_id = int(row['category_id'])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid category_id format")
                        continue
                
                # Create text data structure
                text_data_dict = {
                    'english_title': row['english_title'].strip(),
                    'tibetan_title': row.get('tibetan_title', '').strip(),
                    'order_index': _safe_int_convert(row.get('order_index', '0')),
                    'is_active': _safe_bool_convert(row.get('is_active', 'true')),
                    'sermon_id': _safe_int_convert(row.get('sermon_id')) if row.get('sermon_id') else None,
                    'yana_id': _safe_int_convert(row.get('yana_id')) if row.get('yana_id') else None,
                    'translation_type_id': _safe_int_convert(row.get('translation_type_id')) if row.get('translation_type_id') else None,
                }
                
                # Handle optional fields
                optional_fields = [
                    'tibetan_short_title', 'wylie_title', 'sanskrit_title', 'chinese_title',
                    'toh_number', 'cbeta_number', 'alternative_titles', 'translators',
                    'source_language', 'target_language', 'translation_period', 'location',
                    'notes', 'content_summary', 'keywords', 'difficulty_level'
                ]
                
                for field in optional_fields:
                    if row.get(field):
                        text_data_dict[field] = row[field].strip()
                
                # Create text summary if provided
                text_summary = None
                if any(row.get(f'summary_{field}') for field in ['content', 'key_points', 'significance']):
                    text_summary = TextSummaryCreate(
                        content=row.get('summary_content', '').strip(),
                        key_points=row.get('summary_key_points', '').strip(),
                        significance=row.get('summary_significance', '').strip(),
                        word_count=_safe_int_convert(row.get('summary_word_count', '0'))
                    )
                
                # Create the request object
                text_request = KagyurTextCreateRequest(
                    **text_data_dict,
                    text_summary=text_summary,
                    yeshe_de_spans=[]  # CSV doesn't support complex nested structures
                )
                
                # Use the existing create_text logic
                result = _create_single_text(
                    category_id=category_id,
                    sub_category_id=sub_category_id,
                    text_data=text_request,
                    db=db,
                    row_identifier=f"Row {row_num}"
                )
                
                if result:
                    imported_count += 1
                    logger.debug(f"Successfully imported text from row {row_num}")
                
            except HTTPException as http_e:
                errors.append(f"Row {row_num}: HTTP {http_e.status_code} - {http_e.detail}")
                continue
            except Exception as e:
                logger.error(f"Error processing CSV row {row_num}: {e}")
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        return imported_count, errors
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File encoding error. Please ensure the CSV file is UTF-8 encoded.")
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=422, detail=f"CSV processing failed: {str(e)}")

async def _process_json_import(content: bytes, db: Session) -> tuple[int, list]:
    """Process JSON file import"""
    try:
        json_content = json.loads(content.decode('utf-8'))
        logger.debug(f"JSON content loaded, type: {type(json_content)}")
        
        imported_count = 0
        errors = []
        
        # Handle both single object and array of objects
        if isinstance(json_content, dict):
            json_content = [json_content]
        elif not isinstance(json_content, list):
            raise HTTPException(status_code=422, detail="JSON must be an object or array of objects")
        
        for item_num, item in enumerate(json_content, start=1):
            try:
                logger.debug(f"Processing JSON item {item_num}: {item}")
                
                # Validate required fields
                if not item.get('english_title'):
                    errors.append(f"Item {item_num}: Missing required field 'english_title'")
                    continue
                
                if not item.get('sub_category_id'):
                    errors.append(f"Item {item_num}: Missing required field 'sub_category_id'")
                    continue
                
                # Create text request from JSON data
                try:
                    text_request = KagyurTextCreateRequest(**item)
                except Exception as validation_error:
                    errors.append(f"Item {item_num}: Validation error - {str(validation_error)}")
                    continue
                
                # Extract category_id
                category_id = item.get('category_id')
                sub_category_id = item['sub_category_id']
                
                # Use the existing create_text logic
                result = _create_single_text(
                    category_id=category_id,
                    sub_category_id=sub_category_id,
                    text_data=text_request,
                    db=db,
                    row_identifier=f"Item {item_num}"
                )
                
                if result:
                    imported_count += 1
                    logger.debug(f"Successfully imported text from item {item_num}")
                
            except HTTPException as http_e:
                errors.append(f"Item {item_num}: HTTP {http_e.status_code} - {http_e.detail}")
                continue
            except Exception as e:
                logger.error(f"Error processing JSON item {item_num}: {e}")
                errors.append(f"Item {item_num}: {str(e)}")
                continue
        
        return imported_count, errors
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON format: {str(e)}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File encoding error. Please ensure the JSON file is UTF-8 encoded.")
    except Exception as e:
        logger.error(f"Error processing JSON file: {e}")
        raise HTTPException(status_code=422, detail=f"JSON processing failed: {str(e)}")

def _create_single_text(
    category_id: int,
    sub_category_id: int,
    text_data: KagyurTextCreateRequest,
    db: Session,
    row_identifier: str
) -> bool:
    """Create a single text using the same logic as handle_create_text"""
    try:
        logger.debug(f"Creating text for {row_identifier}")
        
        # Step 1: Verify sub-category exists
        sub_category_query = db.query(SubCategory).filter(SubCategory.id == sub_category_id)
        if category_id:
            sub_category_query = sub_category_query.filter(SubCategory.main_category_id == category_id)
        
        sub_category = sub_category_query.first()
        if not sub_category:
            if category_id:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Sub-category {sub_category_id} not found in category {category_id}"
                )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Sub-category {sub_category_id} not found"
                )
        
        # Step 2: Validate foreign keys
        if text_data.sermon_id:
            sermon = db.query(Sermon).filter(Sermon.id == text_data.sermon_id).first()
            if not sermon:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Sermon with ID {text_data.sermon_id} not found"
                )
        
        if text_data.yana_id:
            yana = db.query(Yana).filter(Yana.id == text_data.yana_id).first()
            if not yana:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Yana with ID {text_data.yana_id} not found"
                )
        
        if text_data.translation_type_id:
            translation_type = db.query(TranslationType).filter(
                TranslationType.id == text_data.translation_type_id
            ).first()
            if not translation_type:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Translation type with ID {text_data.translation_type_id} not found"
                )
        
        # Step 3: Create main text
        text_dict = text_data.dict(exclude={'text_summary', 'yeshe_de_spans'})
        text_dict['sub_category_id'] = sub_category_id
        
        new_text = KagyurText(**text_dict)
        db.add(new_text)
        db.flush()
        
        # Step 4: Create text summary if provided
        if text_data.text_summary:
            summary_dict = text_data.text_summary.dict()
            summary_dict['text_id'] = new_text.id
            
            new_summary = TextSummary(**summary_dict)
            db.add(new_summary)
            db.flush()
        
        # Step 5: Create Yeshe De spans if provided
        if text_data.yeshe_de_spans:
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
            
            db.flush()
        
        logger.debug(f"Successfully created text with ID: {new_text.id} for {row_identifier}")
        return True
        
    except HTTPException:
        db.rollback()
        raise
        
    except IntegrityError as e:
        logger.error(f"IntegrityError for {row_identifier}: {e}")
        db.rollback()
        
        # Parse the error message and return appropriate HTTP status codes
        error_str = str(e).lower()
        
        if "foreign key constraint" in error_str:
            if "text_summaries_text_id_fkey" in error_str:
                if "karchag_texts" in error_str:
                    raise HTTPException(
                        status_code=500,
                        detail="Database schema error - foreign key constraint refers to wrong table name"
                    )
                else:
                    raise HTTPException(
                        status_code=422,
                        detail="Text ID reference error"
                    )
            elif "sermon_id" in error_str:
                raise HTTPException(
                    status_code=404,
                    detail="Referenced sermon not found"
                )
            elif "yana_id" in error_str:
                raise HTTPException(
                    status_code=404,
                    detail="Referenced yana not found"
                )
            elif "translation_type_id" in error_str:
                raise HTTPException(
                    status_code=404,
                    detail="Referenced translation type not found"
                )
            elif "sub_categories" in error_str:
                raise HTTPException(
                    status_code=404,
                    detail="Referenced sub-category not found"
                )
            else:
                raise HTTPException(
                    status_code=422,
                    detail=f"Foreign key constraint violation: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
                )
        elif "unique constraint" in error_str:
            raise HTTPException(
                status_code=409,
                detail="Duplicate entry - this text already exists"
            )
        elif "not null constraint" in error_str:
            raise HTTPException(
                status_code=422,
                detail="Required field is missing"
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Database constraint violation: {str(e)}"
            )
        
    except Exception as e:
        logger.error(f"Error creating text for {row_identifier}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while creating text: {str(e)}"
        )

def _safe_int_convert(value: str) -> int:
    """Safely convert string to int"""
    if not value or value.strip() == '':
        return 0
    try:
        return int(value.strip())
    except ValueError:
        return 0

def _safe_bool_convert(value: str) -> bool:
    """Safely convert string to bool"""
    if not value:
        return True
    return value.strip().lower() in ('true', '1', 'yes', 'on')