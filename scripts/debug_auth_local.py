
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import db, User
from backend.security import hash_password, verify_password

def test_auth_flow():
    app = create_app()
    with app.app_context():
        email = "debug_user@example.com"
        password = "debug_password_123"
        
        print(f"Testing auth flow for: {email}")
        
        # Cleanup
        existing = User.query.filter_by(email=email).first()
        if existing:
            print("Removing existing debug user...")
            db.session.delete(existing)
            db.session.commit()
            
        # 1. Hash Password
        print("1. Hashing password...")
        hashed_pw = hash_password(password)
        print(f"   Hash: {hashed_pw[:20]}...")
        
        # 2. Verify immediately (in memory)
        print("2. Verifying hash in memory...")
        is_valid = verify_password(hashed_pw, password)
        print(f"   Result: {is_valid}")
        if not is_valid:
            print("   FATAL: In-memory verification failed!")
            return
            
        # 3. Store in DB
        print("3. Storing in DB...")
        user = User(
            name="Debug User",
            email=email,
            password_hash=hashed_pw,
            age=25,
            gender="Male",
            state="Delhi",
            income=50000.0,
            category="General"
        )
        db.session.add(user)
        db.session.commit()
        print(f"   User stored with ID: {user.id}")
        
        # 4. Fetch from DB
        print("4. Fetching from DB...")
        fetched_user = User.query.filter_by(email=email).first()
        print(f"   Fetched Hash: {fetched_user.password_hash[:20]}...")
        
        # 5. Verify from DB
        print("5. Verifying from DB...")
        is_valid_db = verify_password(fetched_user.password_hash, password)
        print(f"   Result: {is_valid_db}")
        
        if is_valid_db:
            print("✅ Auth flow passed successfully!")
        else:
            print("❌ Auth flow FAILED at DB verification step!")

if __name__ == "__main__":
    test_auth_flow()
