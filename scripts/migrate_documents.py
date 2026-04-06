
import sys
import os
import sqlalchemy
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting migration...")
        
        # 1. Update Document Table
        try:
            with db.engine.connect() as conn:
                # SQLite doesn't support IF NOT EXISTS in ALTER TABLE usually, so we check first
                # Check file_size
                try:
                    conn.execute(text("SELECT file_size FROM documents LIMIT 1"))
                    print("Column 'file_size' already exists.")
                except Exception:
                    print("Adding column 'file_size'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN file_size INTEGER"))
                
                # Check mime_type
                try:
                    conn.execute(text("SELECT mime_type FROM documents LIMIT 1"))
                    print("Column 'mime_type' already exists.")
                except Exception:
                    print("Adding column 'mime_type'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN mime_type VARCHAR(100)"))
                
                # Commit basic alters if not autocommit
                if not conn.in_transaction():
                    # SQLAlchemy 1.4+ usually requires explicit commit for DDL in some configurations
                    # But SQLite usually autocommits DDL. 
                    pass
        except Exception as e:
            print(f"Migration warning (ignorable if columns exist): {e}")

        # 2. Add Application Table (db.create_all handles only new tables)
        db.create_all()
        print("Ensured all tables exist (Application).")
        
        print("Migration finished successfully.")

if __name__ == "__main__":
    migrate()
