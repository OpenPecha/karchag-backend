from sqlalchemy.orm import Session
from sqlalchemy import func
from models import MainCategory, SubCategory, KagyurText, KagyurAudio
from schemas import MainCategoryResponse
from typing import Optional, List

async def handle_get_audio_categories(lang: Optional[str], db: Session) -> dict:
    categories = db.query(MainCategory).join(SubCategory).join(KagyurText).join(KagyurAudio).filter(
        MainCategory.is_active == True,
        SubCategory.is_active == True,
        KagyurText.is_active == True,
        KagyurAudio.is_active == True
    ).distinct().order_by(MainCategory.order_index).all()
    result = []
    for category in categories:
        audio_count = db.query(func.count(KagyurAudio.id)).join(KagyurText).join(SubCategory).filter(
            SubCategory.main_category_id == category.id,
            KagyurAudio.is_active == True
        ).scalar()
        category_dict = MainCategoryResponse.from_orm(category).dict()
        category_dict['audio_count'] = audio_count
        result.append(category_dict)
    return {"categories": result} 