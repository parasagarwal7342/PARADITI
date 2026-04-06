from datetime import datetime, timezone
from backend.app import create_app
from backend.models import Document, User

app = create_app()
with app.app_context():
    try:
        # 1. Get a user
        user = User.query.first()
        if not user:
            print("No users found.")
            exit()
            
        print(f"Testing for User: {user.email} (ID: {user.id})")
        
        # 2. Get Documents
        documents = Document.query.filter_by(user_id=user.id).all()
        print(f"Found {len(documents)} documents.")
        
        # 3. Test Logic
        expiring = 0
        now_naive = datetime.now()
        now_aware = datetime.now(timezone.utc)
        
        for d in documents:
            print(f"Doc {d.id}: expiry={d.expiry_date}, tz={d.expiry_date.tzinfo if d.expiry_date else 'None'}")
            
            if getattr(d, 'expiry_date', None):
                try:
                    d_date = d.expiry_date
                    if d_date.tzinfo:
                         if (d_date - now_aware).days < 30: expiring += 1
                    else:
                         if (d_date - now_naive).days < 30: expiring += 1
                except Exception as e:
                    print(f"  Error calculating expiry: {e}")

        # 4. Test to_dict
        for d in documents:
            try:
                print(d.to_dict())
            except Exception as e:
                print(f"  Error in to_dict: {e}")

        print("Debug script completed successfully.")
        
    except Exception as e:
        print(f"Global Error: {e}")
