"""
Initialize database and create tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db

def init_database():
    """Initialize the database"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (for fresh start - comment out in production)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")
        print("Tables created: users, schemes, user_schemes")

if __name__ == '__main__':
    init_database()
