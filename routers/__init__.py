from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from database import get_db
from models import MainCategory, SubCategory, KarchagText, TextSummary
from schemas import (
    MainCategoryResponse, MainCategoryWithSubCategories, MainCategoryUpdate,
    SubCategoryResponse, SubCategoryWithTexts, SubCategoryUpdate,
    KarchagTextResponse, KarchagTextUpdate,
    TextSummaryResponse, TextSummaryUpdate
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
'''
@router.post("/category/{category_id}", response_model=MainCategoryResponse, tags=["Categories"])
async def update_category(
    category_id: int, 
    category_update: MainCategoryUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update a main category.
    
    Args:
        category_id: The ID of the category to update
        category_update: The updated category data
        
    Returns:
        The updated category information
        
    Raises:
        HTTPException: 404 if category not found
    """
    category = db.query(MainCategory).filter(MainCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    for field, value in category_update.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    
    category.updated_at = func.now()
    db.commit()
    db.refresh(category)
    
    return category

@router.post("/category/{category_id}/sub-category/{sub_category_id}", response_model=SubCategoryResponse, tags=["Sub-Categories"])
async def update_sub_category(
    category_id: int,
    sub_category_id: int,
    sub_category_update: SubCategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a sub-category.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category to update
        sub_category_update: The updated sub-category data
        
    Returns:
        The updated sub-category information
        
    Raises:
        HTTPException: 404 if sub-category not found
    """
    sub_category = db.query(SubCategory).filter(
        SubCategory.id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub-category not found")
    
    # Update fields
    for field, value in sub_category_update.model_dump(exclude_unset=True).items():
        setattr(sub_category, field, value)
    
    sub_category.updated_at = func.now()
    db.commit()
    db.refresh(sub_category)
    
    return sub_category

@router.post("/category/{category_id}/sub-category/{sub_category_id}/text/{text_id}", response_model=KarchagTextResponse, tags=["Texts"])
async def update_text(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    text_update: KarchagTextUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a text.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        text_id: The ID of the text to update
        text_update: The updated text data
        
    Returns:
        The updated text information
        
    Raises:
        HTTPException: 404 if text not found
    """
    # Verify the text exists and belongs to the correct hierarchy
    text = db.query(KarchagText).join(SubCategory).filter(
        KarchagText.id == text_id,
        KarchagText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Update fields
    for field, value in text_update.model_dump(exclude_unset=True).items():
        setattr(text, field, value)
    
    text.updated_at = func.now()
    db.commit()
    db.refresh(text)
    
    return text

@router.post("/category/{category_id}/sub-category/{sub_category_id}/text/{text_id}/summary", response_model=TextSummaryResponse, tags=["Text Summaries"])
async def update_text_summary(
    category_id: int,
    sub_category_id: int,
    text_id: int,
    summary_update: TextSummaryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update or create a text summary.
    
    Args:
        category_id: The ID of the main category
        sub_category_id: The ID of the sub-category
        text_id: The ID of the text
        summary_update: The updated summary data
        
    Returns:
        The updated or created text summary
        
    Raises:
        HTTPException: 404 if text not found
    """
    # Verify the text exists and belongs to the correct hierarchy
    text = db.query(KarchagText).join(SubCategory).filter(
        KarchagText.id == text_id,
        KarchagText.sub_category_id == sub_category_id,
        SubCategory.main_category_id == category_id
    ).first()
    
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    
    # Check if summary exists
    summary = db.query(TextSummary).filter(TextSummary.text_id == text_id).first()
    
    if summary:
        # Update existing summary
        for field, value in summary_update.model_dump(exclude_unset=True).items():
            setattr(summary, field, value)
        summary.updated_at = func.now()
    else:
        # Create new summary
        summary_data = summary_update.model_dump(exclude_unset=True)
        summary = TextSummary(text_id=text_id, **summary_data)
        db.add(summary)
    
    db.commit()
    db.refresh(summary)
    
    return summary'''