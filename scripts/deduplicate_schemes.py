
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models import Scheme
from sqlalchemy import func

def deduplicate_schemes():
    app = create_app('development')
    with app.app_context():
        print("Checking for duplicate schemes...")
        
        # Find duplicates by name
        duplicates = db.session.query(Scheme.name, func.count(Scheme.id))\
            .group_by(Scheme.name)\
            .having(func.count(Scheme.id) > 1)\
            .all()
            
        if not duplicates:
            print("No duplicates found.")
            return

        print(f"Found {len(duplicates)} schemes with duplicates.")
        
        total_removed = 0
        
        for name, count in duplicates:
            print(f"Processing '{name}' (count: {count})...")
            # Get all schemes with this name
            schemes = Scheme.query.filter_by(name=name).order_by(Scheme.id).all()
            
            # Keep the first one, delete the rest
            # (assuming the first one is the 'original' or they are identical)
            keep = schemes[0]
            remove = schemes[1:]
            
            for s in remove:
                db.session.delete(s)
                total_removed += 1
                
        db.session.commit()
        print(f"Successfully removed {total_removed} duplicate schemes.")

if __name__ == "__main__":
    deduplicate_schemes()
