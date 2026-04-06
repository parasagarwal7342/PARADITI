
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import db, User

def cleanup_chat_users():
    app = create_app()
    with app.app_context():
        users = User.query.filter(User.email.like('chat_test_%')).all()
        count = len(users)
        if count > 0:
            print(f"Found {count} chat test users. Deleting...")
            for user in users:
                db.session.delete(user)
            db.session.commit()
            print("Cleanup complete.")
        else:
            print("No chat test users found.")

if __name__ == "__main__":
    cleanup_chat_users()
