from backend.app import create_app
from backend.models import Scheme
from backend.services.api_setu import sync_schemes_to_db

app = create_app('development')
with app.app_context():
    print("Testing Sync...")
    added, updated = sync_schemes_to_db()
    print(f"Added: {added}, Updated: {updated}")
    
    api_setu_schemes = Scheme.query.filter_by(source='api_setu').all()
    print(f"Total API Setu Schemes in DB: {len(api_setu_schemes)}")
    for s in api_setu_schemes[:3]:
        print(f"- {s.name}")
