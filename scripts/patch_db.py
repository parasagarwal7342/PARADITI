
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'sahaj.db')

def patch_database():
    print(f"Patching database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist in applications table
    cursor.execute("PRAGMA table_info(applications)")
    columns = [info[1] for info in cursor.fetchall()]
    
    new_columns = {
        'approval_confidence': 'FLOAT',
        'rejection_reasons': 'TEXT',
        'appeal_letter_draft': 'TEXT',
        'appeal_status': 'VARCHAR(20)',
        'validation_status': 'VARCHAR(20)',
        'missing_fields': 'TEXT'
    }
    
    for col, dtype in new_columns.items():
        if col not in columns:
            print(f"Adding missing column: {col}")
            try:
                cursor.execute(f"ALTER TABLE applications ADD COLUMN {col} {dtype}")
            except Exception as e:
                print(f"Error adding {col}: {e}")
        else:
            print(f"Column {col} already exists.")
            
    conn.commit()
    conn.close()
    print("Database patch completed.")

if __name__ == '__main__':
    patch_database()
