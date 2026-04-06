
import sqlite3
import os

def migrate():
    print("Migrating database to v5.0 Schema...")
    db_path = os.path.join('instance', 'sahaj.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Skipping migration (will be created on first run).")
        # Try finding it in just 'sahaj.db' if run from backend dir? No, app runs from root.
        # Let's inspect what IS there if it fails.
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if agent_id column exists in users
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [info[1] for info in cursor.fetchall()]
    
    if 'agent_id' not in user_columns:
        print("Adding 'agent_id' column to 'users' table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN agent_id TEXT DEFAULT NULL")
            print("Column added successfully.")
        except Exception as e:
            print(f"Error adding column: {e}")
            
    # Check schemes table columns
    cursor.execute("PRAGMA table_info(schemes)")
    scheme_columns = [info[1] for info in cursor.fetchall()]
    
    new_cols = {
        'link_health_score': 'INTEGER DEFAULT 100',
        'graduation_path': 'TEXT DEFAULT NULL',
        'projected_salary_increase': 'REAL DEFAULT 0.0',
        'skill_tags': 'TEXT DEFAULT NULL'
    }
    
    for col, definition in new_cols.items():
        if col not in scheme_columns:
            print(f"Adding '{col}' column to 'schemes' table...")
            try:
                cursor.execute(f"ALTER TABLE schemes ADD COLUMN {col} {definition}")
                print(f"Column '{col}' added.")
            except Exception as e:
                print(f"Error adding {col}: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
