from backend.app import create_app
from backend.models import Scheme, db

app = create_app()

with app.app_context():
    # Find schemes with income limits
    print("--- Schemes with Max Income ---")
    schemes = Scheme.query.filter(Scheme.max_income.isnot(None)).limit(5).all()
    for s in schemes:
        print(f"ID: {s.id}, Name: {s.name}, Max Income: {s.max_income}")

    # Find schemes with age limits
    print("\n--- Schemes with Age Limits ---")
    schemes = Scheme.query.filter(Scheme.min_age.isnot(None) | Scheme.max_age.isnot(None)).limit(5).all()
    for s in schemes:
        print(f"ID: {s.id}, Name: {s.name}, Min Age: {s.min_age}, Max Age: {s.max_age}")
