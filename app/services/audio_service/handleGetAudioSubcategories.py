from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import SubCategory, KagyurText, KagyurAudio
from app.schemas import SubCategoryResponse
from typing import Optional, List

async def handle_get_audio_subcategories(category_id: int, lang: Optional[str], db: Session) -> dict:
    subcategories = db.query(SubCategory).join(KagyurText).join(KagyurAudio).filter(
        SubCategory.main_category_id == category_id,
        SubCategory.is_active == True,
        KagyurText.is_active == True,
        KagyurAudio.is_active == True
    ).distinct().order_by(SubCategory.order_index).all()
    result = []
    for subcategory in subcategories:
        audio_count = db.query(func.count(KagyurAudio.id)).join(KagyurText).filter(
            KagyurText.sub_category_id == subcategory.id,
            KagyurAudio.is_active == True
        ).scalar()
        subcategory_dict = SubCategoryResponse.from_orm(subcategory).dict()
        subcategory_dict['audio_count'] = audio_count
        result.append(subcategory_dict)
    return {"subcategories": result} 