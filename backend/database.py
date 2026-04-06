import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from backend.models import User, Scheme, UserScheme, Document, Application
        
        # Create all tables
        db.create_all()
        
        # AUTO-SEEDING FOR PRODUCTION (Live Preview)
        # If we are using an in-memory database in production, we must seed it immediately
        is_production = (os.getenv('FLASK_ENV') == 'production')
        is_in_memory = (app.config.get('SQLALCHEMY_DATABASE_URI') == 'sqlite://')
        
        if is_production and is_in_memory:
            from scripts.seed_data import seed_db
            try:
                seed_db(app)
                print("Production Auto-Seed: Database populated successfully.")
            except Exception as e:
                print(f"Production Auto-Seed Error: {str(e)}")
        
        try:
            print("Database initialized successfully!")
        except (ValueError, OSError):
            pass  # stdout may be closed in background process
    
    return db
