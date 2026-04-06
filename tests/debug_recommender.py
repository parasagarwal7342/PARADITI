
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import User, Scheme, db
from backend.ml_engine import get_ml_engine

def debug_recommendations():
    app = create_app('development')
    with app.app_context():
        # Create a test user
        user = User(
            name="Test User",
            age=30,
            gender="Male",
            state="Maharashtra",
            income=15000,
            category="General",
            occupation="Farmer"
        )
        # We don't save the user to DB, just use the object
        
        print(f"\n--- Debugging Recommendations for User ---")
        print(f"Profile: Age={user.age}, State={user.state}, Income={user.income}, Cat={user.category}, Occ={user.occupation}")
        
        ml_engine = get_ml_engine()
        all_schemes = Scheme.query.all()
        print(f"Total Schemes in DB: {len(all_schemes)}")
        
        # 1. Check Filtering
        filtered = ml_engine._filter_schemes_by_criteria(user, all_schemes)
        print(f"Schemes after Hard Filtering: {len(filtered)}")
        
        # Print dropped schemes
        filtered_ids = {s.id for s in filtered}
        for s in all_schemes:
            if s.id not in filtered_ids:
                print(f"  [DROPPED] {s.name} (State: {s.state}, Income: {s.min_income}-{s.max_income}, Cat: {s.category_specific})")

        # 2. Check Scoring
        print("\n--- Top 5 Recommendations ---")
        recommendations = ml_engine.recommend_schemes(user, limit=5)
        for s, score in recommendations:
            print(f"  [SCORE: {score:.4f}] {s.name} ({s.ministry})")
            # print(f"    Desc: {s.description[:50]}...")

if __name__ == "__main__":
    debug_recommendations()
