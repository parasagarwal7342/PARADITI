"""
Enhance seed data with Patent Claim features (Dependencies)
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models import Scheme

def enhance_data():
    app = create_app()
    with app.app_context():
        # 1. Create a Dependency Chain: PM-KISAN -> PM-KMY (Pension)
        # Logic: You must be a verified farmer (PM-KISAN beneficiary) to get the pension.
        
        pm_kisan = Scheme.query.filter(Scheme.name.like('%PM-KISAN%')).first()
        pm_kmy = Scheme.query.filter(Scheme.name.like('%PM-KMY%')).first()
        
        if pm_kisan and pm_kmy:
            print(f"Linking {pm_kmy.name} requires {pm_kisan.name}...")
            # Set prerequisite
            # PM-KMY requires [PM-KISAN ID]
            pm_kmy.prerequisites = json.dumps([pm_kisan.id])
            db.session.commit()
            print("Dependency chain created! (Patent Claim #2 unlocked)")
        else:
            print("Could not find PM-KISAN or PM-KMY schemes to link.")

        # 2. Add another: Stand Up India -> PMMY (Mudra)
        # Logic: Mudra (small loan) -> Stand Up (big loan)
        mudra = Scheme.query.filter(Scheme.name.like('%Mudra%')).first()
        standup = Scheme.query.filter(Scheme.name.like('%Stand Up%')).first()
        
        if mudra and standup:
            print(f"Linking {standup.name} requires {mudra.name}...")
            standup.prerequisites = json.dumps([mudra.id])
            db.session.commit()
            print("Dependency chain created!")

if __name__ == '__main__':
    enhance_data()
