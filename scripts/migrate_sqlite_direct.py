import sqlite3
import os

DB_PATH = r"e:\SAHAJ\instance\sahaj.db"

def migrate_sqlite():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # helper to check if col exists
    def column_exists(table, col):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [info[1] for info in cursor.fetchall()]
        return col in cols

    try:
        # Add category
        if not column_exists('documents', 'category'):
            print("Adding category...")
            cursor.execute("ALTER TABLE documents ADD COLUMN category TEXT")
        else:
            print("category exists.")

        # Add expiry_date
        if not column_exists('documents', 'expiry_date'):
            print("Adding expiry_date...")
            cursor.execute("ALTER TABLE documents ADD COLUMN expiry_date DATETIME")
        else:
            print("expiry_date exists.")
            
        # Add is_verified
        if not column_exists('documents', 'is_verified'):
            print("Adding is_verified...")
            cursor.execute("ALTER TABLE documents ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        else:
            print("is_verified exists.")
            
        # Add original_size
        if not column_exists('documents', 'original_size'):
            print("Adding original_size...")
            cursor.execute("ALTER TABLE documents ADD COLUMN original_size INTEGER")
        else:
            print("original_size exists.")

        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_sqlite()
