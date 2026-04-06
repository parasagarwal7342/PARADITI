from datetime import datetime, timezone
from backend.database import db
from sqlalchemy import text # Import text for raw SQL

def utc_now():
    return datetime.now(timezone.utc)

def migrate_documents_v2():
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        print("Starting Document Model Migration V2...")
        
        try:
            with db.engine.connect() as conn:
                # Add expiry_date
                try:
                    conn.execute(text("SELECT expiry_date FROM documents LIMIT 1"))
                    print("Column 'expiry_date' already exists.")
                except Exception:
                    print("Adding column 'expiry_date'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN expiry_date DATETIME"))

                # Add category
                try:
                    conn.execute(text("SELECT category FROM documents LIMIT 1"))
                    print("Column 'category' already exists.")
                except Exception:
                    print("Adding column 'category'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN category VARCHAR(50)"))
                
                # Add is_verified
                try:
                    conn.execute(text("SELECT is_verified FROM documents LIMIT 1"))
                    print("Column 'is_verified' already exists.")
                except Exception:
                    print("Adding column 'is_verified'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN is_verified BOOLEAN DEFAULT 0"))

                # Add compression_ratio (to show "245 KB -> 95 KB")
                try:
                    conn.execute(text("SELECT original_size FROM documents LIMIT 1"))
                    print("Column 'original_size' already exists.")
                except Exception:
                    print("Adding column 'original_size'...")
                    conn.execute(text("ALTER TABLE documents ADD COLUMN original_size INTEGER"))

        except Exception as e:
            print(f"Migration error: {e}")
        
        print("Migration V2 finished.")

if __name__ == "__main__":
    migrate_documents_v2()
