import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.database import db
from backend.models import Scheme
from backend.services.api_setu import fetch_schemes_from_api_setu, API_SETU_DIRECTORY_BASE

def force_sync():
    print("Initializing Flask App...")
    app = create_app('development')
    with app.app_context():
        print("Fetching schemes from API Setu (Simulated)...")
        # Pass the required base_url
        schemes_data = fetch_schemes_from_api_setu(base_url=API_SETU_DIRECTORY_BASE)
        
        print(f"Fetched {len(schemes_data)} schemes.")
        
        added = 0
        updated = 0
        
        for s_data in schemes_data:
            existing = Scheme.query.filter_by(external_id=s_data['external_id']).first()
            if existing:
                # Update logic
                existing.name = s_data['name']
                existing.description = s_data['description']
                existing.category = s_data['category']
                existing.state = s_data['state']
                existing.eligibility_criteria = s_data['eligibility_criteria']
                existing.benefits = s_data['benefits']
                existing.documents_required = s_data['documents_required']
                existing.min_income = s_data.get('min_income')
                existing.max_income = s_data.get('max_income')
                existing.gender_specific = s_data.get('gender_specific')
                existing.category_specific = s_data.get('category_specific')
                updated += 1
            else:
                new_scheme = Scheme(**s_data)
                db.session.add(new_scheme)
                added += 1
        
        db.session.commit()
        print(f"Sync Complete: Added {added}, Updated {updated}")

if __name__ == '__main__':
    force_sync()
