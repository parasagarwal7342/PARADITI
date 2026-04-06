"""
P Λ R Λ D I T I (परादिति) - Database User Cleanup Script
(C) 2026 Founder: PARAS AGRAWAL

WARNING: This script will DELETE ALL user profiles from the database.
Use only for development/testing purposes.
"""

import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import User, Application, Document, db

app = create_app()

def delete_all_users():
    """
    Deletes all user profiles and their associated data from the database.
    """
    with app.app_context():
        try:
            # Count existing records
            user_count = User.query.count()
            app_count = Application.query.count()
            doc_count = Document.query.count()
            
            print(f"\n{'='*60}")
            print(f"P Λ R Λ D I T I - Database Cleanup Utility")
            print(f"{'='*60}")
            print(f"\nCurrent Database Status:")
            print(f"  • Users: {user_count}")
            print(f"  • Applications: {app_count}")
            print(f"  • Documents: {doc_count}")
            print(f"\n{'='*60}")
            
            if user_count == 0:
                print("\n✅ Database is already clean. No users to delete.")
                return
            
            # Delete all records (cascading will handle related data)
            print("\n🔄 Deleting all user data...")
            
            # Delete applications first
            deleted_apps = Application.query.delete()
            print(f"   ✓ Deleted {deleted_apps} applications")
            
            # Delete documents
            deleted_docs = Document.query.delete()
            print(f"   ✓ Deleted {deleted_docs} documents")
            
            # Delete users
            deleted_users = User.query.delete()
            print(f"   ✓ Deleted {deleted_users} users")
            
            # Commit changes
            db.session.commit()
            
            print(f"\n{'='*60}")
            print("✅ Database cleanup completed successfully!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during deletion: {str(e)}")
            print("Database has been rolled back to previous state.\n")
            raise

if __name__ == "__main__":
    delete_all_users()
