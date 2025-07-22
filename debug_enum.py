#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.database import SessionLocal
from app.models import KagyurNews, PublicationStatus

def test_enum():
    db = SessionLocal()
    try:
        print(f"PublicationStatus.PUBLISHED = {PublicationStatus.PUBLISHED}")
        print(f"PublicationStatus.PUBLISHED value = {PublicationStatus.PUBLISHED.value}")
        
        # Try a simple query without the enum filter first
        print("\nTesting simple query...")
        news_count = db.query(KagyurNews).count()
        print(f"Total news count: {news_count}")
        
        # Try with is_active filter
        print("\nTesting with is_active filter...")
        active_count = db.query(KagyurNews).filter(KagyurNews.is_active == True).count()
        print(f"Active news count: {active_count}")
        
        # Try with publication status using string directly
        print("\nTesting with string publication status...")
        published_string_count = db.query(KagyurNews).filter(
            KagyurNews.is_active == True,
            KagyurNews.publication_status == 'published'
        ).count()
        print(f"Published news (string filter) count: {published_string_count}")
        
        # Try with enum
        print("\nTesting with enum publication status...")
        try:
            published_enum_count = db.query(KagyurNews).filter(
                KagyurNews.is_active == True,
                KagyurNews.publication_status == PublicationStatus.PUBLISHED
            ).count()
            print(f"Published news (enum filter) count: {published_enum_count}")
        except Exception as e:
            print(f"Error with enum filter: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_enum()
