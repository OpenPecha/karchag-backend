#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.database import SessionLocal
from app.models import KagyurNews, PublicationStatus
from sqlalchemy import text

def test_enum_detailed():
    db = SessionLocal()
    try:
        print(f"PublicationStatus enum members:")
        for status in PublicationStatus:
            print(f"  {status.name} = '{status.value}'")
        
        # Test direct value query
        print(f"\nTesting with direct value 'published'...")
        try:
            count = db.execute(text("SELECT COUNT(*) FROM kagyur_news WHERE publication_status = 'published'")).scalar()
            print(f"Count with direct SQL: {count}")
        except Exception as e:
            print(f"Error with direct SQL: {e}")
        
        # Test with lowercase string
        print(f"\nTesting with SQLAlchemy and lowercase string 'published'...")
        try:
            count = db.query(KagyurNews).filter(
                KagyurNews.publication_status == 'published'
            ).count()
            print(f"Count with lowercase string: {count}")
        except Exception as e:
            print(f"Error with lowercase string: {e}")
            
        # Test with enum value
        print(f"\nTesting with enum value...")
        try:
            count = db.query(KagyurNews).filter(
                KagyurNews.publication_status == PublicationStatus.PUBLISHED.value
            ).count()
            print(f"Count with enum.value: {count}")
        except Exception as e:
            print(f"Error with enum.value: {e}")
            
        # Test with enum directly
        print(f"\nTesting with enum directly...")
        try:
            count = db.query(KagyurNews).filter(
                KagyurNews.publication_status == PublicationStatus.PUBLISHED
            ).count()
            print(f"Count with enum: {count}")
        except Exception as e:
            print(f"Error with enum: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_enum_detailed()
