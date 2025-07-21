from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base

class MainCategory(Base):
    __tablename__ = "main_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    description_english = Column(Text)
    description_tibetan = Column(Text)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    sub_categories = relationship("SubCategory", back_populates="main_category")

class SubCategory(Base):
    __tablename__ = "sub_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    main_category_id = Column(Integer, ForeignKey("main_categories.id"))
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    description_english = Column(Text)
    description_tibetan = Column(Text)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    main_category = relationship("MainCategory", back_populates="sub_categories")
    texts = relationship("KagyurText", back_populates="sub_category")

class Sermon(Base):
    __tablename__ = "sermons"
    
    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Yana(Base):
    __tablename__ = "yanas"
    
    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TranslationType(Base):
    __tablename__ = "translation_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class KagyurText(Base):
    __tablename__ = "kagyur_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"))
    derge_id = Column(String)
    yeshe_de_id = Column(String)
    tibetan_title = Column(String)
    chinese_title = Column(String)
    sanskrit_title = Column(String)
    english_title = Column(String)
    sermon_id = Column(Integer, ForeignKey("sermons.id"), nullable=True) 
    yana_id = Column(Integer, ForeignKey("yanas.id"), nullable=True)
    translation_type_id = Column(Integer, ForeignKey("translation_types.id"), nullable=True)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    sub_category = relationship("SubCategory", back_populates="texts")
    text_summary = relationship("TextSummary", back_populates="text", uselist=False)
    sermon = relationship("Sermon")
    yana = relationship("Yana")
    translation_type = relationship("TranslationType")
    yeshe_de_spans = relationship("YesheDESpan", back_populates="text", cascade="all, delete-orphan", lazy="select")
    audio_files = relationship("KagyurAudio", back_populates="text", cascade="all, delete-orphan", lazy="select")

class TextSummary(Base):
    __tablename__ = "text_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, ForeignKey("kagyur_texts.id"))
    translator_homage_english = Column(Text)
    translator_homage_tibetan = Column(Text)
    purpose_english = Column(Text)
    purpose_tibetan = Column(Text)
    text_summary_english = Column(Text)
    text_summary_tibetan = Column(Text)
    keyword_and_meaning_english = Column(Text)
    keyword_and_meaning_tibetan = Column(Text)
    relation_english = Column(Text)
    relation_tibetan = Column(Text)
    question_and_answer_english = Column(Text)
    question_and_answer_tibetan = Column(Text)
    translator_notes_english = Column(Text)
    translator_notes_tibetan = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    text = relationship("KagyurText", back_populates="text_summary")

class YesheDESpan(Base):
    __tablename__ = "yeshe_de_spans"
    
    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, ForeignKey("kagyur_texts.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    volumes = relationship("Volume", back_populates="yeshe_de_span", lazy="select")
    text = relationship("KagyurText", back_populates="yeshe_de_spans") 

class Volume(Base):
    __tablename__ = "volumes"
    
    id = Column(Integer, primary_key=True, index=True)
    yeshe_de_span_id = Column(Integer, ForeignKey("yeshe_de_spans.id"))
    volume_number = Column(String)
    start_page = Column(String)
    end_page = Column(String)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    yeshe_de_span = relationship("YesheDESpan", back_populates="volumes")

class KagyurAudio(Base):
    __tablename__ = "kagyur_audio"
    
    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, ForeignKey("kagyur_texts.id"))
    audio_url = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    duration = Column(Integer)
    narrator_name_english = Column(String)
    narrator_name_tibetan = Column(String)
    audio_quality = Column(String)
    audio_language = Column(String)
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    text = relationship("KagyurText", back_populates="audio_files")

class PublicationStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"

class KagyurNews(Base):
    __tablename__ = "kagyur_news"
    
    id = Column(Integer, primary_key=True, index=True)
    tibetan_title = Column(String)
    english_title = Column(String)
    tibetan_content = Column(Text)
    english_content = Column(Text)
    publication_status = Column(String)
    published_date = Column(DateTime(timezone=True), nullable=True)  # Set when published
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class KagyurVideo(Base):
    __tablename__ = "kangyur_video"
    
    id = Column(Integer, primary_key=True, index=True)
    tibetan_title = Column(String)
    english_title = Column(String)
    tibetan_description = Column(Text)
    english_description = Column(Text)
    video_url = Column(String)
    published_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    old_values = Column(Text)
    new_values = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String)

class Edition(Base):
    __tablename__ = "editions"
    
    id = Column(Integer, primary_key=True, index=True)
    name_english = Column(String, nullable=False)
    name_tibetan = Column(String)
    description_english = Column(Text)
    description_tibetan = Column(Text)
    abbreviation = Column(String)
    publisher = Column(String)
    publication_year = Column(Integer)
    location = Column(String)
    total_volumes = Column(Integer)
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())