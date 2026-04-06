
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import User
from backend.security import verify_password

def inspect(email):
    app = create_app()
    print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User found: {user.email}")
            print(f"Hash: {user.password_hash}")
            print(f"Verifying 'password123' against hash...")
            is_valid = verify_password(user.password_hash, "password123")
            print(f"Match: {is_valid}")
        else:
            print("User not found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect(sys.argv[1])
    else:
        print("Please provide email.")
