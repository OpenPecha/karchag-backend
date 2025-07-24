#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.database import SessionLocal
from app.models import User

def make_user_admin(username: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_admin = True
            db.commit()
            print(f"User '{username}' is now an admin")
        else:
            print(f"User '{username}' not found")
    finally:
        db.close()

if __name__ == "__main__":
    make_user_admin("admin")
