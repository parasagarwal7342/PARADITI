"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from backend.models import User, Scheme, UserScheme, Document, Application
        from backend.services.seeder import seed_production_data
        
        # Create all tables
        db.create_all()
        
        # Auto-seed in production/ephemeral environments
        try:
            db_uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
            if 'sqlite://' in db_uri:
                 seed_production_data()
            print("Database initialized and auto-seeded successfully!")
        except Exception as e:
            print(f"Auto-seed warning: {str(e)}")
    
    return db
