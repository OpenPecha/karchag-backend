from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from database import get_db
from models import MainCategory, SubCategory, KarchagText, TextSummary,YesheDESpan,Volume
from schemas import (
    MainCategoryResponse, MainCategoryWithSubCategories, MainCategoryCreate,
    SubCategoryResponse, SubCategoryWithTexts, SubCategoryCreate,
    KarchagTextResponse,KarchagTextCreate,
    
)

router = APIRouter()

# GET Endpoints
@router.get("/categories", response_model=List[MainCategoryResponse], tags=["Categories"])
async def get_categories(db: Session = Depends(get_db)):
    """
    Retrieve all main categories.
    
    Returns a list of all active main categories ordered by their index.
    """
    categories = db.query(MainCategory).filter(
        MainCategory.is_active == True
    ).order_by(MainCategory.order_index).all()
    return categories

@router.get("/category/{category_id}", response_model=MainCategoryWithSubCategories, tags=["Categories"])
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific main category with its sub-categories.
    
    Args:
        category_id: The ID of the main category to retrieve
        
    Returns:
        Main category details with associated sub-categories
        
    Raises:
        HTTPException: 404 if category not found
    """
    category = db.query(MainCategory).filter(
        MainCategory.id == category_id,
        MainCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@router.get("/category/{category_id}/sub-categories", response_model=List[SubCategoryResponse], tags=["Sub-Categories"])
async def get_sub_categories(category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all sub-categories for a specific main category.
    
    Args:
        category_id: The ID of the main category
        
    Returns:
        List of sub-categories belonging to the specified main category
        
    Raises:
        HTTPException: 404 if main category not found
    """
    # Verify main category exists
    category = db.query(MainCategory).filter(
        MainCategory.id == category_id,
        MainCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    sub_categories = db.query(SubCategory).filter(
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).order_by(SubCategory.order_index).all()
    
    return sub_categories

@router.get("/category/{category_id}/sub-category/{sub_category_id}", response_model=SubCategoryWithTexts, tags=["Sub-Categories"])
async def get_sub_category(category_id: int, sub_category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific sub-category with its texts.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category to retrieve
        
    Returns:
        Sub-category details with associated texts
        
    Raises:
        HTTPException: 404 if sub-category not found or doesn't belong to the category
    """
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).first()
    
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    return sub_category

@router.get("/category/{category_id}/sub-category/{sub_category_id}/texts", response_model=List[KarchagTextResponse], tags=["Texts"])
async def get_texts(category_id: int, sub_category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all texts for a specific sub-category.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        
    Returns:
        List of texts belonging to the specified sub-category
        
    Raises:
        HTTPException: 404 if sub-category not found
    """
    # Verify sub-category exists and belongs to the category
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True
    ).first()
    
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    texts = db.query(KarchagText).filter(
        KarchagText.sub_category_id == sub_category_id,
        KarchagText.is_active == True
    ).order_by(KarchagText.order_index).all()
    
    return texts

@router.get("/category/{category_id}/sub-category/{sub_category_id}/text/{text_id}", 
           response_model=KarchagTextResponse, tags=["Texts"])
async def get_text(category_id: int, sub_category_id: int, text_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific text with all its details including summary, yeshe_de_spans, and volumes.
     
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        text_id: The ID of the text to retrieve
         
    Returns:
        Complete text details including summary, yeshe_de_spans with volumes, and related information
         
    Raises:
        HTTPException: 404 if text not found or doesn't belong to the hierarchy
    """
    # Verify the text exists and belongs to the correct hierarchy with eager loading
    text = db.query(KarchagText).options(
        joinedload(KarchagText.text_summary),
        joinedload(KarchagText.sermon),
        joinedload(KarchagText.yana),
        joinedload(KarchagText.translation_type),
        joinedload(KarchagText.yeshe_de_spans).joinedload(YesheDESpan.volumes)
    ).join(SubCategory).filter(
        KarchagText.id == text_id,
        KarchagText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id,
        KarchagText.is_active == True
    ).first()
         
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
         
    return text

# POST Endpoints (Updates)

# Create main category
@router.post("/category", response_model=MainCategoryResponse, status_code=201)
async def create_category(
    category_data: MainCategoryCreate, 
    db: Session = Depends(get_db)
):
    db_category = MainCategory(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Create sub-category under a category
@router.post("/category/{category_id}/sub-category", response_model=SubCategoryResponse, status_code=201)
async def create_sub_category(
    category_id: int,
    sub_category_data: SubCategoryCreate,
    db: Session = Depends(get_db)
):
    # Verify parent category exists
    if not db.query(MainCategory).filter(MainCategory.id == category_id).first():
        raise HTTPException(status_code=404, detail="Parent category not found")
    
    db_sub_category = SubCategory(**sub_category_data.dict(), main_category_id=category_id)
    db.add(db_sub_category)
    db.commit()
    db.refresh(db_sub_category)
    return db_sub_category


@router.post("/category/{category_id}/sub-category/{sub_category_id}/text",response_model=KarchagTextResponse, tags=["Texts"])
async def create_text_with_relations(
    category_id: int,
    sub_category_id: int,
    text_data: KarchagTextCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new text with optional text_summary, yeshe_de_spans, and volumes in a single request.
    
    Example payload:
    {
        "english_title": "Sample Text",
        "tibetan_title": "Tibetan Title",
        "sub_category_id": 1,
        "text_summary": {
            "purpose_english": "This is the purpose",
            "text_summary_english": "This is the summary"
        },
        "yeshe_de_spans": [
            {
                "volumes": [
                    {
                        "volume_number": "Vol 1",
                        "start_page": "1",
                        "end_page": "50",
                        "order_index": 1
                    },
                    {
                        "volume_number": "Vol 2", 
                        "start_page": "51",
                        "end_page": "100",
                        "order_index": 2
                    }
                ]
            }
        ]
    }
    """
    
    # Verify sub_category belongs to category
    sub_cat = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not sub_cat:
        raise HTTPException(
            status_code=404, 
            detail=f"Sub-category {sub_category_id} not found in category {category_id}"
        )
    
    try:
        # Create the main text
        text_dict = text_data.model_dump(exclude={'text_summary', 'yeshe_de_spans'})
        text_dict['sub_category_id'] = sub_category_id
        
        db_text = KarchagText(**text_dict)
        db.add(db_text)
        db.flush()  # Get the ID without committing
        
        # Create text summary if provided
        if text_data.text_summary:
            summary_dict = text_data.text_summary.model_dump()
            summary_dict['text_id'] = db_text.id
            db_summary = TextSummary(**summary_dict)
            db.add(db_summary)
        
        # Create yeshe_de_spans with volumes if provided
        for span_data in text_data.yeshe_de_spans:
            # Create YesheDESpan
            db_span = YesheDESpan(text_id=db_text.id)
            db.add(db_span)
            db.flush()  # Get the span ID
            
            # Create volumes for this span
            for volume_data in span_data.volumes:
                volume_dict = volume_data.model_dump()
                volume_dict['yeshe_de_span_id'] = db_span.id
                db_volume = Volume(**volume_dict)
                db.add(db_volume)
        
        db.commit()
        
        # Return the created text with all relationships
        return await get_text(category_id, sub_category_id, db_text.id, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating text: {str(e)}")