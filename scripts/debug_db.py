
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models import Scheme
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    print(f"Tables: {inspector.get_table_names()}")
    try:
        count = Scheme.query.count()
        print(f"Schemes count: {count}")
    except Exception as e:
        print(f"Error querying schemes: {e}")
