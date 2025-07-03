from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from .base import TimestampMixin
from .reference import SermonResponse, YanaResponse, TranslationTypeResponse


class VolumeBase(BaseModel):
    volume_number: Optional[str] = None
    start_page: Optional[str] = None
    end_page: Optional[str] = None
    order_index: int = 0


class VolumeCreate(VolumeBase):
    """For creating volume within YesheDESpan (no yeshe_de_span_id needed)"""
    pass


class VolumeUpdate(VolumeBase):
    pass


class VolumeResponse(VolumeBase, TimestampMixin):
    id: int
    yeshe_de_span_id: int
    model_config = ConfigDict(from_attributes=True)


class YesheDESpanBase(BaseModel):
    pass


class YesheDESpanCreate(YesheDESpanBase):
    """For creating YesheDESpan within Text (no text_id needed)"""
    volumes: List[VolumeCreate] = Field(default_factory=list)


class YesheDESpanUpdate(YesheDESpanBase):
    volumes: Optional[List[VolumeCreate]] = None


class YesheDESpanResponse(BaseModel, TimestampMixin):
    id: int
    text_id: int
    volumes: List[VolumeResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TextSummaryBase(BaseModel):
    translator_homage_english: Optional[str] = None
    translator_homage_tibetan: Optional[str] = None
    purpose_english: Optional[str] = None
    purpose_tibetan: Optional[str] = None
    text_summary_english: Optional[str] = None
    text_summary_tibetan: Optional[str] = None
    keyword_and_meaning_english: Optional[str] = None
    keyword_and_meaning_tibetan: Optional[str] = None
    relation_english: Optional[str] = None
    relation_tibetan: Optional[str] = None
    question_and_answer_english: Optional[str] = None
    question_and_answer_tibetan: Optional[str] = None
    translator_notes_english: Optional[str] = None
    translator_notes_tibetan: Optional[str] = None


class TextSummaryCreate(TextSummaryBase):
    pass


class TextSummaryUpdate(TextSummaryBase):
    pass


class TextSummaryResponse(TextSummaryBase, TimestampMixin):
    id: int
    text_id: int
    model_config = ConfigDict(from_attributes=True)


class KagyurTextBase(BaseModel):
    derge_id: Optional[str] = None
    yeshe_de_id: Optional[str] = None
    tibetan_title: Optional[str] = None
    chinese_title: Optional[str] = None
    sanskrit_title: Optional[str] = None
    english_title: Optional[str] = None
    sermon_id: Optional[int] = None
    yana_id: Optional[int] = None
    translation_type_id: Optional[int] = None
    order_index: int = 0
    is_active: bool = True


class KagyurTextCreate(KagyurTextBase):
    sub_category_id: int
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: List[YesheDESpanCreate] = Field(default_factory=list)


class KagyurTextCreateRequest(KagyurTextBase):
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: Optional[List[YesheDESpanCreate]] = Field(default_factory=list)


class KagyurTextUpdate(KagyurTextBase):
    text_summary: Optional[TextSummaryCreate] = None
    yeshe_de_spans: Optional[List[YesheDESpanCreate]] = None


class KagyurTextResponse(KagyurTextBase, TimestampMixin):
    id: int
    sub_category_id: int
    text_summary: Optional[TextSummaryResponse] = None
    sermon: Optional[SermonResponse] = None
    yana: Optional[YanaResponse] = None
    yeshe_de_spans: List[YesheDESpanResponse] = []
    translation_type: Optional[TranslationTypeResponse] = None
    model_config = ConfigDict(from_attributes=True)